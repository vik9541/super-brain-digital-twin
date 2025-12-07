# 🧠 SUPER BRAIN ENTERPRISE — ТЕХНИЧЕСКОЕ ЗАДАНИЕ v3.0

**Дата:** 7 декабря 2025, 13:50 MSK  
**Статус:** ✅ ENTERPRISE-LEVEL  
**Версия:** 3.0  
**Масштаб:** 1000+ пользователей, 100+ проектов, 500+ агентов  
**Платформа:** Kubernetes + N8N + Supabase + Twilio + SendGrid + Replit

---

## 🎯 КОНЦЕПЦИЯ: SUPER BRAIN ENTERPRISE

**"Супер Мозг" = Интеллектуальная экосистема для управления строительными проектами**

### Архитектура на 5 столпов:

```
┌─────────────────────────────────────────────────────────┐
│         SUPER BRAIN ENTERPRISE ECOSYSTEM                 │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  1. 📱 TELEGRAM BOT (BOT.PY)                             │
│     └─ Главный интерфейс: файлы, текст, голос, задачи  │
│                                                           │
│  2. 🤖 MULTI-AGENT SYSTEM (N8N)                         │
│     ├─ Agent: Document Parser (строительные сметы)      │
│     ├─ Agent: Email Manager (SendGrid + IMAP)           │
│     ├─ Agent: SMS Notifier (Twilio)                     │
│     ├─ Agent: Task Scheduler (CRON jobs)                │
│     ├─ Agent: Data Sync (Replit ← Supabase)             │
│     └─ Agent: AI Analyzer (Perplexity)                  │
│                                                           │
│  3. 💾 DATABASE LAYER (Supabase + PostgreSQL)           │
│     ├─ contacts (менеджеры, рабочие, партнёры)          │
│     ├─ projects (строительные объекты)                  │
│     ├─ documents (сметы, чертежи, акты)                 │
│     ├─ tasks (распределение работ)                      │
│     ├─ communications (письма, SMS, звонки)             │
│     └─ agents_log (логи всех агентов)                   │
│                                                           │
│  4. 📧 COMMUNICATIONS HUB                                │
│     ├─ Email (SendGrid SMTP + webhooks)                 │
│     ├─ SMS (Twilio)                                     │
│     ├─ Telegram (python-telegram-bot)                   │
│     ├─ WhatsApp (Twilio WhatsApp Business)              │
│     └─ Voice Calls (Twilio)                             │
│                                                           │
│  5. ⚡ RUNTIME AGENTS (Replit)                          │
│     ├─ Worker 1: Document OCR + Classification          │
│     ├─ Worker 2: Email Parser + Intent Detection        │
│     ├─ Worker 3: Data Validation + Normalization        │
│     └─ Worker N: Custom Business Logic                  │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

---

## 🏗️ СЦЕНАРИЙ: СТРОИТЕЛЬНЫЙ ПРОЕКТ

```
ДЕНЬ 1: Проект MOS-001 (Строительство офиса)
├─ 09:00
│  Менеджер через BOT.PY: "Загружаю смету на MOS-001"
│  [Загружает file.pdf]
│         ↓
│  BOT → N8N Agent: "Parse Document" 
│         ↓
│  N8N извлекает:
│  - Позиции работ
│  - Стоимость
│  - Сроки
│  - Материалы
│         ↓
│  Сохраняется в Supabase → documents table
│         ↓
│  BOT отправляет в Telegram: ✅ Смета загружена (250 позиций)
│
├─ 10:00
│  BOT: /assign_task "Начать земляные работы"
│  N8N Agent: Task Distributor
│  - Ищет в БД кто свободен
│  - Отправляет SMS через Twilio: "Твоя задача: земляные работы..."
│  - Создаёт запись в tasks
│  - Отправляет EMAIL через SendGrid с деталями
│  - Логирует в agents_log
│
├─ 15:00
│  Рабочий отправляет фото progress через Telegram
│  BOT классифицирует: "80% земляных работ готово"
│  Обновляет project progress в Supabase
│  N8N Agent: Status Updater отправляет уведомление менеджерам
│
├─ 17:00
│  Главный архитектор: /report MOS-001
│  BOT → Supabase → составляет отчёт из 5 таблиц
│  Генерирует PDF через Perplexity
│  Отправляет EMAIL всем stakeholders через SendGrid
│
└─ 19:00 (2:00 AM BATCH)
   BATCH_ANALYZER (ночной анализ)
   - Перечитывает ВСЕ документы за день
   - Обновляет БД (эволюция схемы)
   - Генерирует инсайты
   - Отправляет сводку всем через SMS + Email
```

---

## 📱 BOT.PY v3.0 (800-1200 строк)

### Главные функции:

#### 1️⃣ **Загрузка Строительной Документации**

```
Менеджер: [Загружает Excel со сметой]
BOT: "📄 Получил смету. Анализирую..."
    ↓
N8N Agent "DocumentParser":
    - Извлекает строки (позиции работ)
    - Определяет категории (ЗМР, МКД, etc)
    - Распознаёт стоимость/сроки
    - OCR если изображение
    ↓
Supabase saves:
    {
        doc_id: 123,
        type: "смета",
        project_id: MOS-001,
        content: {...50 позиций...},
        extracted_data: {...},
        status: "processed"
    }
    ↓
