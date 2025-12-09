# 🧠 FULL CONTEXT CONTACT INTELLIGENCE (v2.1)
**Module:** Contact Intelligence
**Status:** IMPLEMENTATION
**Security Level:** HIGH (Encryption Enabled)

---

## 1. EXECUTIVE SUMMARY
Модуль для агрегации, анализа и автоматизации общения.
**Full Context Strategy:** Мы отправляем в AI полные данные (имена, телефоны, адреса), чтобы получить максимально точный анализ и контекст.
**Security:** База данных защищена шифрованием AES-256 (At-Rest), чтобы предотвратить утечки при дампе БД.

---

## 2. ARCHITECTURE

```mermaid
graph TD
    User[Contact Message] -->|Telegram/WhatsApp| n8n[n8n Webhook]
    n8n -->|Raw Payload| API[FastAPI Service]
    
    subgraph "Super Brain Core"
        API -->|1. Encrypt (AES-256)| DB[(Supabase Interactions)]
        API -->|2. Full Text Analysis| OpenAI[GPT-4o]
        
        subgraph "Intelligence Loop"
            OpenAI -->|Sentiment/Intent| API
            API -->|Update Profile| Vector[(pgvector)]
        end
        
        Vector -->|Semantic Search| RAG[Context Retrieval]
    end
```

---

## 3. DATA FLOW & SECURITY

### 3.1. Ingestion (Вход)
1. **n8n** получает сообщение.
2. **n8n** передает JSON на `POST /api/v1/contact/ingest`.
3. **API**:
   - Генерирует вектор (embedding) по *полному* тексту.
   - Шифрует текст ключом `CONTACT_ENCRYPTION_KEY` для сохранения в поле `message_encrypted`.
   - Отправляет *полный* текст в GPT-4o для анализа.

### 3.2. Response Strategy
- Если `urgency` = `high` -> Мгновенное уведомление в Admin Bot.
- Если `auto_respond` = `true` -> Генерация ответа через RAG (поиск похожих ситуаций в прошлом).

---

## 4. DATABASE SCHEMA

### `contacts`
- `id`: UUID
- `name`: Text
- `telegram_id`: BigInt (Unique)
- `communication_style`: JSONB (ML Profile)

### `interactions`
- `contact_id`: UUID
- `message_encrypted`: TEXT (AES-256 string)
- `embedding`: VECTOR(1536)
- `sentiment`: Enum
- `message_metadata`: JSONB (AI Analysis Result)

---

## 5. API ENDPOINTS

- `POST /api/v1/contact/ingest` - Прием сообщения из n8n.
- `POST /api/v1/contact/analyze/{id}` - Принудительный переанализ.
- `GET /api/v1/contact/profile/{id}` - Получение ML-профиля общения.
