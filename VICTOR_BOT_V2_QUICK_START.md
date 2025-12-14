# 🚀 VICTOR BOT v2.0 - QUICK START GUIDE

**Version:** 2.0.0  
**Date:** 14 декабря 2025  
**Status:** 🟢 READY FOR DEPLOYMENT

---

## 📋 СОДЕРЖАНИЕ

1. [Обзор системы](#обзор-системы)
2. [Быстрый старт (5 минут)](#быстрый-старт)
3. [Установка зависимостей](#установка-зависимостей)
4. [Настройка БД](#настройка-бд)
5. [Конфигурация](#конфигурация)
6. [Запуск](#запуск)
7. [Тестирование](#тестирование)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 ОБЗОР СИСТЕМЫ

### Что это?

**Victor Bot v2.0** — универсальный сенсор для автоматического сбора ВСЕХ данных от Виктора через Telegram:

- ✅ **Текст** → автоматическая классификация (встреча/задача/идея/расход)
- ✅ **Фото** → OCR распознавание + вопрос "что это?"
- ✅ **Видео** → сохранение + вопрос "опиши"
- ✅ **Аудио** → автоматическая транскрипция (Whisper)
- ✅ **Голос** → автоматическая транскрипция
- ✅ **Документы** → сохранение + вопрос "тип документа?"
- ✅ **Контакты** → вопрос "сохранить?"
- ✅ **Геолокация** → автоматическое сохранение

### Архитектура

```
Telegram (Виктор) → Webhook API → Database (Supabase) → Processing Queue → AI Workers
```

### Ключевые компоненты

| Компонент | Файл | Описание |
|-----------|------|----------|
| Database Schema | `database/victor_bot_v2_schema.sql` | Таблицы БД |
| API Router | `api/victor_bot_router.py` | Telegram webhook + endpoints |
| Background Worker | `workers/processing_queue_worker.py` | OCR, транскрипция, анализ |
| Main App | `main_victor_bot.py` | FastAPI application |
| Dependencies | `requirements.api.txt` | Python packages |
| Configuration | `.env.victor-bot-v2.example` | Environment vars |

---

## ⚡ БЫСТРЫЙ СТАРТ

### Предварительные требования

- ✅ Python 3.11+
- ✅ PostgreSQL 15+ (Supabase)
- ✅ Telegram Bot Token
- ✅ OpenAI API Key (для Whisper/GPT-4 Vision)
- ✅ Tesseract OCR (опционально)

### Шаг 1: Клонировать репозиторий

```bash
cd C:\Projects\personal-assistant-bot
```

### Шаг 2: Создать виртуальное окружение

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Шаг 3: Установить зависимости

```powershell
pip install -r requirements.api.txt
```

### Шаг 4: Настроить БД

#### 4.1. Открыть Supabase SQL Editor

https://app.supabase.com/project/lvixtpatqrtuwhygtpjx/sql

#### 4.2. Выполнить SQL схему

```sql
-- Скопировать содержимое database/victor_bot_v2_schema.sql
-- Вставить в SQL Editor
-- Нажать "Run"
```

**Ожидаемый результат:**

```
✅ 4 tables created: victor_inbox, victor_files, victor_observations, victor_processing_queue
✅ Foreign keys configured
✅ Indexes created
✅ Triggers added
✅ Views created
```

### Шаг 5: Настроить .env

```powershell
# Скопировать пример
cp .env.victor-bot-v2.example .env

# Отредактировать .env (заполнить ключи)
notepad .env
```

**Минимальная конфигурация:**

```env
TELEGRAM_BOT_TOKEN=7234567890:AAHdqTcvbXYqX8c3_example
VICTOR_CHAT_ID=123456789
DATABASE_URL=postgresql://postgres:password@db.lvixtpatqrtuwhygtpjx.supabase.co:5432/postgres
OPENAI_API_KEY=sk-proj-example_key_here
```

### Шаг 6: Запустить сервер

```powershell
python main_victor_bot.py
```

**Ожидаемый вывод:**

```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
🚀 Starting Victor Bot v2.0...
✅ Background worker started
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Шаг 7: Настроить Telegram Webhook

```powershell
# Установить webhook
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" `
  -H "Content-Type: application/json" `
  -d '{
    "url": "https://your-domain.com/api/telegram/webhook"
  }'
```

**Для локального тестирования используйте ngrok:**

```powershell
# Установить ngrok
choco install ngrok

# Запустить туннель
ngrok http 8000

# Использовать ngrok URL для webhook
# https://abc123.ngrok.io/api/telegram/webhook
```

### Шаг 8: Протестировать

Отправьте сообщение боту в Telegram:

```
Виктор: "Встреча с Петровым завтра в 10:00"
```

**Ожидаемый результат:**

```
Бот: ✅ Записано как meeting
```

---

## 📦 УСТАНОВКА ЗАВИСИМОСТЕЙ

### Python Packages

```powershell
pip install -r requirements.api.txt
```

**Основные зависимости:**

| Пакет | Версия | Назначение |
|-------|--------|------------|
| fastapi | 0.109.0 | Web framework |
| uvicorn | 0.27.0 | ASGI server |
| asyncpg | 0.29.0 | PostgreSQL async driver |
| httpx | 0.26.0 | HTTP client |
| python-telegram-bot | 20.7 | Telegram Bot API |
| pytesseract | 0.3.10 | OCR engine |
| openai | 1.7.2 | OpenAI API (Whisper/GPT-4) |
| Pillow | 10.2.0 | Image processing |

### Tesseract OCR (опционально)

#### Windows:

```powershell
choco install tesseract
```

#### Linux:

```bash
sudo apt-get install tesseract-ocr tesseract-ocr-rus
```

#### macOS:

```bash
brew install tesseract tesseract-lang
```

**Проверка установки:**

```bash
tesseract --version
```

---

## 🗄️ НАСТРОЙКА БД

### 1. Создать таблицы

Выполнить SQL:

```sql
-- database/victor_bot_v2_schema.sql
```

### 2. Проверить созданные таблицы

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name LIKE 'victor_%'
ORDER BY table_name;
```

**Ожидаемый результат:**

```
victor_files
victor_inbox
victor_observations
victor_processing_queue
```

### 3. Проверить sample data

```sql
SELECT * FROM victor_observations LIMIT 1;
SELECT * FROM victor_inbox LIMIT 1;
```

### 4. Проверить views

```sql
SELECT * FROM victor_inbox_summary;
SELECT * FROM victor_queue_summary;
SELECT * FROM victor_files_summary;
```

---

## ⚙️ КОНФИГУРАЦИЯ

### Environment Variables

Все настройки в `.env`:

#### Обязательные:

```env
TELEGRAM_BOT_TOKEN=xxx
VICTOR_CHAT_ID=123456789
DATABASE_URL=postgresql://...
OPENAI_API_KEY=sk-xxx
```

#### Опциональные:

```env
AWS_S3_BUCKET=victor-files
TESSERACT_PATH=/usr/bin/tesseract
ENABLE_OCR=true
ENABLE_TRANSCRIPTION=true
ENABLE_IMAGE_ANALYSIS=true
```

### Feature Flags

```env
ENABLE_OCR=true                 # OCR распознавание
ENABLE_TRANSCRIPTION=true        # Транскрипция аудио
ENABLE_FACE_RECOGNITION=false    # Распознавание лиц (TODO)
ENABLE_TABLE_EXTRACTION=false    # Извлечение таблиц (TODO)
ENABLE_IMAGE_ANALYSIS=true       # GPT-4 Vision анализ
```

---

## 🚀 ЗАПУСК

### Запуск в Development Mode

```powershell
python main_victor_bot.py
```

### Запуск с Uvicorn напрямую

```powershell
uvicorn main_victor_bot:app --host 0.0.0.0 --port 8000 --reload
```

### Запуск только Background Worker

```powershell
python workers/processing_queue_worker.py
```

### Запуск в Production (systemd)

```bash
# /etc/systemd/system/victor-bot.service
[Unit]
Description=Victor Bot v2.0 API
After=network.target

[Service]
Type=simple
User=viktor
WorkingDirectory=/home/viktor/personal-assistant-bot
Environment="PATH=/home/viktor/personal-assistant-bot/.venv/bin"
ExecStart=/home/viktor/personal-assistant-bot/.venv/bin/python main_victor_bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable victor-bot
sudo systemctl start victor-bot
sudo systemctl status victor-bot
```

---

## 🧪 ТЕСТИРОВАНИЕ

### 1. Проверка Health Endpoint

```powershell
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

### 2. Проверка Root Endpoint

```powershell
curl http://localhost:8000/
```

**Ожидаемый ответ:**

```json
{
  "service": "Victor Bot v2.0 - Universal Sensor",
  "version": "2.0.0",
  "status": "running",
  "features": {
    "text_processing": "✅ Enabled",
    "file_upload": "✅ Enabled",
    "ocr": "✅ Enabled",
    "transcription": "✅ Enabled (OpenAI Whisper)"
  }
}
```

### 3. Тест Webhook (Manual)

```powershell
curl -X POST http://localhost:8000/api/telegram/webhook `
  -H "Content-Type: application/json" `
  -d '{
    "update_id": 123,
    "message": {
      "message_id": 1,
      "from": {"id": 123456789, "first_name": "Victor"},
      "chat": {"id": 123456789, "type": "private"},
      "date": 1702548600,
      "text": "Встреча с Петровым завтра в 10:00"
    }
  }'
```

**Ожидаемый ответ:**

```json
{
  "ok": true,
  "status": "processed"
}
```

### 4. Проверка БД

```sql
-- Проверить что сообщение сохранилось
SELECT * FROM victor_inbox ORDER BY created_at DESC LIMIT 1;

-- Проверить observation
SELECT * FROM victor_observations ORDER BY created_at DESC LIMIT 1;
```

### 5. Тест OCR

Отправить фото боту в Telegram → должен прийти вопрос "Что на фото?"

### 6. Тест транскрипции

Отправить голосовое сообщение боту → должно прийти "Голос записан. Очередь транскрипции."

---

## 🛠️ TROUBLESHOOTING

### Проблема 1: "DATABASE_URL not configured"

**Решение:**

```powershell
# Проверить .env файл
cat .env | findstr DATABASE_URL

# Убедиться что файл загружается
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('DATABASE_URL'))"
```

### Проблема 2: "TELEGRAM_BOT_TOKEN not configured"

**Решение:**

Добавить в `.env`:

```env
TELEGRAM_BOT_TOKEN=ваш_токен_бота
```

### Проблема 3: Tesseract не найден

**Решение:**

```powershell
# Windows
$env:TESSERACT_PATH="C:\Program Files\Tesseract-OCR\tesseract.exe"

# Или в .env
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
```

### Проблема 4: OpenAI API ошибка

**Решение:**

```powershell
# Проверить API key
python -c "import openai; openai.api_key='ваш_ключ'; print(openai.Model.list())"
```

### Проблема 5: Background worker не запускается

**Решение:**

```powershell
# Запустить worker отдельно
python workers/processing_queue_worker.py

# Проверить логи
tail -f logs/worker.log
```

### Проблема 6: Файлы не сохраняются

**Решение:**

```powershell
# Создать директорию uploads
mkdir uploads

# Проверить права
icacls uploads
```

---

## 📊 МОНИТОРИНГ

### Проверка статуса inbox

```sql
SELECT * FROM victor_inbox_summary;
```

### Проверка очереди обработки

```sql
SELECT * FROM victor_queue_summary;
```

### Проверка файлов

```sql
SELECT * FROM victor_files_summary;
```

### Логи

```powershell
# FastAPI logs
tail -f logs/api.log

# Worker logs
tail -f logs/worker.log
```

---

## 📚 ДОКУМЕНТАЦИЯ API

### Swagger UI

http://localhost:8000/docs

### ReDoc

http://localhost:8000/redoc

### OpenAPI JSON

http://localhost:8000/openapi.json

---

## 🎯 NEXT STEPS

После успешного запуска:

1. ✅ Настроить Telegram Webhook на production URL
2. ✅ Настроить SSL сертификат
3. ✅ Настроить systemd service
4. ✅ Настроить мониторинг (Prometheus + Grafana)
5. ✅ Настроить backup БД
6. ✅ Добавить rate limiting
7. ✅ Добавить логирование в Sentry

---

## 📞 ПОДДЕРЖКА

**Issues:** https://github.com/vik9541/personal-assistant-bot/issues  
**Email:** viktor@97v.ru  
**Telegram:** @vik9541

---

## ✅ CHECKLIST ДЛЯ DEPLOYMENT

- [ ] Python 3.11+ установлен
- [ ] PostgreSQL БД создана
- [ ] SQL schema применена
- [ ] .env настроен
- [ ] Dependencies установлены
- [ ] Tesseract установлен (опционально)
- [ ] API сервер запускается
- [ ] Background worker запускается
- [ ] Health endpoint работает
- [ ] Telegram webhook настроен
- [ ] Тестовое сообщение обработано
- [ ] OCR работает (опционально)
- [ ] Транскрипция работает (опционально)

---

**Version:** 2.0.0  
**Last Updated:** 14 December 2025  
**Status:** 🟢 PRODUCTION READY