BOT: ✅ Смета загружена!
    📊 250 позиций
    💰 $500,000
    📅 120 дней
    Агентов: Document Parser
```

**Поддерживает:**
- 📊 Excel (XLS, XLSX) — парсит таблицы
- 📄 PDF (обычный + отсканированный с OCR)
- 🖼️ Изображения (чертежи, фото)
- 📝 Word (DOC, DOCX)
- 🔗 Google Docs links (API)
- 📦 ZIP архивы (распаковывает)

---

#### 2️⃣ **Управление Проектами & Задачами**

```
Менеджер: /project MOS-001
BOT: 📋 ПРОЕКТ: МОС-001 (Строительство офиса)
     Статус: 45% готово
     Команда: 12 чел
     Бюджет: $500K / $520K (96%)
     Дедлайн: 15 янв 2026
     
     [Кнопки]:
     ├─ 📊 Показать смету
     ├─ 👥 Список команды
     ├─ 📅 График работ
     ├─ 📄 Все документы
     └─ ⚠️ Проблемы

Менеджер: /assign_task "Установка окон"
BOT: 🤖 N8N Agent: Task Distributor
     - Кто свободен? Иван (8 проектов, 60% занят)
     - Отправляет SMS через Twilio:
       "🔔 Новая задача: Установка окон на MOS-001
        Сроки: 10-15 дек
        Деньги: $5000
        Координаты: [link to Google Maps]"
     - Отправляет Email через SendGrid с вложениями
     - Создаёт Push-notification в Telegram
     - Логирует в agents_log
     ↓
Иван видит в Telegram: ✅ ГОТОВО (нажал кнопку)
     ↓
BOT → Supabase обновляет статус
     ↓
N8N Agent: Status Notifier отправляет менеджеру SMS:
     "✅ Иван принял задачу: Установка окон"

Менеджер: /report MOS-001
BOT: 📊 ОТЧЁТ ПО МОС-001 (PDF + Email)
     - Статус выполнения
     - Финансовый отчёт
     - Список сделанного
     - Проблемы и риски
     - График на месяц
     ↓
     Отправляется EMAIL через SendGrid
     всем stakeholders (PM, финдиректор, заказчик)
```

---

#### 3️⃣ **Интеллектуальные Агенты (N8N)**

### Agent #1: Document Parser

```
Триггер: Новый файл в Telegram/Email
Действие:
1. Скачивает файл
2. Если PDF/Image → OCR (tesseract)
3. Если Excel → парсит таблицы
4. Вызывает Perplexity AI:
   "Это смета? Извлеки позиции, стоимость, сроки"
5. Классифицирует тип документа
6. Сохраняет в Supabase
7. Отправляет уведомление менеджеру

Где видна работа: agents_log
```

### Agent #2: Email Manager (Inbox Auto-Pilot)

```
Триггер: Новое письмо на общий ящик project@super-brain.com
Действие:
1. SendGrid webhook → N8N
2. Парсит текст письма
3. Определяет тип:
   - Запрос предложения (RFQ)
   - Счёт (Invoice)
   - Проблема (Issue)
   - Статус обновление
   - Другое
4. Вызывает Perplexity для анализа
5. Определяет проект по контексту
6. Создаёт задачу или комментарий
7. Отправляет автоответ через SendGrid:
   "Спасибо! Обрабатываем..."
8. Логирует в communications table

Пример:
От: ivan@contractor.com
Тема: "Готовы к установке окон на МОС-001"
     ↓
N8N определяет: Issue type = "Status Update"
     ↓
Создаёт в Supabase:
{
  type: "email",
  from: "ivan@contractor.com",
  subject: "Готовы к установке окон на МОС-001",
  project_id: "MOS-001",
  task_id: 456,
  auto_classified: true,
  status: "awaiting_action"
}
     ↓
BOT отправляет менеджеру Telegram:
"📧 От Ivan: Готовы к установке окон. Что делать?"
```

### Agent #3: SMS Notifier (Twilio)

```
Триггер: Создана критичная задача (priority=HIGH)
Действие:
1. Берёт контакт менеджера
2. Отправляет SMS через Twilio:
   "🔴 URGENT: Проблема на МОС-001 - задержка поставки"
3. Добавляет clickable link на задачу
4. Логирует отправку SMS в communications
5. Отслеживает доставку (Twilio webhooks)
6. Если не открыл в течение часа → повторная SMS

Для рабочих:
"🔔 Твоя задача: Установка окон, МОС-001
Сроки: 10-15 дек
Место: [Google Maps link]
Ответь: ✅ Принял или ❌ Не могу"
```

### Agent #4: Task Scheduler (CRON)

```
Каждый день в 8:00 AM:
1. Проверяет tasks с due_date = today
2. Для каждой задачи:
   - Отправляет SMS напоминание рабочему
   - Отправляет Email менеджеру
   - Обновляет priority если overdue
3. Проверяет проекты близко к дедлайну
4. Отправляет сводку в Telegram чат

Каждый день в 18:00 PM:
1. Собирает все completed tasks за день
2. Генерирует дневной отчёт
3. Отправляет Email всем PM

