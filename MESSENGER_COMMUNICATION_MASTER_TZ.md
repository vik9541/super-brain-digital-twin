# 📱 SUPER BRAIN: Мастер ТЗ по общению с человеком через месенджеры

**Дата:** 12 декабря 2025, 13:56 MSK  
**Версия:** v2.0 (Комплексное издание)  
**Статус:** 🟢 PRODUCTION READY  
**Архитектура:** Multi-Channel Intelligent Communication Hub  
**Тип документа:** Главное ТЗ для реализации

---

## 📋 СОДЕРЖАНИЕ

- [Обзор системы](#обзор-системы)
- [Архитектура коммуникации](#архитектура-коммуникации)
- [Цели и приоритеты](#цели-и-приоритеты)
- [Месенджеры и интеграции](#месенджеры-и-интеграции)
- [Стек технологий](#стек-технологий)
- [Разделение задач (TASK-COMM)](#разделение-задач-task-comm)
- [План реализации](#план-реализации)
- [Процессы обучения от общения](#процессы-обучения-от-общения)
- [API Endpoints для коммуникации](#api-endpoints-для-коммуникации)
- [Примеры реальных диалогов](#примеры-реальных-диалогов)

---

## 🎯 Обзор системы

### Главная идея

**Super Brain должен общаться с тобой ВЕЗДЕ, ВСЕГДА, КАК ЧЕЛОВЕК.**

Не просто обрабатывать файлы, но:
- 💬 Задавать уточняющие вопросы (Clarification Questions)
- 🤔 Предлагать действия (Suggestions)
- 📣 Отправлять уведомления (Notifications)
- 📊 Поделиться insights (Intelligence Reports)
- 🔔 Напоминать о дедлайнах (Reminders)
- 💡 Давать рекомендации (Recommendations)

**Где?**
- 📱 Telegram (основной канал)
- 💬 WhatsApp (вторичный канал)
- 📧 Email (официальный канал)
- 🔔 Web Push Notifications (реал-тайм)
- 📲 Slack / Discord (корпоративный канал)

### Разница между v4.1 и v5.0

| Аспект | v4.1 | v5.0 |
|--------|------|------|
| **Отправка** | Только от пользователя (file upload) | Двусторонняя коммуникация |
| **Инициатива** | Реактивная (ждёт действие) | Проактивная (сам предлагает) |
| **Языки** | Только русский | Многоязычная система |
| **Контекст** | Файл + текущая сессия | ВСЯ история + память |
| **Персонализация** | Базовая | Глубокая (учит стиль общения) |
| **Каналы** | Telegram only | Multi-channel hub |

---

## 🏗️ Архитектура коммуникации

### Граф потока данных

```
┌─────────────────────────────────────────────┐
│      👤 ЧЕЛОВЕК                            │
│  (Никита, Мария, Иван и т.д.)             │
└────────────┬────────────────────────────────┘
             │
    ┌────────┴────────┬──────────┬──────────┐
    │                 │          │          │
    ▼                 ▼          ▼          ▼
┌─────────┐      ┌─────────┐ ┌──────┐  ┌───────┐
│Telegram │      │WhatsApp │ │Email │  │ Slack │
│ (BOT)   │      │ (API)   │ │(SMTP)│  │(Hook) │
└────┬────┘      └────┬────┘ └──┬───┘  └───┬───┘
     │                │         │          │
     └────────────────┼─────────┼──────────┘
                      ▼
        ┌─────────────────────────────┐
        │  MESSAGE INGESTION LAYER    │
        │  - Normalize all formats    │
        │  - Extract metadata         │
        │  - Create audit trail       │
        └────────────┬────────────────┘
                     ▼
        ┌─────────────────────────────┐
        │  AI AGENT LAYER             │
        │  - Primary Analyzer         │
        │  - Organizer                │
        │  - Master Teacher           │
        │  - Response Generator       │
        └────────────┬────────────────┘
                     ▼
        ┌─────────────────────────────┐
        │  CONTEXT & MEMORY LAYER     │
        │  - User memory              │
        │  - Conversation history     │
        │  - Knowledge graph          │
        │  - Vector embeddings        │
        └────────────┬────────────────┘
                     ▼
        ┌─────────────────────────────┐
        │  RESPONSE GENERATION        │
        │  - Generate message         │
        │  - Personalization          │
        │  - Tone matching            │
        │  - Safety checks            │
        └────────────┬────────────────┘
                     ▼
        ┌─────────────────────────────┐
        │  MESSAGE DELIVERY LAYER     │
        │  - Prioritize channels      │
        │  - Format for each channel  │
        │  - Track delivery           │
        │  - Log responses            │
        └────────────┬────────────────┘
                     │
    ┌────────────────┼──────────┬──────────┐
    │                │          │          │
    ▼                ▼          ▼          ▼
┌─────────┐      ┌─────────┐ ┌──────┐  ┌───────┐
│Telegram │      │WhatsApp │ │Email │  │ Slack │
└─────────┘      └─────────┘ └──────┘  └───────┘
    │                │          │          │
    └────────────────┼──────────┼──────────┘
                     ▼
        ┌─────────────────────────────┐
        │      👤 ЧЕЛОВЕК             │
        │   (получает ответ)          │
        └─────────────────────────────┘
```

### Состояния общения

```
                    ┌──────────────┐
                    │   IDLE       │ (ждем сообщение)
                    └───────┬──────┘
                            │ Сообщение получено
                            ▼
                    ┌──────────────┐
                    │ INGESTING    │ (парсим сообщение)
                    └───────┬──────┘
                            │
                            ▼
                    ┌──────────────┐
        ┌──────────►│ ANALYZING    │ (анализируем контент)
        │           └───────┬──────┘
        │                   │
        │                   ▼
        │           ┌──────────────────┐
        │           │ CONTEXT_LOOKUP   │ (ищем контекст)
        │           └───────┬──────────┘
        │                   │
        │                   ▼
        │           ┌──────────────────┐
        │           │ CLARIFICATION?   │ (нужны уточнения?)
        │           └───┬────────────┬──┘
        │         YES   │            │ NO
        └───────────────┘            ▼
                        ┌──────────────────────┐
                        │ GENERATE_RESPONSE    │
                        └───────┬──────────────┘
                                │
                                ▼
                        ┌──────────────────────┐
                        │ PERSONALIZE_TONE     │
                        └───────┬──────────────┘
                                │
                                ▼
                        ┌──────────────────────┐
                        │ SAFETY_CHECK         │
                        └───────┬──────────────┘
                                │
                                ▼
                        ┌──────────────────────┐
                        │ SELECT_CHANNELS      │
                        └───────┬──────────────┘
                                │
                                ▼
                        ┌──────────────────────┐
                        │ DELIVER              │
                        └───────┬──────────────┘
                                │
                                ▼
                        ┌──────────────────────┐
                        │ LOG_INTERACTION      │
                        └───────┬──────────────┘
                                │
                                ▼
                        ┌──────────────────────┐
                        │ LEARN_FROM_RESPONSE  │
                        └───────┬──────────────┘
                                │
                                ▼
                    ┌──────────────────────┐
                    │ IDLE (ждём ответ)   │
                    └──────────────────────┘
```

---

## 🎯 Цели и приоритеты

### Приоритет 1: Основная коммуникация (TASK-COMM-001 to 010)
- ✅ Двусторонний диалог в Telegram
- ✅ Уточняющие вопросы (Clarification Questions)
- ✅ История разговоров (Conversation History)
- ✅ Контекстная память (Context Memory)
- ✅ Personalized responses

### Приоритет 2: Многоканальность (TASK-COMM-020 to 030)
- WhatsApp интеграция
- Email интеграция
- Slack интеграция
- Push-уведомления
- Channel selection logic

### Приоритет 3: Умная инициатива (TASK-COMM-040 to 050)
- Проактивные уведомления
- Автоматические напоминания
- Smart suggestions
- Deadline alerts
- Pattern-based recommendations

### Приоритет 4: Обучение от общения (TASK-COMM-060 to 070)
- Tone learning (учимся стилю общения)
- Preference learning (любимые каналы)
- Response pattern learning
- Context enrichment
- Personalization deepening

---

## 📱 Месенджеры и интеграции

### 1️⃣ TELEGRAM (Основной канал)

**Статус:** 🟢 СУЩЕСТВУЕТ (но нужно переписать для v5.0)

**Текущее:**
- @digital_twin_bot (должен быть зарегистрирован)
- Receives files from users
- Sends basic analysis
- Limited conversation capability

**Требуется (v5.0):**
```python
# TASK-COMM-001: Двусторонний Telegram Bot

1. Обработка входящих сообщений:
   - /start → приветствие + онбординг
   - /help → справка по командам
   - /status → статус системы
   - /memory → показать мою память о тебе
   - /export → экспорт данных
   - Любой текст → анализ и ответ
   - Любой файл → документ анализ
   - Голосовое → transcription + анализ
   - Фото → vision API анализ
   - Стикер → попытка распознатьIntent

2. Отправка от бота:
   - Уточняющие вопросы (Clarifications)
   - Подтверждения (Confirmations)
   - Результаты анализа (Analysis Results)
   - Напоминания (Reminders)
   - Notifications (важные обновления)
   - Daily/Weekly reports
   - Suggestions (предложения)

3. Расширенные функции:
   - Inline кнопки для быстрых ответов
   - Inline поиск по памяти
   - Message edits (бот может отредактировать сообщение)
   - Media groups (группы фото/видео)
   - Scheduled messages (отправить в будущем)
   - Message reactions (реагировать на сообщения)

4. Хранение:
   - Все сообщения в telegram_messages таблице
   - Связь с conversation_id
   - Metadata: user_id, timestamp, channel, intent

Код основы:
class TelegramCommunicationHandler:
    async def handle_incoming_message(self, message):
        # Parse сообщение
        content, metadata = await self.parse_message(message)
        
        # Анализ с контекстом
        analysis = await self.analyzer.analyze_with_context(
            content=content,
            user_id=metadata.user_id,
            conversation_history=await self.get_conversation_history(metadata.user_id)
        )
        
        # Нужны ли уточнения?
        if analysis.confidence < 0.8:
            questions = await self.generate_clarification_questions(analysis)
            await self.send_message(
                chat_id=metadata.chat_id,
                text="Мне нужно уточнить. Вопросы:",
                keyboard=self.create_inline_keyboard(questions)
            )
        else:
            # Сгенерировать ответ
            response = await self.response_generator.generate(
                analysis=analysis,
                tone=await self.get_user_tone_preference(metadata.user_id),
                context=await self.get_full_context(metadata.user_id)
            )
            
            # Отправить
            await self.send_message(
                chat_id=metadata.chat_id,
                text=response,
                media=await self.prepare_media(analysis)
            )
            
            # Залогировать
            await self.log_interaction(
                user_id=metadata.user_id,
                incoming=content,
                outgoing=response,
                confidence=analysis.confidence
            )
```

---

### 2️⃣ WHATSAPP (Вторичный канал)

**Статус:** 🔴 НЕ РЕАЛИЗОВАНО (TASK-COMM-020)

**Интеграция:** Twilio WhatsApp API

**Требуется:**
```
1. Account настройка:
   - Twilio account (создать если нет)
   - Phone number (купить Twilio number)
   - White-label setup (твой номер)
   - Template approval (сообщения)

2. Инcomings:
   - Text messages
   - Images
   - Documents
   - Voice notes
   - Location

3. Outgoings:
   - Text replies
   - Templates (pre-approved)
   - Media (images, documents)
   - Buttons/Quick replies
   - Interactive lists

4. Разница от Telegram:
   - Формат сообщений уже (WhatsApp UX)
   - Меньше функций (нет inline)
   - Но лучше доставляемость (SMS fallback)
   - Шифрование E2E

5. Implementation:
   - Webhook для входящих
   - Queue для исходящих (Celery)
   - Template management
   - Conversation state management

Тек: Twilio SDK + FastAPI webhook
```

---

### 3️⃣ EMAIL (Официальный канал)

**Статус:** 🔴 НЕ РЕАЛИЗОВАНО (TASK-COMM-030)

**Интеграция:** SendGrid API

**Требуется:**
```
1. Входящие (Email parsing):
   - Parse incoming emails
   - Extract attachments
   - Classify intent (question, alert, report request)
   - Thread tracking (threading conversations)

2. Исходящие (Email sending):
   - Daily/weekly digests
   - Important alerts
   - Report delivery
   - Document analysis results
   - Scheduled reports

3. Features:
   - Pretty HTML templates
   - Unsubscribe tracking
   - Open/click tracking (optional)
   - Attachment support
   - Signature management

4. Integration:
   - APScheduler для scheduled emails
   - Jinja2 для templates
   - SendGrid batch API
   - Email archive в database

Тек: SendGrid SDK + Jinja2 templates
```

---

### 4️⃣ SLACK (Корпоративный канал)

**Статус:** 🔴 НЕ РЕАЛИЗОВАНО (TASK-COMM-040)

**Интеграция:** Slack SDK (bolt-python)

**Требуется:**
```
1. Bot Setup:
   - Create Slack App
   - OAuth token
   - Event subscriptions
   - Scopes configuration

2. Interactions:
   - Direct messages to bot
   - Channel mentions (@digital_twin)
   - Slash commands (/analyze, /search, /report)
   - Interactive buttons
   - Modal forms (dialogs)

3. Features:
   - Thread replies (conversations)
   - Reactions (acknowledge)
   - File sharing
   - User mentions (@someone)
   - Channel announcements

4. Integration:
   - Socket mode for local dev
   - Events: message, app_mention, file_shared
   - Actions: button_click, modal_submission

Тек: slack-bolt SDK
```

---

### 5️⃣ PUSH NOTIFICATIONS (Веб и мобильное)

**Статус:** 🔴 НЕ РЕАЛИЗОВАНО (TASK-COMM-050)

**Интеграция:** Firebase Cloud Messaging (FCM) / OneSignal

**Требуется:**
```
1. Типы уведомлений:
   - Urgent alerts (немедленно)
   - Important updates (в течение часа)
   - Reminders (в запланированное время)
   - Digest (раз в день)
   - New files (опционально)

2. Где показывается:
   - Web browser (при открытом сайте)
   - Mobile app (iOS/Android)
   - Desktop (Windows/Mac)
   - Smart watch (если есть)

3. Customization:
   - Silent notifications (only badge)
   - Sound selection
   - Vibration patterns
   - Do not disturb schedule
   - Channel priorities

Тек: FCM API
```

---

## 💻 Стек технологий

### Messaging Libraries
```python
# Telegram
python-telegram-bot==21.0
aiogram==3.0.0

# WhatsApp
twilio==8.10.0

# Email
sendgrid==6.11.0
premailer==3.15.0
jinja2==3.1.2

# Slack
slack-bolt==1.18.0

# Push
firebase-admin==6.5.0

# General
aiohttp==3.9.1
celery==5.3.4
redis==5.0.1
pydantic==2.5.0
```

### Database Tables (Supabase)
```sql
-- Основные таблицы разговоров
CREATE TABLE messenger_conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR NOT NULL,
    channel VARCHAR NOT NULL, -- telegram, whatsapp, email, slack
    channel_user_id VARCHAR NOT NULL, -- identifier в этом каналле
    created_at TIMESTAMP DEFAULT NOW(),
    last_message_at TIMESTAMP,
    summary TEXT, -- краткое резюме разговора
    tone_detected VARCHAR, -- formal/casual/urgent
    user_preference_channels TEXT[], -- предпочтительные каналы
    metadata JSONB
);

-- Сообщения
CREATE TABLE messenger_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES messenger_conversations(id),
    direction VARCHAR NOT NULL, -- incoming/outgoing
    channel VARCHAR NOT NULL,
    content TEXT NOT NULL,
    content_type VARCHAR, -- text/image/document/voice
    media_url VARCHAR,
    sender VARCHAR, -- bot/user
    timestamp TIMESTAMP DEFAULT NOW(),
    confidence_score FLOAT,
    intent VARCHAR, -- question/statement/request/feedback
    tags TEXT[],
    metadata JSONB
);

-- История ответов
CREATE TABLE messenger_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID REFERENCES messenger_messages(id),
    response_text TEXT NOT NULL,
    response_type VARCHAR, -- direct_answer/clarification/confirmation
    generated_at TIMESTAMP DEFAULT NOW(),
    delivery_channels VARCHAR[],
    delivery_status JSONB, -- {telegram: delivered, email: failed}
    tone_applied VARCHAR,
    personalization_level INT, -- 1-5 (how personalized)
    user_satisfaction INT -- 1-5 (if user reacted)
);

-- Пользовательские настройки коммуникации
CREATE TABLE messenger_user_preferences (
    user_id VARCHAR PRIMARY KEY,
    primary_channel VARCHAR, -- telegram/whatsapp/email/slack
    backup_channels VARCHAR[],
    preferred_tone VARCHAR, -- formal/casual/mixed
    quiet_hours JSONB, -- {start: "22:00", end: "08:00"}
    urgency_threshold VARCHAR, -- low/medium/high
    notification_frequency VARCHAR, -- real_time/hourly/daily
    language VARCHAR,
    timezone VARCHAR,
    do_not_disturb_schedule JSONB,
    metadata JSONB
);

-- Tone и personalization learning
CREATE TABLE messenger_user_tone_learning (
    user_id VARCHAR NOT NULL,
    sample_text TEXT NOT NULL,
    detected_tone VARCHAR,
    confidence FLOAT,
    sample_source VARCHAR, -- own_message/feedback
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 📊 Разделение задач (TASK-COMM)

### PHASE 1: TELEGRAM ENHANCEMENT (TASK-COMM-001 to 010)

| Task ID | Название | Описание | Зависит от | Deadline |
|---------|----------|----------|------------|----------|
| **TASK-COMM-001** | Двусторонний диалог | Реагировать на текстовые сообщения | - | 15 дек |
| **TASK-COMM-002** | Clarification Questions | Задавать уточняющие вопросы | COMM-001 | 17 дек |
| **TASK-COMM-003** | Conversation Memory | Помнить историю разговоров | COMM-002 | 18 дек |
| **TASK-COMM-004** | Context Injection | Использовать контекст при ответах | COMM-003 | 20 дек |
| **TASK-COMM-005** | Tone Detection | Распознавать стиль общения | COMM-001 | 17 дек |
| **TASK-COMM-006** | Personalized Responses | Адаптировать ответы под стиль | COMM-005 | 20 дек |
| **TASK-COMM-007** | Rich Media Support | Поддержка фото, видео, документов | COMM-001 | 18 дек |
| **TASK-COMM-008** | Voice Messages | Поддержка голосовых сообщений | COMM-007 | 19 дек |
| **TASK-COMM-009** | Inline Keyboards | Быстрые ответы через кнопки | COMM-002 | 18 дек |
| **TASK-COMM-010** | Response Logging | Логировать все взаимодействия | COMM-001 | 16 дек |

### PHASE 2: MULTI-CHANNEL (TASK-COMM-020 to 050)

| Task ID | Название | Описание | Статус | Deadline |
|---------|----------|----------|--------|----------|
| **TASK-COMM-020** | WhatsApp API | Интеграция Twilio WhatsApp | PLANNED | 25 дек |
| **TASK-COMM-021** | WhatsApp Message Parsing | Обработка входящих WA | PLANNED | 26 дек |
| **TASK-COMM-022** | WhatsApp Templates | Одобренные шаблоны сообщений | PLANNED | 27 дек |
| **TASK-COMM-030** | Email Integration | SendGrid API | PLANNED | 2 янв |
| **TASK-COMM-031** | Email Templates | HTML шаблоны | PLANNED | 3 янв |
| **TASK-COMM-032** | Scheduled Emails | Отправка по расписанию | PLANNED | 4 янв |
| **TASK-COMM-040** | Slack Bot | Slack SDK интеграция | PLANNED | 5 янв |
| **TASK-COMM-041** | Slack Slash Commands | /analyze, /search и т.д. | PLANNED | 6 янв |
| **TASK-COMM-050** | Push Notifications | FCM / OneSignal | PLANNED | 10 янв |

### PHASE 3: SMART PROACTIVITY (TASK-COMM-060 to 080)

| Task ID | Название | Описание | Статус | Deadline |
|---------|----------|----------|--------|----------|
| **TASK-COMM-060** | Proactive Alerts | Система проактивных уведомлений | PLANNED | 12 янв |
| **TASK-COMM-061** | Deadline Reminders | Напоминания о дедлайнах | PLANNED | 13 янв |
| **TASK-COMM-062** | Daily Digest | Ежедневные выжимки | PLANNED | 14 янв |
| **TASK-COMM-070** | Smart Suggestions | Рекомендации на основе паттернов | PLANNED | 15 янв |
| **TASK-COMM-071** | Pattern Recognition | Распознавание паттернов в общении | PLANNED | 16 янв |
| **TASK-COMM-080** | Learning from Responses | Обучение от ответов пользователя | PLANNED | 18 янв |

---

## 🚀 План реализации

### НЕДЕЛЯ 1 (12-18 дек): Telegram Basics

```
ПН 12 дек:
  ✅ TASK-COMM-001: Двусторонний диалог
    └─ Telegram bot обрабатывает текстовые сообщения
    └─ Отправляет базовые ответы
    └─ Сохраняет в БД

ВТ 13 дек:
  ✅ TASK-COMM-010: Response Logging
    └─ Все сообщения логируются
    └─ Metadata сохраняется
  
  ✅ TASK-COMM-005: Tone Detection
    └─ Распознаем стиль (formal/casual/urgent)

СР 14 дек:
  ✅ TASK-COMM-002: Clarification Questions
    └─ Бот задает уточняющие вопросы
    └─ Inline кнопки для быстрых ответов
  
  ✅ TASK-COMM-009: Inline Keyboards
    └─ Добавляем кнопки для навигации

ЧТ 15 дек:
  ✅ TASK-COMM-003: Conversation Memory
    └─ Сохраняем историю разговоров
    └─ Загружаем при новом сообщении
  
  ✅ TASK-COMM-007: Rich Media Support
    └─ Поддержка фото, документов

ПТ 16 дек:
  ✅ TASK-COMM-004: Context Injection
    └─ Используем контекст из памяти
    └─ Улучшенные ответы
  
  ✅ TASK-COMM-006: Personalized Responses
    └─ Адаптируем стиль к пользователю

СБ 17 дек:
  ✅ TASK-COMM-008: Voice Messages
    └─ Transcription голосовых сообщений
    └─ Обработка как обычного текста

ВС 18 дек:
  📊 REVIEW PHASE 1
    └─ Тестирование всех функций
    └─ Исправление ошибок
    └─ Подготовка к Phase 2
```

### НЕДЕЛЯ 2-3 (19 дек - 1 янв): Multi-Channel

```
19-21 дек: WhatsApp
  ✅ TASK-COMM-020: Twilio WhatsApp интеграция
  ✅ TASK-COMM-021: Message parsing
  ✅ TASK-COMM-022: Templates

22-24 дек: Email
  ✅ TASK-COMM-030: SendGrid API
  ✅ TASK-COMM-031: Email templates
  ✅ TASK-COMM-032: Scheduled emails

25-27 дек: Slack
  ✅ TASK-COMM-040: Slack bot
  ✅ TASK-COMM-041: Slash commands

28-31 дек: Push & Integration
  ✅ TASK-COMM-050: FCM notifications
  ✅ Channel selection logic
  ✅ Cross-channel consistency
```

### НЕДЕЛЯ 4 (2-8 янв): Smart Proactivity

```
2-4 янв: Proactive System
  ✅ TASK-COMM-060: Alerts
  ✅ TASK-COMM-061: Reminders
  ✅ TASK-COMM-062: Daily digest

5-6 янв: Learning
  ✅ TASK-COMM-070: Smart suggestions
  ✅ TASK-COMM-071: Pattern recognition
  ✅ TASK-COMM-080: Learning from responses

7-8 янв: Optimization
  ✅ Performance tuning
  ✅ Error handling
  ✅ Documentation
```

---

## 🧠 Процессы обучения от общения

### Что система учит из диалогов

```
1. TONE LEARNING
   - Анализируем стиль сообщений пользователя
   - Извлекаем характеристики (formal/casual/urgent/humorous)
   - Обновляем user_tone_learning таблицу
   - Используем при генерации ответов
   
   Пример:
   User: "Ок, буду ждать"
   → Tone: casual/patient
   
   Bot (next time):
   "Понимаю, буду быстрее!" (не formal)

2. CHANNEL PREFERENCE LEARNING
   - Отслеживаем, какой канал пользователь использует
   - Какой канал читает ответы (не бросает)
   - Выбираем более продуктивные каналы
   
   Пример:
   User reads Telegram → send there
   User ignores Email → reduce email

3. TIME ZONE & QUIET HOURS LEARNING
   - Анализируем, когда пользователь активен
   - Когда не активен (спит?)
   - Избегаем уведомлений в quiet hours
   
   Пример:
   User never active 23:00-08:00
   → Don't send notifications then

4. RESPONSE TIME LEARNING
   - Сколько времени пользователь обычно отвечает
   - Если долго не отвечает → может пропустить
   - Если быстро отвечает → может ответить сейчас
   
   Пример:
   User typically replies within 10 minutes
   → If no reply in 15 min, add reminder

5. PREFERENCE LEARNING
   - Какая информация интересна
   - Какие типы уведомлений нравятся
   - Какая длина сообщений предпочтительна
   
   Пример:
   User replies to detailed reports
   User ignores one-liners
   → Make reports longer

6. QUESTION-ANSWER PATTERN LEARNING
   - Какие типы вопросов задает
   - Какие ответы полезны
   - Какие уточнения нужны
   
   Пример:
   User often asks about "deadlines"
   → Start checking deadlines proactively

7. DOMAIN-SPECIFIC LANGUAGE LEARNING
   - Какие термины использует
   - Какие аббревиатуры любит
   - Какой язык смеси (code-mixing)
   
   Пример:
   User writes: "Надо ASAP сделать MOS-01"
   → Bot learns: ASAP = urgent, MOS-01 = project
   → Answer using same terms

8. CONTEXT PATTERN LEARNING
   - Когда обычно нужна какая информация
   - Какие файлы идут вместе
   - Какие люди работают вместе
   
   Пример:
   User always asks about budget when mentioning "project"
   → Proactively share budget info
```

### Как это хранится

```python
# User Communication Profile (обновляется ежедневно)
{
    user_id: "user_123",
    
    # Tone detection
    tone_profile: {
        primary: "casual",
        secondary: "urgent",
        confidence: 0.92,
        samples: 45,
        learned_from: ["last 30 days of messages"]
    },
    
    # Channel preferences
    channels: {
        telegram: {
            engagement: 0.95,  # reads/replies ratio
            response_time_minutes: 8.3,
            preferred_for: ["urgent", "quick_updates"],
            avg_messages_per_day: 12
        },
        email: {
            engagement: 0.4,
            response_time_minutes: 240,
            preferred_for: ["reports", "digests"],
            avg_messages_per_day: 0.5
        }
    },
    
    # Time zones & activity
    timezone: "Europe/Moscow",
    active_hours: [[8, 0], [23, 0]],
    quiet_hours: [[23, 0], [8, 0]],
    avg_message_length: 45,  # characters
    
    # Preferences
    preferences: {
        message_length: "medium",
        detail_level: "high",
        use_emojis: True,
        use_humor: True,
        formal_topics: ["finance", "contracts"]
    },
    
    # Domain knowledge
    known_projects: ["MOS-01", "MOS-02"],
    known_people: ["Ivan", "Maria"],
    known_acronyms: {"ASAP": "urgent", "KISS": "simple"},
    
    # Learning metrics
    learning_level: 0.82,  # 0-1, how well we know this user
    last_updated: "2025-12-12T13:30:00Z",
    samples_this_week: 87
}
```

---

## 📡 API Endpoints для коммуникации

### REST API

```http
# Получить историю разговора
GET /api/v1/messenger/conversations/{conversation_id}
Response: {
    id: uuid,
    channel: "telegram",
    messages: [{...}, {...}],
    tone: "casual",
    summary: "..."
}

# Отправить сообщение
POST /api/v1/messenger/send
Body: {
    user_id: "user_123",
    text: "Hello",
    target_channels: ["telegram"],
    urgency: "high",
    personalize: true
}

# Получить user communication profile
GET /api/v1/messenger/user/{user_id}/profile
Response: {
    tone_profile: {...},
    channel_preferences: {...},
    learning_level: 0.82
}

# Обновить preferences
PUT /api/v1/messenger/user/{user_id}/preferences
Body: {
    primary_channel: "telegram",
    quiet_hours: {start: "23:00", end: "08:00"}
}

# Get learning insights
GET /api/v1/messenger/user/{user_id}/insights
Response: {
    preferred_tone: "casual",
    best_communication_time: "10:00",
    response_rate_by_channel: {telegram: 0.95, email: 0.4},
    recommendations: ["Use Telegram for urgent", "Email for digests"]
}
```

### WebSocket (Real-time)

```javascript
// Connect to real-time messages
ws://api.97v.ru/ws/messenger/{user_id}

// Incoming message
{
    type: "message_received",
    from: "telegram",
    text: "User message",
    timestamp: 1234567890
}

// Bot typing
{
    type: "typing",
    channel: "telegram",
    duration_ms: 1500
}

// Bot response
{
    type: "message_sent",
    text: "Bot response",
    channels: ["telegram"],
    personalization_applied: true
}
```

---

## 💬 Примеры реальных диалогов

### Сценарий 1: Анализ документа с уточнениями

```
12:34 USER (Telegram): [Загрузил PDF контракт]

12:34 BOT: 
  Получил контракт (PDF, 150 KB). Анализирую...
  
12:35 BOT:
  📄 Контракт с компанией XYZ
  📅 Срок: 2026-01-15
  💰 Сумма: не указана
  👥 Люди: Ivan Petrov, Maria Sidorova
  
  Мне нужны уточнения:
  1️⃣ Это рабочий договор?
  2️⃣ Нужно ли создать напоминание?
  
  [ДА] [НЕТ] [ПОКАЗАТЬ ПОЛНЫЙ АНАЛИЗ]

12:36 USER: [Нажал ДА]

12:37 BOT:
  ✅ Понял! Это рабочий договор.
  
  На какую дату создать напоминание?
  [30 дней до] [2 недели до] [1 неделю до] [Вручную]

12:37 USER: [Нажал "2 недели до"]

12:37 BOT:
  ✅ Сохранено!
  
  📌 Напоминание: 1 января 2026
  🔗 Связано с проектом: MOS-01
  👥 Участники: Ivan, Maria
  
  Что дальше?
  [📊 Подробный анализ] [💾 Сохранить] [🔗 Связать]  
```

### Сценарий 2: Проактивное напоминание

```
09:00 SYSTEM (Daily check):
  User hasn't uploaded files in 3 days
  Next deadline approaching in 2 days
  
09:15 BOT (Telegram):
  🔔 Напоминание: Дедлайн проекта MOS-01 через 2 дня!
  
  Последние документы:
  📄 contract.pdf (5 дней назад)
  📊 budget.xlsx (7 дней назад)
  
  Нужны ли обновления?
  [📤 Загрузить файлы] [👀 Показать статус] [✅ Всё готово]

10:30 USER (WhatsApp):
  "Спасибо! Сейчас пришлю обновления"
  [Загрузил 3 файла]

10:32 BOT (WhatsApp, в ответ в том же канале):
  ✅ Получил 3 файла!
  
  Анализирую...
  
10:35 BOT (WhatsApp):
  📊 АНАЛИЗ ОБНОВЛЕНИЙ:
  
  ✅ budget.xlsx - актуально
  ⚠️  timeline.docx - требует внимания
  ❌ report.pdf - не соответствует стандарту
  
  Нужна помощь с report.pdf?
  [💬 Обсудим] [🤖 Я помогу переделать] [➡️  Дальше]
```

### Сценарий 3: Learning and Personalization

```
День 1:
  USER: "Ок, буду ждать"
  BOT: "Спасибо за терпение!"
  → Tone learning: casual + patient

День 2:
  USER: "Когда результаты?"
  BOT (remembering tone):
  "Раб

ботаю, должны быть готовы к вечеру!"
  (не formal, more familiar)

День 5:
  USER sends several messages quickly in Telegram
  ignores emails
  
  BOT (learning channels):
  → Primary: Telegram
  → Secondary: Email (low engagement)
  
  Next notification:
  Send via Telegram (not email)

День 10:
  BOT learned:
  - Tone: casual, sometimes urgent
  - Channels: Telegram 95%, Email 30%
  - Time: Most active 10:00-18:00
  - Length: Prefers medium (not too long)
  
  Profile confidence: 0.82
  
  /memory command shows:
  "Я знаю о тебе:
  📱 Предпочитаешь Telegram
  💬 Casual стиль общения
  ⏰ Активен днем
  📝 Любишь средние сообщения
  
  Level: Advanced (82%)"
```

---

## 📈 Метрики успеха

### PHASE 1 SUCCESS METRICS (Telegram)
- ✅ Response time < 2 seconds
- ✅ Message delivery rate > 99%
- ✅ Conversation continuity (remember context) > 95%
- ✅ User satisfaction > 4/5
- ✅ False positive questions < 5%

### PHASE 2 SUCCESS METRICS (Multi-Channel)
- ✅ All channels operational
- ✅ Channel selection accuracy > 90%
- ✅ Cross-channel consistency > 95%
- ✅ User adoption of new channels > 50%

### PHASE 3 SUCCESS METRICS (Smart Proactivity)
- ✅ Useful alerts > 80%
- ✅ Alert usefulness rating > 4/5
- ✅ Proactive action taken rate > 40%
- ✅ User says "I was just about to ask that" > 30%

### LEARNING SUCCESS METRICS
- ✅ Tone detection accuracy > 85%
- ✅ Channel preference prediction > 90%
- ✅ Response personalization satisfaction > 4.2/5
- ✅ "Knows me well" sentiment > 80%

---

## 🔗 GitHub Issues для реализации

Все TASK-COMM задачи должны быть созданы в GitHub Issues:

```
https://github.com/vik9541/super-brain-digital-twin/issues

Этапы:
1. Create Issue: [TASK-COMM-001] Two-way Telegram Dialogue
2. Description: Подробное описание что нужно сделать
3. Labels: task, communication, priority:high
4. Assignee: твой username
5. Milestone: v5.0-Phase1

Когда завершишь:
6. Отправь отчет через MCP
7. Issue закроется автоматически
8. CHECKLIST.md обновится
```

---

**Версия документа:** 2.0  
**Дата создания:** 12 декабря 2025, 13:56 MSK  
**Статус:** 🟢 READY FOR IMPLEMENTATION  
**Требует ревью:** ✅ APPROVED  
**GitHub Issues:** 📊 30+ TASKS  
**Total Effort:** ~500 hours  
**Timeline:** 8 weeks (mid-January 2026)  

---

> 🚀 **НАЧНЕМ С TELEGRAM! ЭТО ОСНОВНОЙ КАНАЛ.**
> 
> Phase 1 (Неделя 1): Двусторонний диалог с памятью  
> Phase 2 (Недели 2-3): Другие каналы  
> Phase 3 (Неделя 4): Smart proactivity  
>
> Первая TASK-COMM-001 должна быть закончена в пятницу 15 декабря!
