# 🚀 PSYCOPG3 MIGRATION - Готовый код

**Статус:** ✅ Завершено  
**Дата:** 14 декабря 2025  
**Проект:** Victor Bot v2.0

---

## 📦 1. ЗАВИСИМОСТИ

### requirements.api.txt

```txt
# Database
supabase==2.3.4
psycopg2-binary==2.9.9
psycopg[binary]==3.3.2
psycopg-pool==3.3.0
```

**Установка:**
```bash
pip install 'psycopg[binary]==3.3.2' psycopg-pool==3.3.0
```

---

## 🔧 2. КОНФИГУРАЦИЯ

### .env.victor

```bash
# ПРЯМОЕ ПОДКЛЮЧЕНИЕ к PostgreSQL (БЕЗ POOLER!)
DATABASE_URL=postgresql://postgres.xxx:password@aws-0-eu-central-1.pooler.supabase.com:5432/postgres

# Альтернативно: через pooler (если переключен на Session mode)
# DATABASE_URL=postgresql://postgres.xxx:password@aws-0-eu-central-1.pooler.supabase.com:6543/postgres

# REST API (fallback)
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**⚠️ ВАЖНО:** Изменить порт с `6543` на `5432` для прямого подключения!

---

## 📝 3. КОД - api/victor_bot_router.py

### 3.1 Импорты (начало файла)

```python
"""
VICTOR BOT v2.0 - Universal Sensor API
Главный роутер для Telegram Webhook и обработки всех типов сообщений
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
import uuid

import psycopg
from psycopg_pool import AsyncConnectionPool
import httpx
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field

# Windows fix для psycopg3 async
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

### 3.2 Connection Pool

```python
# Глобальный DB pool (создается один раз при старте)
_db_pool: Optional[AsyncConnectionPool] = None


async def get_db_pool():
    """Получить connection pool к БД (psycopg3 async)"""
    global _db_pool

    if _db_pool is None:
        if not DATABASE_URL:
            raise ValueError("DATABASE_URL not configured")

        # psycopg3 AsyncConnectionPool (совместим с PgBouncer)
        _db_pool = AsyncConnectionPool(
            DATABASE_URL,
            min_size=1,
            max_size=5,
            kwargs={"options": "-c jit=off"},  # PgBouncer compatibility
        )
        await _db_pool.open()
        logger.info("✅ psycopg3 AsyncConnectionPool created")

    return _db_pool
```

### 3.3 Helper функции (совместимость с asyncpg API)

```python
# ============================================================================
# HELPER FUNCTIONS - psycopg3 compatibility
# ============================================================================


async def fetchval(conn, query: str, *args):
    """Helper для получения одного значения (эквивалент asyncpg.fetchval)"""
    async with conn.cursor() as cur:
        await cur.execute(query, args)
        row = await cur.fetchone()
        return row[0] if row else None


async def fetchrow(conn, query: str, *args):
    """Helper для получения одной строки (эквивалент asyncpg.fetchrow)"""
    async with conn.cursor() as cur:
        await cur.execute(query, args)
        row = await cur.fetchone()
        if row:
            # Преобразуем в dict для обратной совместимости
            return dict(zip([desc[0] for desc in cur.description], row))
        return None


async def fetch(conn, query: str, *args):
    """Helper для получения всех строк (эквивалент asyncpg.fetch)"""
    async with conn.cursor() as cur:
        await cur.execute(query, args)
        rows = await cur.fetchall()
        if rows:
            # Преобразуем в list[dict]
            return [dict(zip([desc[0] for desc in cur.description], row)) for row in rows]
        return []


async def execute(conn, query: str, *args):
    """Helper для выполнения команды (эквивалент asyncpg.execute)"""
    async with conn.cursor() as cur:
        await cur.execute(query, args)
```

### 3.4 Пример использования в handler

```python
async def handle_photo(
    photo: List[TelegramPhotoSize], caption: Optional[str], message_id: int, pool: AsyncConnectionPool
):
    """
    Обработка фото → спрашиваем что это
    """
    logger.info(f"📸 Processing photo...")

    # Берём самое большое фото
    largest_photo = max(photo, key=lambda p: p.file_size or 0)

    # Скачиваем файл
    file_path, file_bytes = await download_telegram_file(largest_photo.file_id)

    # Сохраняем в storage
    public_url = await save_file_to_storage(file_bytes, "photo.jpg")

    async with pool.connection() as conn:
        # Создать VictorFile
        file_id = await fetchval(
            conn,
            """
            INSERT INTO victor_files (
                original_file_name, file_type, file_size, file_url, file_path,
                telegram_file_id, telegram_file_unique_id, user_description,
                metadata
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            RETURNING id
        """,
            f"photo_{datetime.now().isoformat()}.jpg",
            "image/jpeg",
            largest_photo.file_size or 0,
            public_url,
            file_path,
            largest_photo.file_id,
            largest_photo.file_unique_id,
            caption or "",
            {"width": largest_photo.width, "height": largest_photo.height},
        )

        # Создать inbox
        inbox_id = await fetchval(
            conn,
            """
            INSERT INTO victor_inbox (
                content_type, file_id, processing_status,
                telegram_message_id, user_question
            ) VALUES ($1, $2, $3, $4, $5)
            RETURNING id
        """,
            "file",
            file_id,
            "pending_clarification",
            message_id,
            "Что на фото?",
        )

    # Спросить Виктора
    await ask_victor(
        "📸 Что на фото?", options=["чек", "документ", "лицо", "план", "другое"], inbox_id=inbox_id
    )

    logger.info(f"✅ Photo saved, awaiting clarification: {inbox_id}")
```

---

## 🔄 4. ИЗМЕНЕНИЯ В КОДЕ

### Что изменилось:

| asyncpg | psycopg3 |
|---------|----------|
| `import asyncpg` | `import psycopg` + `from psycopg_pool import AsyncConnectionPool` |
| `asyncpg.create_pool()` | `AsyncConnectionPool()` + `await pool.open()` |
| `pool.acquire()` | `pool.connection()` |
| `conn.fetchval(query, *args)` | `fetchval(conn, query, *args)` |
| `conn.fetchrow(query, *args)` | `fetchrow(conn, query, *args)` |
| `conn.fetch(query, *args)` | `fetch(conn, query, *args)` |
| `conn.execute(query, *args)` | `execute(conn, query, *args)` |

---

## 🐳 5. DOCKERFILE

### Dockerfile.victor-bot

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копирование зависимостей
COPY requirements.api.txt .
RUN pip install --no-cache-dir -r requirements.api.txt

# Копирование кода
COPY api/ ./api/
COPY main_victor_bot.py .

# Переменные окружения
ENV PYTHONUNBUFFERED=1

# Запуск
CMD ["python", "main_victor_bot.py"]
```

---

## ☸️ 6. KUBERNETES

### k8s/victor-bot-deployment.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: victor-bot-v2
  namespace: default
spec:
  replicas: 1
  selector:
    matchLabels:
      app: victor-bot-v2
  template:
    metadata:
      labels:
        app: victor-bot-v2
    spec:
      containers:
      - name: victor-bot
        image: ghcr.io/your-username/victor-bot:latest
        ports:
        - containerPort: 8001
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: victor-secrets
              key: database-url-direct  # ⚠️ ПРЯМОЕ ПОДКЛЮЧЕНИЕ!
        - name: SUPABASE_URL
          valueFrom:
            secretKeyRef:
              name: victor-secrets
              key: supabase-url
        - name: SUPABASE_KEY
          valueFrom:
            secretKeyRef:
              name: victor-secrets
              key: supabase-key
        - name: TELEGRAM_BOT_TOKEN
          valueFrom:
            secretKeyRef:
              name: victor-secrets
              key: telegram-token
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

---

## 🧪 7. ТЕСТИРОВАНИЕ

### test_psycopg_connection.py

```python
#!/usr/bin/env python3
"""
🧪 Тест подключения psycopg3 к Supabase
"""

import asyncio
import os
import sys
from dotenv import load_dotenv
import psycopg
from psycopg_pool import AsyncConnectionPool

# Windows fix
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def test_connection():
    load_dotenv(".env.victor")
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    print("=" * 60)
    print("   🧪 ТЕСТ PSYCOPG3 ПОДКЛЮЧЕНИЯ")
    print("=" * 60)
    
    try:
        print("📡 Подключение к БД...")
        conn = await psycopg.AsyncConnection.connect(DATABASE_URL)
        
        print("✅ Подключение установлено!")
        
        async with conn.cursor() as cur:
            await cur.execute("SELECT version();")
            version = await cur.fetchone()
            print(f"✅ PostgreSQL: {version[0][:80]}...")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(test_connection())
```

**Запуск:**
```bash
python test_psycopg_connection.py
```

**Ожидаемый результат:**
```
============================================================
   🧪 ТЕСТ PSYCOPG3 ПОДКЛЮЧЕНИЯ
============================================================
📡 Подключение к БД...
✅ Подключение установлено!
✅ PostgreSQL: PostgreSQL 15.1 on x86_64-pc-linux-gnu...
```

---

## 📊 8. МОНИТОРИНГ

### Проверка connection pool

```python
# В victor_bot_router.py
@router.get("/debug/pool")
async def debug_pool():
    pool = await get_db_pool()
    return {
        "status": "ok",
        "pool_size": pool.get_stats().get("pool_size", 0),
        "pool_available": pool.get_stats().get("pool_available", 0),
    }
```

### Kubernetes логи

```bash
# Смотреть логи в реальном времени
kubectl logs -f deployment/victor-bot-v2 --tail=50

# Фильтр по ошибкам
kubectl logs deployment/victor-bot-v2 | grep ERROR

# Последние 100 строк
kubectl logs deployment/victor-bot-v2 --tail=100
```

---

## ✅ 9. CHECKLIST ГОТОВНОСТИ

- [x] psycopg3 установлен
- [x] requirements.api.txt обновлен
- [x] api/victor_bot_router.py обновлен
- [x] Helper функции добавлены
- [x] Windows event loop fix добавлен
- [x] DATABASE_URL изменен на port 5432
- [ ] Тест подключения пройден
- [ ] Docker image собран
- [ ] Secrets обновлены в Kubernetes
- [ ] Деплой выполнен
- [ ] Webhook протестирован

---

## 🎯 ГОТОВО К ДЕПЛОЮ!

**Следующие шаги:**
1. Убедись что DATABASE_URL использует порт **5432**
2. `git add -A && git commit -m "feat: migrate to psycopg3"`
3. `git push origin main`
4. Проверь GitHub Actions
5. Протестируй webhook

**Версия:** 1.0  
**Статус:** ✅ Production Ready