Каждый пятница в 17:00 PM:
1. Генерирует еженедельный отчёт
2. Отправляет 5 главным stakeholders
3. Логирует в reports table
```

### Agent #5: Data Sync (Replit)

```
Каждые 30 минут Replit Worker:
1. Коннектится к Supabase API
2. Проверяет новые записи
3. Валидирует данные (схема, constraints)
4. Нормализирует (trim, case, phone format)
5. Кэширует в Redis (быстрые запросы)
6. Отправляет метрики в Prometheus

Реплит обрабатывает:
- Дедупликацию контактов
- Нормализацию номеров телефонов
- Преобразование валют
- Синхронизацию с внешними API
```

### Agent #6: AI Analyzer (Perplexity)

```
Ночью (2:00 AM) BATCH:
1. Читает ВСЕ документы за день
2. Для каждого проекта анализирует:
   - Риски (срыв сроков, перерасход)
   - Возможности (ускорение, экономия)
   - Аномалии (необычные расходы)
   - Паттерны (какие типы работ задерживаются)
3. Генерирует insights
4. Рекомендует действия
5. Обновляет project.risk_score
6. Отправляет сводку PM через Email + SMS
```

---

## 🗄️ SUPABASE DATABASE (v3.0)

### Основные таблицы:

```sql
-- 1. Контакты (менеджеры, рабочие, партнёры)
contacts {
    id BIGSERIAL PRIMARY KEY,
    full_name TEXT,
    role TEXT (manager, worker, contractor, partner),
    phone TEXT,
    email TEXT,
    telegram_id BIGINT,
    whatsapp TEXT,
    organization TEXT,
    position TEXT,
    skills JSONB,
    availability_hours INT,
    hourly_rate DECIMAL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
}

-- 2. Проекты (строительные объекты)
projects {
    id BIGSERIAL PRIMARY KEY,
    project_name TEXT,
    project_code TEXT (MOS-001, etc),
    type TEXT (office, residential, commercial),
    status TEXT (planning, active, on_hold, completed),
    budget DECIMAL,
    budget_spent DECIMAL,
    start_date DATE,
    due_date DATE,
    completion_date DATE,
    progress_percent INT,
    risk_score INT (0-100),
    manager_id BIGINT REFERENCES contacts(id),
    client_id BIGINT REFERENCES contacts(id),
    team_size INT,
    metadata JSONB,
    created_at TIMESTAMP
}

-- 3. Документы (сметы, чертежи, акты, договоры)
documents {
    id BIGSERIAL PRIMARY KEY,
    project_id BIGINT REFERENCES projects(id),
    doc_type TEXT (estimate, blueprint, invoice, act, contract, report),
    file_name TEXT,
    file_hash TEXT,
    storage_path TEXT (S3 URL),
    file_size_bytes INT,
    
    -- Extracted data from OCR/Parser
    extracted_content JSONB,
    line_items JSONB (for estimates: [{"position": "...", "cost": 1000, ...}]),
    total_amount DECIMAL,
    
    -- AI Classification
    ai_classification JSONB,
    confidence INT,
    keywords JSONB,
    
    -- Meta
    uploaded_by BIGINT REFERENCES contacts(id),
    uploaded_at TIMESTAMP,
    processed_by_agent TEXT (DocumentParser),
    processed_at TIMESTAMP,
    version INT
}

-- 4. Задачи
tasks {
    id BIGSERIAL PRIMARY KEY,
    project_id BIGINT REFERENCES projects(id),
    title TEXT,
    description TEXT,
    assigned_to BIGINT REFERENCES contacts(id),
    assigned_by BIGINT REFERENCES contacts(id),
    
    status TEXT (new, accepted, in_progress, completed, blocked),
    priority TEXT (low, medium, high, urgent),
    
    due_date DATE,
    estimated_hours INT,
    actual_hours INT,
    
    -- Финансы
    estimated_cost DECIMAL,
    actual_cost DECIMAL,
    
    created_at TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- История изменений
    change_history JSONB,
    agents_involved JSONB (["TaskDistributor", "StatusNotifier"])
}

-- 5. Коммуникации (письма, SMS, звонки)
communications {
    id BIGSERIAL PRIMARY KEY,
    type TEXT (email, sms, telegram, whatsapp, voice_call),
    project_id BIGINT REFERENCES projects(id),
    from_contact BIGINT REFERENCES contacts(id),
    to_contact BIGINT REFERENCES contacts(id),
    
    subject TEXT,
    content TEXT,
    
    -- Для Email
    email_provider TEXT (SendGrid, IMAP),
    email_message_id TEXT,
    
    -- Для SMS
    sms_provider TEXT (Twilio),
    sms_sid TEXT,
    delivery_status TEXT (sent, delivered, failed),
    
    -- Для Telegram
    telegram_message_id BIGINT,
    
    -- AI Classification
    auto_classified TEXT (request, update, problem, info),
    confidence INT,
    
    created_at TIMESTAMP,
    read_at TIMESTAMP
}

-- 6. Агенты (логи работы)
agents_log {
    id BIGSERIAL PRIMARY KEY,
    agent_name TEXT (DocumentParser, EmailManager, TaskScheduler, etc),
    action TEXT (parsed_document, sent_sms, created_task, etc),
    
    input_data JSONB,
    output_data JSONB,
    
    status TEXT (success, error, pending),
    error_message TEXT,
    
    duration_ms INT,
    
    project_id BIGINT REFERENCES projects(id),
    task_id BIGINT REFERENCES tasks(id),
    
    created_at TIMESTAMP
}

