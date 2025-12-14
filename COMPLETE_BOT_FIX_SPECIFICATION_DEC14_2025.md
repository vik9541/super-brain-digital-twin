# 📘 ПОЛНАЯ СПЕЦИФИКАЦИЯ: Исправление персонального ассистента

**Дата:** 14 декабря 2025, 09:04 MSK  
**Версия:** 2.0 COMPLETE  
**Статус:** 🔴 КРИТИЧЕСКАЯ ПРОБЛЕМА  
**Цель:** Превратить поисковый бот в персонального ассистента  
**Deadline:** 14 декабря 2025, 18:00 MSK  

---

## 📋 СОДЕРЖАНИЕ

1. [Анализ проблемы](#анализ-проблемы)
2. [Архитектура решения](#архитектура-решения)
3. [База данных](#база-данных)
4. [Реализация по модулям](#реализация-по-модулям)
5. [Интеграция компонентов](#интеграция-компонентов)
6. [Тестирование](#тестирование)
7. [Развертывание](#развертывание)

---

## 🔴 АНАЛИЗ ПРОБЛЕМЫ

### Текущее поведение (НЕПРАВИЛЬНО)

```python
# Сейчас в коде (упрощенно):
async def handle_message(update, context):
    text = update.message.text
    
    # ❌ ПРОБЛЕМА: Каждое сообщение идет в Perplexity
    response = await perplexity_api.search(text)
    
    # ❌ ПРОБЛЕМА: Длинные статьи вместо коротких ответов
    await update.message.reply_text(response)  # 5000+ символов
```

**Результат:**
- ❌ "Пришел на работу в 7.50" → статья про ТК РФ и трудовое законодательство
- ❌ "Встречался с Антоном Носковым" → поиск в интернете про всех Антонов Носковых
- ❌ Фото чека → "Опишите что на фото"
- ❌ Не использует базу контактов
- ❌ Не запоминает контекст

### Требуемое поведение (ПРАВИЛЬНО)

```python
# Должно быть:
async def handle_message(update, context):
    text = update.message.text
    user_id = update.effective_user.id
    
    # ✅ 1. Определить намерение БЕЗ внешних API
    intent = intent_classifier.classify(text, has_photo=bool(update.message.photo))
    
    # ✅ 2. Выполнить соответствующее действие
    if intent == "WORK_LOG":
        response = await work_tracker.log(user_id, text)
    elif intent == "CONTACT_MENTION":
        response = await contacts_handler.process(user_id, text)
    elif intent == "RECEIPT":
        response = await receipt_analyzer.process(update.message.photo)
    # ...
    
    # ✅ 3. Короткий ответ (1-3 строки)
    await update.message.reply_text(response)
```

**Результат:**
- ✅ "Пришел на работу в 7.50" → "📍 Записано: приход в 7:50"
- ✅ "Встречался с Антоном Носковым" → поиск в СВОЕЙ базе контактов + запись в историю
- ✅ Фото чека → OCR + "🧾 Чек: Пятёрочка, 385₽"
- ✅ Ведется история по каждому контакту
- ✅ Контекст сохраняется

---

## 🏗️ АРХИТЕКТУРА РЕШЕНИЯ

### Текущая структура (что уже есть)

```
bots/personal-assistant-bot/
├── main.py                          # ✅ Есть
├── config.py                        # ✅ Есть
├── handlers/
│   ├── commands.py                  # ✅ Есть (/start, /help)
│   ├── projects_handler.py          # ✅ Есть
│   ├── tasks_handler.py             # ✅ Есть
│   ├── receipts_handler.py          # ✅ Есть
│   ├── health_handler.py            # ✅ Есть
│   ├── unified.py                   # ⚠️ Нужно исправить
│   └── dispatcher.py                # ⚠️ Нужно исправить
├── services/
│   ├── supabase_service.py          # ✅ Есть
│   ├── ocr_service.py               # ✅ Есть
│   ├── receipt_parser.py            # ✅ Есть
│   └── ...                          # ✅ Есть
```

### Что нужно добавить/исправить

```
❌ УДАЛИТЬ/ОТКЛЮЧИТЬ:
└── perplexity_integration.py (или где вызывается поиск)

✅ СОЗДАТЬ:
├── services/
│   ├── intent_classifier.py         # 🆕 Классификатор интентов
│   ├── contacts_manager.py          # 🆕 Управление контактами
│   └── context_manager.py           # 🆕 Контекст разговора
├── handlers/
│   ├── contacts_handler.py          # 🆕 Обработка упоминаний людей
│   └── work_tracker_handler.py      # 🆕 Учет рабочего времени

⚠️ ИСПРАВИТЬ:
├── handlers/unified.py              # Убрать Perplexity, добавить роутинг
└── handlers/dispatcher.py           # Использовать IntentClassifier
```

---

## 💾 БАЗА ДАННЫХ

### Существующие таблицы

```sql
-- ✅ УЖЕ ЕСТЬ:
users, projects, project_files, user_tasks, receipts, 
receipt_items, health_entries, user_preferences
```

### Новые таблицы (СОЗДАТЬ)

```sql
-- ========================================
-- ТАБЛИЦА 1: Контакты пользователя
-- ========================================
CREATE TABLE IF NOT EXISTS contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR NOT NULL,
    
    -- Основная информация
    full_name VARCHAR NOT NULL,
    first_name VARCHAR,
    last_name VARCHAR,
    middle_name VARCHAR,
    
    -- Контактные данные
    phone VARCHAR,
    email VARCHAR,
    telegram_username VARCHAR,
    
    -- Дополнительная информация
    company VARCHAR,
    position VARCHAR,
    location VARCHAR,
    
    -- Персональные данные
    birthday DATE,
    notes TEXT,
    tags TEXT[],
    
    -- Характеристики (для детального профиля)
    personality_traits JSONB DEFAULT '{}',  -- Черты характера
    habits TEXT[],                          -- Привычки
    interests TEXT[],                       -- Интересы
    
    -- Метаданные
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Индексы
    CONSTRAINT unique_contact_per_user UNIQUE(user_id, full_name)
);

CREATE INDEX idx_contacts_user_id ON contacts(user_id);
CREATE INDEX idx_contacts_full_name ON contacts(user_id, full_name);

-- ========================================
-- ТАБЛИЦА 2: История взаимодействий
-- ========================================
CREATE TABLE IF NOT EXISTS contact_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR NOT NULL,
    contact_id UUID REFERENCES contacts(id) ON DELETE CASCADE,
    
    -- Тип взаимодействия
    type VARCHAR NOT NULL,  -- meeting, call, message, email
    
    -- Детали
    title VARCHAR,
    description TEXT,
    location VARCHAR,
    
    -- Когда
    interaction_date DATE,
    interaction_time TIME,
    
    -- Сырые данные
    raw_text TEXT,
    
    -- Метаданные
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_interactions_user ON contact_interactions(user_id);
CREATE INDEX idx_interactions_contact ON contact_interactions(contact_id);
CREATE INDEX idx_interactions_date ON contact_interactions(interaction_date DESC);

-- ========================================
-- ТАБЛИЦА 3: Связи между контактами
-- ========================================
CREATE TABLE IF NOT EXISTS contact_relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR NOT NULL,
    contact_id_1 UUID REFERENCES contacts(id) ON DELETE CASCADE,
    contact_id_2 UUID REFERENCES contacts(id) ON DELETE CASCADE,
    
    -- Тип связи
    relationship_type VARCHAR,  -- family, colleague, friend, client
    
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ========================================
-- ТАБЛИЦА 4: Контекст разговора
-- ========================================
CREATE TABLE IF NOT EXISTS conversation_context (
    user_id VARCHAR PRIMARY KEY,
    
    -- Последний упомянутый контакт
    last_mentioned_contact_id UUID REFERENCES contacts(id),
    last_mentioned_name VARCHAR,
    last_mention_time TIMESTAMP,
    
    -- Текущий проект
    current_project_id UUID,
    
    -- Общий контекст
    context_data JSONB DEFAULT '{}',
    
    -- Метаданные
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ========================================
-- ТАБЛИЦА 5: Учет рабочего времени
-- ========================================
CREATE TABLE IF NOT EXISTS work_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR NOT NULL,
    
    -- Тип события
    log_type VARCHAR NOT NULL,  -- arrival, departure, break_start, break_end
    
    -- Время
    log_date DATE NOT NULL,
    log_time TIME NOT NULL,
    
    -- Локация
    location VARCHAR,
    
    -- Дополнительно
    notes TEXT,
    raw_text TEXT,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_work_logs_user ON work_logs(user_id, log_date DESC);

-- ========================================
-- ТАБЛИЦА 6: История сообщений (для ML)
-- ========================================
CREATE TABLE IF NOT EXISTS message_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR NOT NULL,
    
    -- Сообщение
    message_text TEXT,
    has_photo BOOLEAN DEFAULT false,
    
    -- Распознанный интент
    detected_intent VARCHAR,
    intent_confidence FLOAT,
    
    -- Ответ бота
    bot_response TEXT,
    
    -- Timestamp
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_messages_user ON message_history(user_id, created_at DESC);
```

---

## 🔧 РЕАЛИЗАЦИЯ ПО МОДУЛЯМ

### МОДУЛЬ 1: Intent Classifier (Классификатор намерений)

**Файл:** `services/intent_classifier.py`

```python
"""
Классификатор намерений пользователя БЕЗ внешних API.
Использует простые правила на основе ключевых слов.
"""

import re
from typing import Dict, List, Tuple
from datetime import datetime


class IntentClassifier:
    """
    Определяет намерение пользователя по тексту сообщения.
    Не использует внешние API - только ключевые слова.
    """
    
    # Ключевые слова для каждого интента
    INTENT_KEYWORDS = {
        'WORK_LOG': [
            'пришел на работу', 'пришёл на работу',
            'приехал на работу', 'прибыл на работу',
            'начал работу', 'на работе',
            'ушел с работы', 'ушёл с работы',
            'закончил работу'
        ],
        
        'CONTACT_MENTION': [
            'встречался с', 'встречалась с',
            'созвонился с', 'созвонилась с',
            'говорил с', 'говорила с',
            'общался с', 'общалась с',
            'звонил', 'звонила',
            'договорились с', 'договорилась с',
            'встреча с', 'звонок с'
        ],
        
        'TASK': [
            'запиши задачу', 'добавь задачу',
            'нужно сделать', 'надо сделать',
            'не забыть', 'напомни',
            'задача:', 'todo:',
            'сделать', 'купить'
        ],
        
        'PROJECT': [
            'создай проект', 'новый проект',
            'проект:', 'начал проект'
        ],
        
        'HEALTH': [
            'съел', 'съела', 'поел', 'поела',
            'курил', 'курила', 'пошел курить', 'пошла курить',
            'тренировка', 'зал', 'спорт',
            'спал', 'спала', 'сон',
            'выпил', 'выпила'
        ],
        
        'CONTACT_REQUEST': [
            'сравни с контактами', 'мои контакты',
            'кто это', 'найди контакт',
            'добавь контакт', 'есть в контактах'
        ],
        
        'REPORT_REQUEST': [
            'покажи отчет', 'покажи отчёт',
            'отчет за', 'отчёт за',
            'статистика', 'аналитика',
            'сколько потратил', 'траты'
        ],
        
        'SMALL_TALK': [
            'привет', 'здравствуй', 'здорово',
            'как дела', 'спасибо', 'ок', 'окей',
            'пока', 'до свидания'
        ]
    }
    
    def __init__(self):
        # Компилируем регулярки для производительности
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Предкомпилировать паттерны для быстрого поиска"""
        self.compiled_patterns = {}
        for intent, keywords in self.INTENT_KEYWORDS.items():
            # Создаем паттерн из всех ключевых слов
            pattern = '|'.join(re.escape(kw) for kw in keywords)
            self.compiled_patterns[intent] = re.compile(pattern, re.IGNORECASE)
    
    def classify(self, text: str, has_photo: bool = False) -> Tuple[str, float]:
        """
        Определить интент сообщения.
        
        Args:
            text: Текст сообщения
            has_photo: Есть ли фото в сообщении
        
        Returns:
            Tuple[intent, confidence]: Интент и уровень уверенности (0.0-1.0)
        """
        if not text and has_photo:
            return ('RECEIPT', 0.95)
        
        if not text:
            return ('UNKNOWN', 0.0)
        
        text_lower = text.lower().strip()
        
        # Специальный случай: фото с текстом "это я купил"
        if has_photo:
            photo_keywords = ['купил', 'купила', 'чек', 'покупка', 'товар']
            if any(kw in text_lower for kw in photo_keywords):
                return ('RECEIPT', 0.90)
            # Если есть фото но текст не про покупки - возможно селфи и т.д.
            # Пока считаем что фото = чек по умолчанию
            return ('RECEIPT', 0.70)
        
        # Подсчитываем совпадения для каждого интента
        scores = {}
        for intent, pattern in self.compiled_patterns.items():
            matches = pattern.findall(text_lower)
            if matches:
                # Больше совпадений = выше уверенность
                score = min(len(matches) * 0.3 + 0.7, 1.0)
                scores[intent] = score
        
        if not scores:
            return ('UNKNOWN', 0.0)
        
        # Выбираем интент с максимальным score
        best_intent = max(scores.items(), key=lambda x: x[1])
        return best_intent
    
    def extract_time(self, text: str) -> str:
        """
        Извлечь время из текста (для work_log).
        
        Examples:
            "пришел в 7.50" -> "07:50"
            "приехал в 08:30" -> "08:30"
        """
        patterns = [
            r'в\s+(\d{1,2})[.:](\d{2})',  # "в 7.50" или "в 8:30"
            r'(\d{1,2})[.:](\d{2})',       # "7.50" или "8:30"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                hour = match.group(1).zfill(2)
                minute = match.group(2)
                return f"{hour}:{minute}"
        
        # Если время не найдено, возвращаем текущее
        return datetime.now().strftime("%H:%M")
    
    def extract_person_name(self, text: str) -> str:
        """
        Извлечь имя человека из текста.
        
        Examples:
            "встречался с Антоном Носковым" -> "Антон Носков"
            "говорил с Иваном" -> "Иван"
        """
        patterns = [
            r'с\s+([А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+)?)',  # "с Антоном Носковым"
            r'встречался\s+([А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+)?)',
            r'созвонился\s+([А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+)?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return None
```

---

### МОДУЛЬ 2: Contacts Manager (Управление контактами)

**Файл:** `services/contacts_manager.py`

```python
"""
Управление контактами и их историей.
Работает ТОЛЬКО с базой данных пользователя.
"""

from typing import List, Dict, Optional
from datetime import datetime, date
import re
from services.supabase_service import SupabaseService


class ContactsManager:
    """
    Управление контактами пользователя.
    Поиск, создание, обновление, история взаимодействий.
    """
    
    def __init__(self, db: SupabaseService):
        self.db = db
    
    async def find_contact(self, user_id: str, name: str) -> Optional[Dict]:
        """
        Найти контакт в базе пользователя по имени.
        
        Args:
            user_id: ID пользователя Telegram
            name: Имя для поиска (частичное совпадение)
        
        Returns:
            Dict с данными контакта или None
        """
        # Нормализуем имя
        name_normalized = name.strip().lower()
        
        # Ищем по полному имени (case-insensitive)
        result = await self.db.query(
            'contacts',
            {
                'user_id': user_id,
                'full_name__ilike': f'%{name}%'
            }
        )
        
        if not result:
            return None
        
        if len(result) == 1:
            return result[0]
        
        # Если несколько совпадений - вернуть самое точное
        # (где имя встречается в начале)
        for contact in result:
            if contact['full_name'].lower().startswith(name_normalized):
                return contact
        
        # Или вернуть первый результат
        return result[0]
    
    async def create_contact(self, user_id: str, contact_data: Dict) -> Dict:
        """
        Создать новый контакт.
        
        Args:
            user_id: ID пользователя
            contact_data: Данные контакта
        
        Returns:
            Созданный контакт
        """
        data = {
            'user_id': user_id,
            'full_name': contact_data.get('full_name'),
            'first_name': contact_data.get('first_name'),
            'last_name': contact_data.get('last_name'),
            'phone': contact_data.get('phone'),
            'email': contact_data.get('email'),
            'company': contact_data.get('company'),
            'position': contact_data.get('position'),
            'notes': contact_data.get('notes'),
            'created_at': datetime.now().isoformat()
        }
        
        result = await self.db.insert('contacts', data)
        return result
    
    async def add_interaction(
        self,
        user_id: str,
        contact_id: str,
        interaction_type: str,
        details: Dict
    ) -> Dict:
        """
        Добавить запись о взаимодействии с контактом.
        
        Args:
            user_id: ID пользователя
            contact_id: ID контакта
            interaction_type: Тип (meeting, call, message)
            details: Детали взаимодействия
        
        Returns:
            Созданная запись
        """
        data = {
            'user_id': user_id,
            'contact_id': contact_id,
            'type': interaction_type,
            'title': details.get('title'),
            'description': details.get('description'),
            'location': details.get('location'),
            'interaction_date': details.get('date', date.today().isoformat()),
            'interaction_time': details.get('time'),
            'raw_text': details.get('raw_text'),
            'created_at': datetime.now().isoformat()
        }
        
        result = await self.db.insert('contact_interactions', data)
        return result
    
    async def get_interaction_history(
        self,
        user_id: str,
        contact_id: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Получить историю взаимодействий с контактом.
        
        Args:
            user_id: ID пользователя
            contact_id: ID контакта
            limit: Максимальное количество записей
        
        Returns:
            List истории взаимодействий
        """
        result = await self.db.query(
            'contact_interactions',
            {
                'user_id': user_id,
                'contact_id': contact_id
            },
            order_by='created_at',
            order='desc',
            limit=limit
        )
        
        return result or []
    
    async def update_context(
        self,
        user_id: str,
        contact_id: str,
        contact_name: str
    ):
        """
        Обновить контекст разговора (последний упомянутый контакт).
        
        Args:
            user_id: ID пользователя
            contact_id: ID контакта
            contact_name: Имя контакта
        """
        data = {
            'user_id': user_id,
            'last_mentioned_contact_id': contact_id,
            'last_mentioned_name': contact_name,
            'last_mention_time': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # Upsert (insert or update)
        await self.db.upsert('conversation_context', data, ['user_id'])
    
    async def get_context(self, user_id: str) -> Optional[Dict]:
        """
        Получить текущий контекст разговора.
        
        Args:
            user_id: ID пользователя
        
        Returns:
            Dict с контекстом или None
        """
        result = await self.db.query(
            'conversation_context',
            {'user_id': user_id}
        )
        
        return result[0] if result else None
    
    def parse_person_name(self, text: str) -> Optional[str]:
        """
        Извлечь имя человека из текста.
        
        Examples:
            "встречался с Антоном Носковым" -> "Антон Носков"
            "говорил с Иваном" -> "Иван"
        """
        patterns = [
            r'с\s+([А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+)?)',
            r'встречался\s+([А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+)?)',
            r'созвонился\s+([А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+)?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return None
```

---

### МОДУЛЬ 3: Contacts Handler (Обработчик контактов)

**Файл:** `handlers/contacts_handler.py`

```python
"""
Обработчик упоминаний контактов в сообщениях.
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.contacts_manager import ContactsManager
from services.supabase_service import SupabaseService
from datetime import datetime, date


class ContactsHandler:
    """
    Обработка упоминаний людей в сообщениях.
    """
    
    def __init__(self, db: SupabaseService):
        self.db = db
        self.contacts = ContactsManager(db)
    
    async def handle_mention(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> str:
        """
        Обработать упоминание контакта.
        
        Args:
            update: Telegram Update
            context: Telegram Context
        
        Returns:
            Текст ответа пользователю
        """
        text = update.message.text
        user_id = str(update.effective_user.id)
        
        # 1. Извлечь имя человека
        person_name = self.contacts.parse_person_name(text)
        
        if not person_name:
            return "❓ Не понял, о ком речь. Укажите имя человека."
        
        # 2. Найти контакт в базе
        contact = await self.contacts.find_contact(user_id, person_name)
        
        if contact:
            # Контакт найден - сохранить взаимодействие
            await self._process_found_contact(
                user_id, contact, text, update, context
            )
            
            return self._format_contact_found(contact, text)
        
        else:
            # Контакт не найден - предложить добавить
            await self._offer_add_contact(
                person_name, update, context
            )
            
            return f"❓ **{person_name}** не найден в контактах.\n" \
                   "Хотите добавить?"
    
    async def _process_found_contact(
        self,
        user_id: str,
        contact: dict,
        text: str,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """
        Обработать найденный контакт:
        - Сохранить взаимодействие
        - Обновить контекст
        """
        # Определить тип взаимодействия
        interaction_type = self._detect_interaction_type(text)
        
        # Сохранить в историю
        await self.contacts.add_interaction(
            user_id=user_id,
            contact_id=contact['id'],
            interaction_type=interaction_type,
            details={
                'title': f"{interaction_type.title()} с {contact['full_name']}",
                'description': text,
                'raw_text': text,
                'date': date.today().isoformat(),
                'time': datetime.now().strftime("%H:%M")
            }
        )
        
        # Обновить контекст (этот человек последний упомянутый)
        await self.contacts.update_context(
            user_id=user_id,
            contact_id=contact['id'],
            contact_name=contact['full_name']
        )
    
    def _detect_interaction_type(self, text: str) -> str:
        """
        Определить тип взаимодействия по тексту.
        
        Returns:
            'meeting', 'call', 'message', 'email'
        """
        text_lower = text.lower()
        
        if any(kw in text_lower for kw in ['встречался', 'встреча', 'увиделись']):
            return 'meeting'
        elif any(kw in text_lower for kw in ['созвонился', 'звонил', 'звонок']):
            return 'call'
        elif any(kw in text_lower for kw in ['написал', 'сообщение']):
            return 'message'
        elif 'email' in text_lower or 'письмо' in text_lower:
            return 'email'
        else:
            return 'meeting'  # По умолчанию
    
    def _format_contact_found(self, contact: dict, original_text: str) -> str:
        """
        Форматировать ответ когда контакт найден.
        """
        message = f"✅ Записано: {original_text}\n\n"
        message += f"👤 **{contact['full_name']}**\n"
        
        if contact.get('phone'):
            message += f"📱 {contact['phone']}\n"
        
        if contact.get('company'):
            message += f"🏢 {contact['company']}"
            if contact.get('position'):
                message += f" ({contact['position']})"
            message += "\n"
        
        if contact.get('email'):
            message += f"📧 {contact['email']}\n"
        
        return message
    
    async def _offer_add_contact(
        self,
        person_name: str,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """
        Предложить добавить контакт (с кнопкой).
        """
        keyboard = [
            [
                InlineKeyboardButton(
                    "➕ Добавить контакт",
                    callback_data=f"add_contact:{person_name}"
                )
            ],
            [
                InlineKeyboardButton(
                    "❌ Отмена",
                    callback_data="cancel"
                )
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"❓ **{person_name}** не найден в ваших контактах.\n"
            "Хотите добавить?",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def handle_search_in_contacts(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> str:
        """
        Обработать запрос "сравни с моими контактами".
        """
        user_id = str(update.effective_user.id)
        
        # Получить последний упомянутый контакт из контекста
        ctx = await self.contacts.get_context(user_id)
        
        if not ctx or not ctx.get('last_mentioned_contact_id'):
            return "❓ Не понял, о ком речь. Сначала упомяните человека."
        
        contact_id = ctx['last_mentioned_contact_id']
        
        # Получить данные контакта
        contacts_list = await self.db.query(
            'contacts',
            {'id': contact_id}
        )
        
        if not contacts_list:
            return "❓ Контакт не найден."
        
        contact = contacts_list[0]
        
        # Получить историю взаимодействий
        history = await self.contacts.get_interaction_history(
            user_id=user_id,
            contact_id=contact_id,
            limit=5
        )
        
        # Форматировать ответ
        message = f"👤 **{contact['full_name']}** найден в контактах!\n\n"
        
        if contact.get('phone'):
            message += f"📱 {contact['phone']}\n"
        if contact.get('company'):
            message += f"🏢 {contact['company']}\n"
        if contact.get('email'):
            message += f"📧 {contact['email']}\n"
        
        if history:
            message += "\n📜 **Последние взаимодействия:**\n"
            for h in history[:3]:
                date_str = h['interaction_date']
                message += f"• {date_str}: {h['type']} - {h.get('description', '')}\n"
        
        return message
```

---

### МОДУЛЬ 4: Work Tracker (Учет рабочего времени)

**Файл:** `handlers/work_tracker_handler.py`

```python
"""
Обработчик учета рабочего времени.
"""

from telegram import Update
from telegram.ext import ContextTypes
from services.supabase_service import SupabaseService
from datetime import datetime, date
import re


class WorkTrackerHandler:
    """
    Учет рабочего времени: приход, уход, перерывы.
    """
    
    def __init__(self, db: SupabaseService):
        self.db = db
    
    async def handle_work_log(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> str:
        """
        Обработать запись о рабочем времени.
        
        Args:
            update: Telegram Update
            context: Telegram Context
        
        Returns:
            Текст ответа
        """
        text = update.message.text
        user_id = str(update.effective_user.id)
        
        # Определить тип события
        log_type = self._detect_log_type(text)
        
        # Извлечь время
        log_time = self._extract_time(text)
        
        # Сохранить в БД
        await self.db.insert('work_logs', {
            'user_id': user_id,
            'log_type': log_type,
            'log_date': date.today().isoformat(),
            'log_time': log_time,
            'raw_text': text,
            'created_at': datetime.now().isoformat()
        })
        
        # Форматировать ответ
        emoji = self._get_emoji(log_type)
        type_text = self._get_type_text(log_type)
        
        return f"{emoji} Записано: {type_text} в {log_time}"
    
    def _detect_log_type(self, text: str) -> str:
        """
        Определить тип события.
        
        Returns:
            'arrival', 'departure', 'break_start', 'break_end'
        """
        text_lower = text.lower()
        
        if any(kw in text_lower for kw in ['пришел', 'пришёл', 'приехал', 'прибыл', 'начал работу']):
            return 'arrival'
        elif any(kw in text_lower for kw in ['ушел', 'ушёл', 'уехал', 'закончил работу']):
            return 'departure'
        elif 'перерыв' in text_lower:
            if 'начал' in text_lower or 'на' in text_lower:
                return 'break_start'
            else:
                return 'break_end'
        else:
            return 'arrival'  # По умолчанию
    
    def _extract_time(self, text: str) -> str:
        """
        Извлечь время из текста.
        
        Examples:
            "пришел в 7.50" -> "07:50"
            "приехал в 08:30" -> "08:30"
        """
        patterns = [
            r'в\s+(\d{1,2})[.:](\d{2})',
            r'(\d{1,2})[.:](\d{2})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                hour = match.group(1).zfill(2)
                minute = match.group(2)
                return f"{hour}:{minute}"
        
        # Если не найдено - текущее время
        return datetime.now().strftime("%H:%M")
    
    def _get_emoji(self, log_type: str) -> str:
        """Получить emoji для типа события."""
        emojis = {
            'arrival': '🟢',
            'departure': '🔴',
            'break_start': '⏸️',
            'break_end': '▶️'
        }
        return emojis.get(log_type, '📍')
    
    def _get_type_text(self, log_type: str) -> str:
        """Получить текстовое описание типа."""
        texts = {
            'arrival': 'приход на работу',
            'departure': 'уход с работы',
            'break_start': 'начало перерыва',
            'break_end': 'конец перерыва'
        }
        return texts.get(log_type, 'событие')
```

---

### МОДУЛЬ 5: Unified Handler (Главный роутер)

**Файл:** `handlers/unified.py` (ИСПРАВИТЬ)

```python
"""
Единый обработчик всех текстовых сообщений.
Маршрутизирует по интентам БЕЗ использования Perplexity.
"""

from telegram import Update
from telegram.ext import ContextTypes
from services.intent_classifier import IntentClassifier
from services.supabase_service import SupabaseService
from handlers.contacts_handler import ContactsHandler
from handlers.work_tracker_handler import WorkTrackerHandler
from handlers.tasks_handler import TasksHandler
from handlers.projects_handler import ProjectsHandler
from handlers.health_handler import HealthHandler
from handlers.receipts_handler import ReceiptsHandler


class UnifiedHandler:
    """
    Единая точка входа для всех текстовых сообщений.
    Определяет интент и маршрутизирует к нужному обработчику.
    """
    
    def __init__(self, db: SupabaseService):
        self.db = db
        self.classifier = IntentClassifier()
        
        # Инициализировать обработчики
        self.contacts_handler = ContactsHandler(db)
        self.work_tracker = WorkTrackerHandler(db)
        self.tasks_handler = TasksHandler(db)
        self.projects_handler = ProjectsHandler(db)
        self.health_handler = HealthHandler(db)
        self.receipts_handler = ReceiptsHandler(db)
    
    async def handle_message(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """
        Главный обработчик сообщений.
        
        Этот метод:
        1. Определяет интент БЕЗ внешних API
        2. Маршрутизирует к нужному handler
        3. Возвращает короткий ответ (1-3 строки)
        """
        text = update.message.text if update.message.text else ""
        has_photo = bool(update.message.photo)
        user_id = str(update.effective_user.id)
        
        # 1. Классифицировать интент
        intent, confidence = self.classifier.classify(text, has_photo)
        
        # 2. Логировать для статистики
        await self._log_message(user_id, text, has_photo, intent, confidence)
        
        # 3. Маршрутизировать
        try:
            response = await self._route_to_handler(
                intent, update, context
            )
        except Exception as e:
            print(f"Error in handler: {e}")
            response = f"❌ Произошла ошибка: {str(e)}"
        
        # 4. Отправить ответ
        await update.message.reply_text(
            response,
            parse_mode='Markdown'
        )
    
    async def _route_to_handler(
        self,
        intent: str,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> str:
        """
        Маршрутизация к обработчику по интенту.
        
        Args:
            intent: Определенный интент
            update: Telegram Update
            context: Telegram Context
        
        Returns:
            Текст ответа пользователю
        """
        
        # WORK_LOG: Учет рабочего времени
        if intent == 'WORK_LOG':
            return await self.work_tracker.handle_work_log(update, context)
        
        # CONTACT_MENTION: Упоминание человека
        elif intent == 'CONTACT_MENTION':
            return await self.contacts_handler.handle_mention(update, context)
        
        # CONTACT_REQUEST: Запрос поиска в контактах
        elif intent == 'CONTACT_REQUEST':
            return await self.contacts_handler.handle_search_in_contacts(
                update, context
            )
        
        # TASK: Задача
        elif intent == 'TASK':
            return await self.tasks_handler.handle_freeform_task(
                update, context
            )
        
        # PROJECT: Проект
        elif intent == 'PROJECT':
            return await self.projects_handler.handle_freeform_project(
                update, context
            )
        
        # HEALTH: Здоровье
        elif intent == 'HEALTH':
            return await self.health_handler.handle_freeform(
                update, context
            )
        
        # RECEIPT: Чек (фото)
        elif intent == 'RECEIPT':
            return await self.receipts_handler.analyze_receipt(
                update, context
            )
        
        # REPORT_REQUEST: Запрос отчета
        elif intent == 'REPORT_REQUEST':
            # TODO: Реализовать обработчик отчетов
            return "📊 Отчеты в разработке. Используйте команды /task list, /health report"
        
        # SMALL_TALK: Обычный разговор
        elif intent == 'SMALL_TALK':
            return self._handle_small_talk(update.message.text)
        
        # UNKNOWN: Неизвестный интент
        else:
            return self._handle_unknown(update.message.text)
    
    def _handle_small_talk(self, text: str) -> str:
        """
        Обработать обычный разговор.
        """
        text_lower = text.lower()
        
        if 'привет' in text_lower or 'здравствуй' in text_lower:
            return "👋 Привет! Что нужно сделать?"
        elif 'спасибо' in text_lower:
            return "🙂 Рад помочь!"
        elif 'пока' in text_lower:
            return "👋 До встречи!"
        else:
            return "😊 Чем могу помочь?"
    
    def _handle_unknown(self, text: str) -> str:
        """
        Обработать неизвестное сообщение.
        """
        return (
            "❓ Не совсем понял. Попробуйте:\n"
            '• "запиши задачу: ..."\n'
            '• "создай проект ..."\n'
            '• "пришел на работу в X:XX"\n'
            '• отправьте фото чека\n'
            '• /help для справки'
        )
    
    async def _log_message(
        self,
        user_id: str,
        text: str,
        has_photo: bool,
        intent: str,
        confidence: float
    ):
        """
        Логировать сообщение для статистики и ML.
        """
        try:
            await self.db.insert('message_history', {
                'user_id': user_id,
                'message_text': text,
                'has_photo': has_photo,
                'detected_intent': intent,
                'intent_confidence': confidence,
                'created_at': datetime.now().isoformat()
            })
        except:
            pass  # Не критично если логирование не работает
```

---

### МОДУЛЬ 6: Main (Точка входа)

**Файл:** `main.py` (ИСПРАВИТЬ)

```python
"""
Главный файл запуска бота.
"""

import os
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

from config import Config
from services.supabase_service import SupabaseService
from handlers.commands import CommandsHandler
from handlers.unified import UnifiedHandler

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def post_init(application: Application):
    """Действия после инициализации бота."""
    logger.info("Bot started successfully!")


def main():
    """Запуск бота."""
    
    # Инициализация
    config = Config()
    db = SupabaseService(
        url=config.SUPABASE_URL,
        key=config.SUPABASE_SERVICE_ROLE_KEY
    )
    
    # Создать Application
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
    
    # Handlers
    commands_handler = CommandsHandler(db)
    unified_handler = UnifiedHandler(db)
    
    # ===========================================
    # КОМАНДЫ
    # ===========================================
    application.add_handler(
        CommandHandler("start", commands_handler.start)
    )
    application.add_handler(
        CommandHandler("help", commands_handler.help_command)
    )
    
    # ===========================================
    # ТЕКСТОВЫЕ СООБЩЕНИЯ
    # ===========================================
    # ⚠️ ВАЖНО: Все текстовые сообщения (кроме команд)
    # идут в UnifiedHandler, который определяет интент
    # и маршрутизирует БЕЗ Perplexity
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            unified_handler.handle_message
        )
    )
    
    # ===========================================
    # ФОТО
    # ===========================================
    # Фото тоже идет в UnifiedHandler
    # (он определит что это чек и передаст в ReceiptsHandler)
    application.add_handler(
        MessageHandler(
            filters.PHOTO,
            unified_handler.handle_message
        )
    )
    
    # ===========================================
    # CALLBACK QUERIES (кнопки)
    # ===========================================
    # TODO: Добавить обработчик для кнопок
    # (например, "Добавить контакт")
    
    # Post init
    application.post_init = post_init
    
    # Запуск
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
```

---

## 🧪 ТЕСТИРОВАНИЕ

### Тестовые сценарии

```python
"""
Файл: tests/test_intent_classifier.py
"""

import pytest
from services.intent_classifier import IntentClassifier


class TestIntentClassifier:
    
    @pytest.fixture
    def classifier(self):
        return IntentClassifier()
    
    def test_work_log_arrival(self, classifier):
        """Тест: Приход на работу"""
        intent, conf = classifier.classify("Пришел на работу в 7.50")
        assert intent == 'WORK_LOG'
        assert conf > 0.7
    
    def test_contact_mention(self, classifier):
        """Тест: Упоминание контакта"""
        intent, conf = classifier.classify(
            "Встречался вчера с Антоном Носковым"
        )
        assert intent == 'CONTACT_MENTION'
        assert conf > 0.7
    
    def test_receipt_photo(self, classifier):
        """Тест: Фото чека"""
        intent, conf = classifier.classify("", has_photo=True)
        assert intent == 'RECEIPT'
        assert conf > 0.9
    
    def test_task(self, classifier):
        """Тест: Задача"""
        intent, conf = classifier.classify(
            "Запиши задачу: купить молоко"
        )
        assert intent == 'TASK'
        assert conf > 0.7
    
    def test_small_talk(self, classifier):
        """Тест: Обычный разговор"""
        intent, conf = classifier.classify("Привет")
        assert intent == 'SMALL_TALK'
        assert conf > 0.7
```

### Ручное тестирование

```bash
# =========================================
# ТЕСТ 1: Рабочее время
# =========================================
USER: "Пришел на работу в 7.50"
EXPECTED: "🟢 Записано: приход на работу в 07:50"

# =========================================
# ТЕСТ 2: Контакт
# =========================================
USER: "Встречался вчера с Антоном Носковым, договорились созвониться"
EXPECTED:
"✅ Записано: встречался вчера с Антоном Носковым...

👤 **Антон Носков**
📱 +7...
🏢 Камчатка"

# =========================================
# ТЕСТ 3: Поиск в контактах
# =========================================
USER: "Сравни с моими контактами"
EXPECTED: Показать данные последнего упомянутого контакта

# =========================================
# ТЕСТ 4: Чек
# =========================================
USER: (отправил фото чека)
EXPECTED:
"🧾 Чек: Пятёрочка, 385₽, 3 товара
• Молоко 90₽
• Хлеб 45₽
• Филе 250₽"

# =========================================
# ТЕСТ 5: Задача
# =========================================
USER: "Запиши задачу: купить молоко до пятницы"
EXPECTED: "✅ Задача добавлена: купить молоко (дедлайн: пт)"

# =========================================
# ТЕСТ 6: Обычный разговор
# =========================================
USER: "Привет"
EXPECTED: "👋 Привет! Что нужно сделать?"

# =========================================
# ТЕСТ 7: Неизвестное
# =========================================
USER: "asdfghjkl"
EXPECTED: "❓ Не совсем понял. Попробуйте: ..."
```

---

## 🚀 РАЗВЕРТЫВАНИЕ

### Шаг 1: Обновить базу данных

```bash
# Выполнить SQL из раздела "База данных"
# в Supabase SQL Editor
```

### Шаг 2: Установить зависимости

```bash
pip install python-telegram-bot==20.7
pip install supabase==2.0.0
pip install python-dotenv
```

### Шаг 3: Обновить .env

```bash
TELEGRAM_BOT_TOKEN=your_bot_token
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

### Шаг 4: Запустить бота

```bash
python main.py
```

### Шаг 5: Протестировать

```
1. /start
2. "Пришел на работу в 8:00"
3. "Встречался с Иваном Ивановым"
4. (отправить фото чека)
5. "Запиши задачу: позвонить Ивану"
```

---

## ✅ ЧЕКЛИСТ ВЫПОЛНЕНИЯ

### Критические изменения

- [ ] **УДАЛИТЬ/ОТКЛЮЧИТЬ** все вызовы Perplexity API из обработчиков
- [ ] **СОЗДАТЬ** `services/intent_classifier.py`
- [ ] **СОЗДАТЬ** `services/contacts_manager.py`
- [ ] **СОЗДАТЬ** `handlers/contacts_handler.py`
- [ ] **СОЗДАТЬ** `handlers/work_tracker_handler.py`
- [ ] **ИСПРАВИТЬ** `handlers/unified.py` (использовать IntentClassifier)
- [ ] **СОЗДАТЬ** таблицы БД (SQL из раздела "База данных")
- [ ] **ИСПРАВИТЬ** `main.py` (роутинг через UnifiedHandler)

### Тестирование

- [ ] Запустить unit-тесты
- [ ] Пройти все 7 ручных тестов
- [ ] Проверить что Perplexity НЕ вызывается
- [ ] Проверить работу с контактами
- [ ] Проверить учет рабочего времени
- [ ] Проверить анализ чеков

### Документация

- [ ] Обновить README.md
- [ ] Добавить примеры использования
- [ ] Описать структуру БД

---

## 📞 ПОДДЕРЖКА

Если возникли вопросы:

1. Проверьте логи: `python main.py` покажет все ошибки
2. Проверьте БД: все таблицы созданы?
3. Проверьте .env: все переменные заполнены?
4. Тестируйте по шагам: сначала intent_classifier, потом handlers

---

**Статус:** 🔴 КРИТИЧЕСКАЯ ПРОБЛЕМА  
**Deadline:** 14 декабря 2025, 18:00 MSK  
**Приоритет:** HIGHEST  

> 🎯 **ЦЕЛЬ: Превратить поисковый бот в персонального ассистента с контекстом и историей!**
