# 💾 ОБНОВЛЕНИЕ ТЗ: RAW DATA STORAGE + BATCH ANALYZER

**Дата:** 10 декабря 2025, 20:00 MSK  
**Версия ТЗ:** 4.2 (Critical Data Storage Update)  
**Приоритет:** 🔴 КРИТИЧЕСКИЙ

---

## 🎯 ПРИНЦИП: СОХРАНЯТЬ ВСЁ → СТРУКТУРИРОВАТЬ ПОТОМ

**Критически важно:** Бот должен сохранять **АБСОЛЮТНО ВСЁ** в сыром виде (raw tables), а ночной batch-analyzer будет структурировать и раскладывать по таблицам.

**Архитектура:**
1. **BOT (Real-time)** → Сохраняет **ВСЁ** в raw tables
2. **BATCH ANALYZER (03:00 MSK)** → Структурирует и раскладывает
3. **Исправление ошибок** → Batch analyzer перемещает неправильно разложенные данные

---

## 📊 НОВЫЕ ТАБЛИЦЫ SUPABASE

### 1. raw_messages — Сырые сообщения

```sql
CREATE TABLE raw_messages (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL,
  message_id BIGINT NOT NULL,
  message_text TEXT,
  message_type TEXT NOT NULL,
  
  -- ЦЕПОЧКА ОТВЕТОВ (reply chain)
  reply_to_message_id BIGINT,
  reply_to_text TEXT,
  is_clarification BOOLEAN DEFAULT FALSE,
  
  -- Сырые данные
  raw_telegram_json JSONB,
  
  -- Статус обработки
  is_processed BOOLEAN DEFAULT FALSE,
  processed_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_raw_messages_user ON raw_messages(user_id);
CREATE INDEX idx_raw_messages_processed ON raw_messages(is_processed);
```

### 2. bot_responses — Ответы бота