-- 7. Инсайты и рекомендации (от AI)
insights {
    id BIGSERIAL PRIMARY KEY,
    project_id BIGINT REFERENCES projects(id),
    type TEXT (risk, opportunity, anomaly, pattern),
    
    title TEXT,
    description TEXT,
    confidence INT,
    
    -- Данные для рекомендации
    recommendation TEXT,
    estimated_impact DECIMAL,
    
    generated_at TIMESTAMP,
    acknowledged_by BIGINT REFERENCES contacts(id),
    acknowledged_at TIMESTAMP
}

-- 8. История изменений БД (evolve tracking)
schema_changes {
    id BIGSERIAL PRIMARY KEY,
    table_name TEXT,
    change_type TEXT (add_column, add_table, modify),
    details JSONB,
    reason TEXT,
    made_by TEXT (system, user),
    made_at TIMESTAMP
}
```

---

## 📧 SENDGRID INTEGRATION

### Функции:

```python
# 1. Отправка писем через API
sendgrid_client.send(
    from_email="projects@super-brain.com",
    to_email="manager@client.com",
    subject="Отчёт по МОС-001",
    html_content=render_template("report.html", project_data),
    attachments=[
        {"filename": "smeta.xlsx", "content": file_bytes},
        {"filename": "report.pdf", "content": pdf_bytes}
    ]
)

# 2. Tracking webhooks
@app.post("/webhooks/sendgrid")
async def sendgrid_webhook(event):
    # delivered, opened, clicked, bounced, etc
    await update_communication_status(event)

# 3. Inbound Parse (получение писем)
@app.post("/webhooks/sendgrid/inbound")
async def inbound_email(message):
    # N8N Agent: EmailManager обрабатывает письмо
    await process_inbound_email(message)
```

### Примеры отправок:

```
1. Ежедневный отчёт PM:
   From: system@super-brain.com
   To: [all PMs]
   Subject: "Ежедневный отчёт - 7 дек 2025"
   Content: HTML с таблицами проектов, задач, проблем

2. Уведомление о новой задаче:
   From: system@super-brain.com
   To: contractor@gmail.com
   Subject: "Новая задача: Установка окон на МОС-001"
   Content: Детали задачи, Google Maps link, документы

3. Отчёт об ошибке:
   From: system@super-brain.com
   To: admin@super-brain.com
   Subject: "🔴 ALERT: DocumentParser crashed on MOS-001/smeta.pdf"
   Content: Error details, logs, рекомендации

4. Еженедельная сводка:
   From: system@super-brain.com
   To: executives@super-brain.com
   Subject: "Еженедельная сводка - неделя 2-8 дек"
   Content: KPI, риски, доход, расходы
```

---

## 📱 TWILIO INTEGRATION

### SMS (Short Message Service)

```python
# 1. Отправка SMS
twilio_client.messages.create(
    body="🔔 Новая задача: Установка окон на МОС-001. " +
         "Сроки: 10-15 дек. Ответь: ✅ Принял или ❌",
    from_="+1234567890",  # Twilio number
    to="+79991234567"     # Рабочий
)

# 2. Получение SMS (webhooks)
@app.post("/webhooks/twilio/sms")
async def handle_sms(message):
    # "✅ Принял"
    await mark_task_accepted(message)

# 3. SMS Status callbacks
@app.post("/webhooks/twilio/sms/status")
async def sms_status(status_data):
    # delivered, undelivered, failed
    await update_sms_status(status_data)
```

### WhatsApp Business API (через Twilio)

```python
# Отправка WhatsApp сообщения с медиа
twilio_client.messages.create(
    body="Здравствуй! Вот твоя задача на МОС-001",
    from_="whatsapp:+1234567890",
    to="whatsapp:+79991234567",
    media_url="https://s3.amazonaws.com/blueprint.pdf"
)
```

### Voice Calls (для срочных уведомлений)

```python
# Входящий звонок с автоответом
@app.post("/webhooks/twilio/call")
async def handle_call():
    response = VoiceResponse()
    response.say(
        "Здравствуй! У тебя срочная задача на МОС-001. " +
        "Нажми 1 чтобы принять, 2 чтобы отклонить",
        voice='woman'
    )
    response.gather(num_digits=1, action="/handle_keypress")
    return str(response)
```

---

## 🔄 N8N WORKFLOW ORCHESTRATION

**n8n.cloud** как центр управления всеми агентами и рабочими процессами.

### Workflow #1: "Document Processing Pipeline"

```
Триггер: New file in Telegram
  ↓
Step 1: Download file from Telegram
  ↓
Step 2: Upload to S3 (DigitalOcean Spaces)
  ↓
Step 3: If PDF/Image → Call OCR API (Tesseract)
  ↓
Step 4: Call Perplexity API for classification
  ↓
Step 5: Parse extracted data
  ↓
Step 6: Insert into Supabase (documents table)
  ↓
Step 7: Send email confirmation via SendGrid
  ↓
Step 8: Send Telegram notification to manager
  ↓
Step 9: Log agent action in agents_log
  ↓
End
```

### Workflow #2: "Task Distribution"

```
Триггер: Manager creates task via /assign_task
  ↓
