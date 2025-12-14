# 🚀 VICTOR BOT v2.0 - DEPLOYMENT STEPS

## ✅ ШАГ 1: Загрузка SQL схемы в Supabase (ВЫПОЛНИТЬ ВРУЧНУЮ)

### 1.1. Открыть Supabase SQL Editor

👉 **URL:** https://app.supabase.com/project/lvixtpatqrtuwhygtpjx/sql/new

### 1.2. Скопировать SQL схему

```powershell
# Откройте файл и скопируйте весь SQL код:
notepad database\victor_bot_v2_schema.sql

# Или скопировать в буфер обмена:
Get-Content database\victor_bot_v2_schema.sql | Set-Clipboard
```

### 1.3. Вставить и выполнить в Supabase

1. Откройте SQL Editor в Supabase
2. Вставьте скопированный SQL код
3. Нажмите **"RUN"** (или F5)
4. Дождитесь завершения

### 1.4. Ожидаемый результат

```
✅ Success. No rows returned
```

### 1.5. Проверка созданных таблиц

Выполните в SQL Editor:

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name LIKE 'victor_%'
ORDER BY table_name;
```

**Ожидаемый вывод:**

```
victor_files
victor_inbox
victor_observations
victor_processing_queue
```

---

## ✅ ШАГ 2: Установка зависимостей

```powershell
# Активировать venv (если не активирован)
.\.venv\Scripts\Activate.ps1

# Установить пакеты (УЖЕ ВЫПОЛНЕНО ✅)
# pip install httpx asyncpg python-telegram-bot aiogram pytesseract Pillow openai boto3
```

**Статус:** ✅ ВЫПОЛНЕНО

---

## ✅ ШАГ 3: Конфигурация .env

**Статус:** ✅ ВЫПОЛНЕНО

Проверить переменные:

```powershell
Get-Content .env | Select-String "VICTOR_CHAT_ID|DATABASE_URL|TELEGRAM_BOT_TOKEN"
```

**Должны быть:**

- ✅ TELEGRAM_BOT_TOKEN
- ✅ VICTOR_CHAT_ID
- ✅ DATABASE_URL
- ✅ SUPABASE_URL
- ✅ SUPABASE_KEY

---

## ✅ ШАГ 4: Запуск API сервера

### 4.1. Запустить сервер

```powershell
python main_victor_bot.py
```

### 4.2. Ожидаемый вывод

```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
🚀 Starting Victor Bot v2.0...
✅ Background worker started
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## ✅ ШАГ 5: Тестирование

### 5.1. Health Check

```powershell
# В новом терминале:
curl http://localhost:8000/api/health
```

**Ожидаемый ответ:**

```json
{
  "status": "ok",
  "service": "Victor Bot v2.0 API",
  "timestamp": "2025-12-14T18:30:00Z"
}
```

### 5.2. Root Endpoint

```powershell
curl http://localhost:8000/
```

### 5.3. Тест Webhook (локально)

```powershell
curl -X POST http://localhost:8000/api/telegram/webhook `
  -H "Content-Type: application/json" `
  -d '{
    "update_id": 1,
    "message": {
      "message_id": 1,
      "from": {"id": 1743141472, "first_name": "Viktor"},
      "chat": {"id": 1743141472, "type": "private"},
      "date": 1734192000,
      "text": "Тестовое сообщение"
    }
  }'
```

---

## ✅ ШАГ 6: Настройка Telegram Webhook (опционально)

### Для локальной разработки (ngrok):

```powershell
# Установить ngrok
choco install ngrok

# Запустить туннель
ngrok http 8000

# Установить webhook (замените URL)
$ngrokUrl = "https://abc123.ngrok.io"
curl -X POST "https://api.telegram.org/bot8457627946:AAEKY9QoV4yI8A9D5u6lJflralz480uazp8/setWebhook" `
  -d "url=$ngrokUrl/api/telegram/webhook"
```

### Для production:

```powershell
# Использовать ваш домен
curl -X POST "https://api.telegram.org/bot8457627946:AAEKY9QoV4yI8A9D5u6lJflralz480uazp8/setWebhook" `
  -d "url=https://97v.ru/api/telegram/webhook"
```

---

## 📊 ПРОВЕРКА РАБОТЫ БД

### Проверить что сообщения сохраняются:

Выполните в Supabase SQL Editor:

```sql
-- Проверить inbox
SELECT * FROM victor_inbox ORDER BY created_at DESC LIMIT 5;

-- Проверить observations
SELECT * FROM victor_observations ORDER BY created_at DESC LIMIT 5;

-- Проверить файлы
SELECT * FROM victor_files ORDER BY created_at DESC LIMIT 5;

-- Проверить очередь
SELECT * FROM victor_processing_queue ORDER BY created_at DESC LIMIT 5;

-- Сводка
SELECT * FROM victor_inbox_summary;
```

---

## 🎯 ТЕКУЩИЙ СТАТУС

- ✅ SQL схема создана: `database/victor_bot_v2_schema.sql`
- ✅ API роутер создан: `api/victor_bot_router.py`
- ✅ Background worker создан: `workers/processing_queue_worker.py`
- ✅ Main app создан: `main_victor_bot.py`
- ✅ Зависимости установлены
- ✅ .env настроен
- ⏳ SQL схема НЕ загружена в Supabase (выполнить вручную)
- ⏳ API сервер НЕ запущен

---

## 🚨 ВАЖНО

1. **Сначала загрузите SQL схему в Supabase** (Шаг 1)
2. Затем запустите API сервер (Шаг 4)
3. Проверьте health endpoint (Шаг 5.1)
4. Протестируйте webhook (Шаг 5.3)

---

**Next:** После загрузки SQL схемы в Supabase выполните:

```powershell
python main_victor_bot.py
```