```sql
CREATE TABLE bot_responses (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL,
  message_id BIGINT NOT NULL,
  response_text TEXT NOT NULL,
  response_type TEXT,
  related_user_message_id BIGINT,
  ai_analysis JSONB,
  chain_id UUID,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### 3. raw_files — Сырые файлы

```sql
CREATE TABLE raw_files (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL,
  message_id BIGINT NOT NULL,
  file_type TEXT NOT NULL,
  file_name TEXT,
  file_path TEXT NOT NULL,
  file_size BIGINT,
  file_hash TEXT UNIQUE,
  raw_metadata JSONB,
  is_processed BOOLEAN DEFAULT FALSE,
  processed_at TIMESTAMP,
  uploaded_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_raw_files_user ON raw_files(user_id);
CREATE INDEX idx_raw_files_hash ON raw_files(file_hash);
```

### 4. message_chains — Цепочки диалогов

```sql
CREATE TABLE message_chains (
  id BIGSERIAL PRIMARY KEY,
  chain_id UUID UNIQUE DEFAULT gen_random_uuid(),
  user_id BIGINT NOT NULL,
  original_message_id BIGINT NOT NULL,
  original_text TEXT,
  replies JSONB DEFAULT '[]'::jsonb,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_chains_user ON message_chains(user_id);
```

---

## 🔧 ОБНОВЛЕНИЕ bot_handler.py

**Добавить после строки 70 в `handle_universal_message`:**

```python
# ====== НОВОЕ: ОБРАБОТКА REPLY CHAIN ======
reply_to_text = None
reply_to_message_id = None
is_clarification = False

if message.reply_to_message:
    reply_to_text = message.reply_to_message.text or "[Медиа контент]"
    reply_to_message_id = message.reply_to_message.message_id
    is_clarification = True
    logger.info(f"📌 Обнаружен ответ на сообщение #{reply_to_message_id}")

# ====== СОХРАНЕНИЕ В СЫРУЮ ТАБЛИЦУ ======
from datetime import datetime
from supabase import create_client

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase = create_client(supabase_url, supabase_key)

raw_message_data = {
    "user_id": user_id,
    "message_id": message.message_id,
    "message_text": message_text,
    "message_type": message_type,
    "reply_to_message_id": reply_to_message_id,
    "reply_to_text": reply_to_text,
    "is_clarification": is_clarification,
    "raw_telegram_json": message.model_dump() if hasattr(message, 'model_dump') else {},
    "created_at": datetime.now().isoformat()
}

try:
    supabase.table("raw_messages").insert(raw_message_data).execute()
    logger.info("✅ Сообщение сохранено в raw_messages")
except Exception as e:
    logger.error(f"❌ Ошибка сохранения: {e}")

# ====== ОБНОВЛЕНИЕ ЦЕПОЧКИ ======
if is_clarification:
    try:
        chain = supabase.table("message_chains").select("*").eq("original_message_id", reply_to_message_id).execute()
        
        if not chain.data:
            chain_data = {
                "user_id": user_id,
                "original_message_id": reply_to_message_id,
                "original_text": reply_to_text,
                "replies": [{
                    "reply_message_id": message.message_id,
                    "reply_text": message_text,
                    "timestamp": datetime.now().isoformat()
                }]
            }
            supabase.table("message_chains").insert(chain_data).execute()
        else:
            chain_id = chain.data[0]["id"]
            replies = chain.data[0]["replies"] or []
            replies.append({
                "reply_message_id": message.message_id,
                "reply_text": message_text,
                "timestamp": datetime.now().isoformat()
            })
            supabase.table("message_chains").update({"replies": replies}).eq("id", chain_id).execute()
        
        logger.info("✅ Цепочка обновлена")
    except Exception as e:
        logger.error(f"❌ Ошибка цепочки: {e}")

# Добавить в analysis_data
analysis_data["reply_to_message"] = reply_to_text
analysis_data["is_clarification"] = is_clarification
```

---

## 🌙 BATCH ANALYZER - Ночная обработка

**Файл:** `batch_analyzer.py`

```python
"""🌙 Batch Analyzer - Ночная структуризация данных
Запуск: Каждую ночь в 03:00 MSK
"""
import asyncio
import os
import logging
from datetime import datetime
from supabase import create_client
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
N8N_WEBHOOK = os.getenv("N8N_WEBHOOK_BASE", "https://lavrentev.app.n8n.cloud/webhook")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

async def process_raw_messages():
    """Обработка сырых сообщений"""
    logger.info("📥 Загрузка raw_messages...")
    
    raw = supabase.table("raw_messages").select("*").eq("is_processed", False).execute()
    logger.info(f"📊 Найдено: {len(raw.data)} сообщений")
    
    for msg in raw.data:
        try:
            # Анализ через Perplexity AI
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(f"{N8N_WEBHOOK}/digital-twin-ask", json={
                    "message": msg["message_text"],
                    "message_type": msg["message_type"],
                    "user_id": msg["user_id"],
                    "reply_to_message": msg.get("reply_to_text"),
                    "is_clarification": msg.get("is_clarification", False)
                })
                analysis = response.json()
            
            # Раскладываем по таблицам
            if analysis.get("type") == "file":
                # Сохранить в files
                pass
            elif analysis.get("type") == "event":
                # Сохранить в events
                pass
            
            # Помечаем как обработанное
            supabase.table("raw_messages").update({
                "is_processed": True,
                "processed_at": datetime.now().isoformat()
            }).eq("id", msg["id"]).execute()
            
            logger.info(f"✅ Сообщение #{msg['id']} обработано")
        except Exception as e:
            logger.error(f"❌ Ошибка #{msg['id']}: {e}")

async def main():
    logger.info(f"🌙 Batch Analyzer запущен: {datetime.now()}")
    await process_raw_messages()
    logger.info("✅ Завершено")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## ☸️ K8S CRONJOB

**Файл:** `k8s/batch-analyzer-cronjob.yaml`

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: batch-analyzer
  namespace: super-brain
spec:
  schedule: "0 3 * * *"  # Каждую ночь в 03:00 MSK
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: batch-analyzer
            image: registry.digitalocean.com/digital-twin-registry/batch-analyzer:latest
            env:
            - name: SUPABASE_URL
              valueFrom:
                secretKeyRef:
                  name: supabase-credentials
                  key: url
            - name: SUPABASE_KEY
              valueFrom:
                secretKeyRef:
                  name: supabase-credentials
                  key: key
            - name: N8N_WEBHOOK_BASE
              value: "https://lavrentev.app.n8n.cloud/webhook"
          restartPolicy: OnFailure
```

---

## ✅ ЧЕКЛИСТ ВЫПОЛНЕНИЯ

- [ ] Создать таблицы в Supabase (SECURE_SCHEMA_V3.sql)
- [ ] Обновить bot_handler.py (обработка reply_to_message)
- [ ] Создать batch_analyzer.py
- [ ] Создать Dockerfile.batch-analyzer
- [ ] Создать batch-analyzer-cronjob.yaml
- [ ] Обновить SUPER_BRAIN_FLEXIBLE_TZ_v4.0.md
- [ ] Запустить GitHub Actions (Build and Push)
- [ ] Применить kubectl apply -f k8s/

---

**Дата обновления:** 10 декабря 2025, 20:00 MSK  
**Статус:** 🟡 ГОТОВО К ВЫПОЛНЕНИЮ  
**Автор:** Perplexity AI + vik9541