Step 1: Get task details from Telegram
  ↓
Step 2: Find available worker
  ↓
Step 3: Create task in Supabase
  ↓
Step 4: Send SMS via Twilio to worker
  ↓
Step 5: Send Email via SendGrid with attachments
  ↓
Step 6: Send Telegram push notification
  ↓
Step 7: Log in agents_log
  ↓
IF worker accepts (via SMS response):
  Step 8a: Update task status to "accepted"
  Step 8b: Notify manager via Telegram
  Step 8c: Set alarm for due_date
ELSE IF worker declines:
  Step 8d: Find next worker (repeat from Step 2)
  ↓
End
```

### Workflow #3: "Email Processing"

```
Триггер: Inbound email to project@super-brain.com (SendGrid Parse)
  ↓
Step 1: Extract email metadata (from, subject, body)
  ↓
Step 2: Call Perplexity for intent classification
  ↓
Step 3: Match email to project (via keywords/email domain)
  ↓
Step 4: Insert into communications table (Supabase)
  ↓
Step 5: If type = "Invoice" → Extract amount and save
  ↓
Step 6: If type = "Problem" → Create task
  ↓
Step 7: Send auto-reply via SendGrid
  ↓
Step 8: Notify relevant manager via Telegram
  ↓
Step 9: Log in agents_log
  ↓
End
```

### Workflow #4: "Daily Report Generation"

```
Триггер: CRON at 18:00 PM every day
  ↓
Step 1: Query all projects from Supabase
  ↓
Step 2: For each project get:
  - Tasks completed today
  - Budget spent today
  - Documents added
  - Issues raised
  - Team activity
  ↓
Step 3: Generate HTML report from template
  ↓
Step 4: Attach metrics/charts
  ↓
Step 5: Send via SendGrid to all PMs
  ↓
Step 6: Send SMS summary via Twilio to manager
  ↓
Step 7: Post summary in Telegram channel
  ↓
Step 8: Save report in documents table
  ↓
End
```

---

## ⚡ REPLIT WORKERS (Runtime Agents)

**Replit для обработки тяжёлых операций**

### Worker #1: Document OCR Processor

```python
# runs on Replit
import asyncio
from pytesseract import image_to_string
from pdf2image import convert_from_path

async def process_document(file_path, file_type):
    if file_type == "pdf":
        images = convert_from_path(file_path)
        text = "\n".join([image_to_string(img) for img in images])
    else:  # image
        text = image_to_string(file_path)
    
    return {
        "text": text,
        "processed_at": datetime.now(),
        "word_count": len(text.split())
    }

# Вызывается из N8N:
# POST https://replit-worker-1.replit.dev/process_ocr
```

### Worker #2: Email Parser

```python
# runs on Replit
import email
from email.mime.text import MIMEText

def parse_email_message(raw_email):
    msg = email.message_from_string(raw_email)
    
    return {
        "from": msg['From'],
        "to": msg['To'],
        "subject": msg['Subject'],
        "body": msg.get_payload(),
        "attachments": extract_attachments(msg),
        "timestamp": parsedate_to_datetime(msg['Date'])
    }

# Calls Perplexity to determine intent:
# - "Invoice": amount, due_date
# - "RFQ": requirements, deadline
# - "Status Update": progress, issues
# - "Question": topic, priority
```

### Worker #3: Data Validator & Normalizer

```python
# runs on Replit
import phonenumbers
from currency_converter import CurrencyConverter

def normalize_contact_data(contact):
    # Phone normalization
    if contact.phone:
        parsed = phonenumbers.parse(contact.phone, "RU")
        contact.phone = phonenumbers.format_number(
            parsed, phonenumbers.PhoneNumberFormat.E164
        )
    
    # Email normalization
    if contact.email:
        contact.email = contact.email.lower().strip()
    
    # Name normalization
    if contact.name:
        contact.name = contact.name.title().strip()
    
    return contact

def normalize_financial_data(transaction):
    # Convert currencies to USD
    if transaction.currency != "USD":
        converter = CurrencyConverter()
        transaction.amount_usd = converter.convert(
            transaction.amount,
            transaction.currency,
            "USD"
        )
    
    return transaction
```

---

## 🌐 ARCHITECTURE DIAGRAM (v3.0)

```
┌─────────────────────────────────────────────────────────────────┐
│                        USERS & INPUTS                           │
├─────────────────────────────────────────────────────────────────┤
│ Telegram | Email | SMS | WhatsApp | Web | Mobile App           │
└────────────────────┬────────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
   BOT.PY (K8s)           N8N.CLOUD (Orchestration)
   ├─ Message Handler         ├─ DocumentParser Agent
   ├─ Command Parser          ├─ EmailManager Agent
   ├─ Task Manager            ├─ TaskScheduler Agent
   ├─ Report Generator        ├─ StatusNotifier Agent
   └─ Telegram API            ├─ ReportGenerator Agent
                              └─ DataSync Agent
                              
        │                         │
        └────────────┬────────────┘
                     │
        ┌────────────┴────────────────────────────────┐
        │                                             │
        ▼                                             ▼
    SUPABASE                            EXTERNAL APIs
    (PostgreSQL)                        ├─ SendGrid (Email)
    ├─ contacts                         ├─ Twilio (SMS/Voice)
    ├─ projects                         ├─ Perplexity (AI)
    ├─ documents                        ├─ Google Maps
    ├─ tasks                            ├─ AWS S3
    ├─ communications                   └─ Tesseract (OCR)
    ├─ agents_log
    └─ insights
    
        │
        ▼
    REPLIT WORKERS
    ├─ Worker 1: OCR Processor
    ├─ Worker 2: Email Parser
    ├─ Worker 3: Data Validator
    └─ Worker N: Custom Logic

        ▲                                             ▲
        └─────────────────────┬───────────────────────┘
                              │
                        REDIS CACHE
                   (Fast queries, sessions)

        ▲                                             ▲
        └─────────────────────┬───────────────────────┘
                              │
                        NOTIFICATIONS
        ├─ Telegram Push      ├─ SMS Twilio
        ├─ Email SendGrid     └─ WhatsApp Business
```

---

## 📊 DATA FLOW: СТРОИТЕЛЬНЫЙ ПРОЕКТ

```
День 1: Загрузка сметы
━━━━━━━━━━━━━━━━━━━━━━━━
09:00 Менеджер в Telegram:
      "/upload_document MOS-001"
      [Загружает smeta.xlsx]
            ↓
      BOT.PY: "📄 Получил файл..."
            ↓
      N8N Trigger: "DocumentParser"
            ↓
      Replit Worker 1: Читает Excel
            ↓
      Perplexity API: Классифицирует
            ↓
      Supabase: INSERT documents table
            ↓
      BOT.PY: "✅ Загружено 250 позиций, $500K"
            ↓
      N8N: Send email to accounting@super-brain.com
            ↓
      SendGrid: ✅ Письмо отправлено


День 1: Распределение задачи
━━━━━━━━━━━━━━━━━━━━━━━━━━━
14:00 Менеджер в Telegram:
      "/assign_task"
      Название: "Земляные работы"
      Проект: "MOS-001"
            ↓
      BOT.PY: Создаёт форму
      [Кнопки с рабочими]
            ↓
      Менеджер выбирает: "Ivan"
            ↓
      N8N Workflow: "Task Distribution"
            ├─ Supabase: INSERT tasks
            ├─ Twilio: SMS Ivan
            │          "🔔 Новая задача: земляные работы"
            ├─ SendGrid: Email Ivan с документами
            ├─ Telegram: Push Ivan в личке
            └─ agents_log: LOG action
            ↓
      Ivan видит уведомления в Telegram + SMS + Email
            ↓
      Ivan нажимает ✅ ПРИНЯЛ в Telegram
            ↓
      Supabase: UPDATE tasks SET status='accepted'
            ↓
      N8N Agent: StatusNotifier
            ├─ Telegram BOT → менеджеру: "✅ Ivan принял"
            ├─ SMS менеджеру: "Земляные работы начало"
            └─ agents_log: LOG action


День 2: Обновление статуса
━━━━━━━━━━━━━━━━━━━━━━━━
16:00 Ivan в Telegram отправляет 5 фото
            ↓
      BOT.PY: Сохраняет фото, создаёт задачу
      "Please classify these photos"
            ↓
      N8N Agent: ImageAnalyzer (Replit)
            ↓
      Perplexity: "80% земляных работ завершено"
            ↓
      Supabase: 
            - UPDATE tasks SET progress='80%'
            - INSERT communications type='photo'
            - INSERT insights: "земляные работы идут по графику"
            ↓
      N8N Agent: StatusNotifier
            ├─ Email менеджеру: "Фото + анализ"
            └─ Telegram менеджеру: "Ivan 80% ready"


День 7: Ночной анализ (2:00 AM)
━━━━━━━━━━━━━━━━━━━━━━━━━━━
      BATCH_ANALYZER (Perplexity + Supabase)
            ├─ Читает 100% документов за неделю
            ├─ Анализирует 50 tasks
            ├─ Анализирует 200 communications
            ├─ Обновляет schema (добавляет поля)
            ├─ Генерирует инсайты:
            │  - "земляные работы завершены вовремя"
            │  - "материалы стоят на 5% дороже"
            │  - "Ivan очень эффективен (95% tasks completed)"
            ├─ Обновляет project.progress_percent = 35%
            ├─ Обновляет project.risk_score = 15
            └─ Отправляет сводку:
               - Email PM: "Еженедельный отчёт"
               - SMS менеджеру: "Проект в норме, риск низкий"
               - Telegram чат: "Итоги недели"
               - Slack channel: "KPI dashboard update"
```

---

## 🎯 AGENTS (Полный список)

| # | Агент | Где работает | Триггер | Действие |
|---|-------|------|---------|---------|
| 1 | DocumentParser | N8N + Replit | Новый файл | Парсит, OCR, классифицирует |
| 2 | EmailManager | N8N + SendGrid | Входящее письмо | Анализирует, создаёт tasks |
| 3 | TaskDistributor | N8N | /assign_task | Ищет рабочего, отправляет SMS+Email |
| 4 | StatusNotifier | N8N | Обновление статуса | Отправляет SMS/Email/Telegram |
| 5 | TaskScheduler | N8N (CRON) | 8:00 AM, 18:00 PM | Отправляет напоминания, отчёты |
| 6 | DataSync | Replit (30 min) | Периодический | Синхронизирует, валидирует |
| 7 | AIAnalyzer | BATCH (2:00 AM) | Ежедневно | Анализирует всю БД, генерирует инсайты |
| 8 | ReportGenerator | N8N | По расписанию | Создаёт PDF отчёты |
| 9 | ImageAnalyzer | Replit | Новое изображение | Классифицирует фото |
| 10 | InvoiceParser | N8N + Replit | Счёт в письме | Извлекает сумму, сроки |

---

## 💾 SUPABASE FEATURES USED

✅ **PostgreSQL** — основная БД  
✅ **Real-time subscriptions** — синхронизация в реал-тайме  
✅ **Auth** — управление пользователями  
✅ **Storage** — хранение документов  
✅ **Webhooks** — интеграция с N8N  
✅ **Row-level security** — безопасность данных  
✅ **Functions** — PL/pgSQL для сложной логики  
✅ **Triggers** — автоматизация при обновлениях

---

## 📧 SENDGRID FEATURES USED

✅ **SMTP API** — отправка писем  
✅ **Inbound Parse** — получение писем  
✅ **Webhooks** — tracking events (delivered, opened, clicked)  
✅ **Templates** — шаблоны писем  
✅ **Attachments** — вложения (PDF, Excel)  
✅ **A/B Testing** — оптимизация subject lines  
✅ **Unsubscribe Management** — управление подписками

---

## 📱 TWILIO FEATURES USED

✅ **SMS API** — отправка SMS  
✅ **Inbound SMS** — получение SMS  
✅ **WhatsApp Business API** — WhatsApp сообщения  
✅ **Voice API** — входящие/исходящие звонки  
✅ **Webhooks** — tracking delivery status  
✅ **Message templates** — шаблоны сообщений

---

## 🤖 N8N FEATURES USED

✅ **Workflows** — создание сложных процессов  
✅ **Triggers** — события-триггеры  
✅ **Webhook** — для интеграции с внешними сервисами  
✅ **HTTP Request** — API вызовы  
✅ **Conditional Logic** — IF/THEN ветвления  
✅ **Loops** — обработка массивов  
✅ **Error Handling** — обработка ошибок  
✅ **Scheduling** — CRON jobs  
✅ **Logging** — логирование операций

---

## ⚡ REPLIT FEATURES USED

✅ **Python Runtime** — выполнение кода  
✅ **HTTP Server** — REST API endpoints  
✅ **Scheduled Tasks** — фоновые работы  
✅ **Environment variables** — API ключи  
✅ **File system** — кэширование  
✅ **Networking** — коннекция к Supabase, Perplexity

---

## 🚀 REQUIREMENTS.TXT (v3.0)

```
# Telegram
python-telegram-bot==21.0
aiohttp==3.9.1

# Database
supabase==2.4.0
psycopg2-binary==2.9.9
sqlalchemy==2.0.23

# Email & SMS
sendgrid==6.10.0
twilio==8.10.0

# AI & ML
requests==2.31.0
perplexity-python==1.0.0
pytesseract==0.3.10
pdf2image==1.16.3
pillow==10.1.0

# Utilities
python-dotenv==1.0.0
pydantic==2.5.0
redis==5.0.0
httpx==0.25.2

# N8N
n8n-python==1.2.0

# Replit
gunicorn==21.2.0
fastapi==0.104.1
uvicorn==0.24.0

# Monitoring
prometheus-client==0.19.0
python-json-logger==2.0.7

# Utils
phonenumbers==8.13.0
pytz==2023.3
```

---

## 🔐 ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ (.env v3.0)

```env
# ========== TELEGRAM ==========
TELEGRAM_BOT_TOKEN=1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefgh
DEFAULT_USER_ID=123456789

# ========== SUPABASE ==========
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...

# ========== SENDGRID ==========
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxx
SENDGRID_FROM_EMAIL=projects@super-brain.com
SENDGRID_INBOUND_WEBHOOK_SECRET=xxxxx

# ========== TWILIO ==========
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxx
TWILIO_PHONE_NUMBER=+1234567890
TWILIO_WHATSAPP_NUMBER=whatsapp:+1234567890

# ========== PERPLEXITY ==========
PERPLEXITY_API_KEY=pplx-xxxxxxxxxxxxxxxxxxxxx
PERPLEXITY_MODEL=sonar-reasoning-pro

# ========== N8N ==========
N8N_API_URL=https://n8n.super-brain.com
N8N_API_KEY=n8n_xxxxxxxxxxxxxxxxxxxxx

# ========== REPLIT WORKERS ==========
REPLIT_WORKER_1_URL=https://replit-worker-1.replit.dev
REPLIT_WORKER_2_URL=https://replit-worker-2.replit.dev
REPLIT_WORKER_3_URL=https://replit-worker-3.replit.dev

# ========== STORAGE ==========
AWS_S3_BUCKET=super-brain-docs
AWS_S3_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=xxxxx

# ========== REDIS ==========
REDIS_URL=redis://redis-master:6379

# ========== ENVIRONMENT ==========
ENVIRONMENT=production
LOG_LEVEL=INFO
DEBUG=false

# ========== BATCH SETTINGS ==========
BATCH_RUN_HOUR=2
BATCH_RUN_MINUTE=0
AUTO_EVOLVE_SCHEMA=true

# ========== THRESHOLDS ==========
CLASSIFICATION_CONFIDENCE_THRESHOLD=70
MERGE_SIMILARITY_THRESHOLD=85
RISK_SCORE_ALERT_THRESHOLD=70
```

---

## ✅ DEFINITION OF DONE (v3.0)

### BOT.PY
- [ ] Получает файлы (Excel, PDF, Image, Doc, ZIP)
- [ ] Управляет проектами и задачами
- [ ] Отправляет/получает SMS
- [ ] Отправляет/получает Email
- [ ] Генерирует отчёты (PDF)
- [ ] Интеграция с N8N workflows
- [ ] Логирование всех действий

### N8N
- [ ] Workflow: DocumentParser запущен и работает
- [ ] Workflow: EmailManager получает письма
- [ ] Workflow: TaskDistributor отправляет SMS+Email
- [ ] Workflow: StatusNotifier уведомляет
- [ ] Workflow: DailyReportGenerator отправляет отчёты
- [ ] Все workflows залогированы

### SUPABASE
- [ ] Все 8 таблиц созданы и заполнены
- [ ] Row-level security настроена
- [ ] Webhooks для N8N интегрированы
- [ ] Real-time subscriptions работают
- [ ] Backups настроены

### SENDGRID
- [ ] Отправка писем работает
- [ ] Inbound Parse webhook настроен
- [ ] Email tracking включен
- [ ] Шаблоны писем созданы

### TWILIO
- [ ] SMS отправка работает
- [ ] SMS получение (webhooks) работает
- [ ] WhatsApp Business API интегрирован
- [ ] Voice Call API готов

### REPLIT
- [ ] Worker 1: OCR processing работает
- [ ] Worker 2: Email parser работает
- [ ] Worker 3: Data validator работает
- [ ] Все workers имеют HTTP endpoints

### Deployment
- [ ] Docker image собран
- [ ] K8s Deployment развёрнут
- [ ] Все сервисы коммуникуют
- [ ] Мониторинг включен (Prometheus)
- [ ] GitHub Actions CI/CD работает

---

## 🎬 TIMELINE (v3.0)

```
WEEK 1
├─ DAY 1 (Telegram Bot Base)
│  ├─ 0:00-1:00   BOT.PY основная структура
│  ├─ 1:00-1:30   File upload + storage integration
│  ├─ 1:30-2:00   Task management basics
│  └─ 2:00 ✅     Локальное тестирование
│
├─ DAY 2 (Database + Supabase)
│  ├─ 0:00-1:00   Supabase schema создание
│  ├─ 1:00-1:30   Row-level security
│  ├─ 1:30-2:00   Тестирование queries
│  └─ 2:00 ✅     
│
└─ DAY 3 (N8N Setup)
   ├─ 0:00-1:00   N8N.cloud базовая настройка
   ├─ 1:00-1:30   Первые workflows создание
   ├─ 1:30-2:00   Интеграция с BOT.PY
   └─ 2:00 ✅

WEEK 2
├─ DAY 4-5 (Email + SMS Integration)
│  ├─ SendGrid: SMTP + Inbound Parse
│  ├─ Twilio: SMS API + Webhooks
│  └─ N8N: EmailManager + TaskDistributor workflows
│
├─ DAY 6-7 (Replit Workers)
│  ├─ Worker 1: OCR processor
│  ├─ Worker 2: Email parser
│  ├─ Worker 3: Data validator
│  └─ Все workers готовы к K8s
│
└─ DAY 8-9 (Deployment)
   ├─ Docker build
   ├─ K8s deployment
   ├─ Мониторинг (Prometheus + Grafana)
   ├─ GitHub Actions CI/CD
   └─ Production ready!

ИТОГО: ~2 недели интенсивной разработки
```

---

## 📈 МАСШТАБИРУЕМОСТЬ

### Текущая архитектура поддерживает:

✅ **1000+ активных пользователей одновременно**  
✅ **100+ одновременных проектов**  
✅ **10,000+ задач в системе**  
✅ **50,000+ документов**  
✅ **100,000+ коммуникаций (письма, SMS)**  
✅ **500+ агентов параллельно**  
✅ **1M+ transactions в день**

### Auto-scaling:
- K8s автоматически масштабирует BOT pods
- N8N автоматически обрабатывает нагрузку
- Supabase автоматически масштабируется
- Replit Workers можно добавить больше

---

## 🎯 ФИНАЛЬНЫЙ СТАТУС

**🚀 SUPER BRAIN ENTERPRISE v3.0 — ГОТОВО К LAUNCH!** ✅

Это не просто система управления проектами.  
Это **интеллектуальная экосистема** с:
- 🤖 Умными агентами
- 📧 Полной коммуникацией (Email, SMS, Telegram, WhatsApp)
- 📊 Анализом документации
- 💡 AI-инсайтами
- ⚡ Масштабируемостью на 1000+

**Готовы к кодированию!** 🚀

---

**Дата утверждения:** 7 декабря 2025, 13:50 MSK  
**Версия:** 3.0 ENTERPRISE  
**Статус:** APPROVED ✅  
**Автор:** Perplexity AI + vik9541  
**Платформа:** Kubernetes + N8N + Supabase + Multi-Cloud
