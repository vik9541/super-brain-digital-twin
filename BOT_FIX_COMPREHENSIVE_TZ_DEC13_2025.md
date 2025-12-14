# 🤖 КОМПЛЕКСНОЕ ТЗ: ИСПРАВЛЕНИЕ И РЕАЛИЗАЦИЯ БОТА 

**Дата:** 13 декабря 2025, 21:56 MSK  
**Версия:** v1.0 (Complete Edition)  
**Статус:** 🟢 READY FOR IMPLEMENTATION  
**Приоритет:** CRITICAL  
**Deadline:** 1 января 2026  

---

## 📋 ПОЛНЫЙ АНАЛИЗ ПРОБЛЕМ

На основе анализа **всех ТЗ, инцидент-репортов и тест-отчетов** выявлены следующие проблемы:

### 🔴 КРИТИЧЕСКИЕ ПРОБЛЕМЫ

#### 1. ИНФРАСТРУКТУРНЫЕ ПРОБЛЕМЫ (РЕШЕНЫ)
- ❌ ~~DNS мисматч (был на 8 декабря)~~ → ✅ **РЕШЕНО 9 декабря**
- ✅ Kubernetes кластер работает нормально
- ✅ API доступен извне (138.197.254.53)
- ✅ LoadBalancer сервисы работают

**Статус:** 🟢 Инфраструктура полностью работает

#### 2. ФУНКЦИОНАЛЬНОСТЬ БОТА

В текущем BOT_PERSONAL_ASSISTANT_TZ.md описана **необходимая функциональность**, которую НУЖНО реализовать:

| Функция | Статус | Приоритет |
|:--------|:------:|:---------:|
| Система проектов с файлами | ❌ Не реализована | CRITICAL |
| Управление задачами | ❌ Не реализована | CRITICAL |
| Анализ чеков (OCR) | ❌ Не реализована | HIGH |
| Категоризация товаров | ❌ Не реализована | HIGH |
| Сравнение цен (маркетплейсы) | ❌ Не реализована | HIGH |
| Дневник здоровья | ❌ Не реализована | MEDIUM |
| Режимы взаимодействия | ❌ Не реализована | MEDIUM |
| Аналитика и отчеты | ❌ Не реализована | MEDIUM |

#### 3. АРХИТЕКТУРНЫЕ ПРОБЛЕМЫ

- ❌ Нет структурированной системы проектов
- ❌ Нет хранилища для файлов
- ❌ Нет интеграций с маркетплейсами
- ❌ Нет OCR для чеков
- ❌ Нет дневника здоровья
- ❌ Код монолитный, не модульный
- ❌ Нет правильной структуры БД в Supabase

---

## 🎯 ПЛАН РЕАЛИЗАЦИИ: 3 НЕДЕЛИ

### НЕДЕЛЯ 1 (13-19 ДЕКАБРЯ): ФУНДАМЕНТ

#### ДЕНЬ 1: ПН 13 ДЕКАБРЯ
**TASK-BOT-FIX-001: Подготовка БД и структуры**

```sql
-- Выполнить в Supabase PostgreSQL консоли:

-- Таблицы для проектов
CREATE TABLE user_projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR NOT NULL,
    project_name VARCHAR NOT NULL,
    description TEXT,
    status VARCHAR DEFAULT 'active', -- active, done, archived
    created_at TIMESTAMP DEFAULT NOW(),
    deadline TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

CREATE TABLE project_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES user_projects(id) ON DELETE CASCADE,
    file_name VARCHAR NOT NULL,
    file_url VARCHAR NOT NULL,
    file_hash VARCHAR,
    file_type VARCHAR,
    file_size INT,
    uploaded_at TIMESTAMP DEFAULT NOW(),
    tags TEXT[] DEFAULT '{}'
);

-- Таблицы для задач
CREATE TABLE user_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR NOT NULL,
    project_id UUID REFERENCES user_projects(id) ON DELETE SET NULL,
    task_description TEXT NOT NULL,
    status VARCHAR DEFAULT 'pending', -- pending, in_progress, done
    created_at TIMESTAMP DEFAULT NOW(),
    due_date TIMESTAMP,
    priority VARCHAR DEFAULT 'medium' -- low, medium, high
);

-- Таблицы для чеков
CREATE TABLE receipts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR NOT NULL,
    store_name VARCHAR,
    store_location VARCHAR,
    receipt_date TIMESTAMP,
    total_sum DECIMAL,
    file_url VARCHAR,
    created_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

CREATE TABLE receipt_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    receipt_id UUID REFERENCES receipts(id) ON DELETE CASCADE,
    item_name VARCHAR NOT NULL,
    category VARCHAR,
    price DECIMAL,
    quantity DECIMAL,
    unit VARCHAR,
    price_per_unit DECIMAL
);

-- Таблицы для здоровья
CREATE TABLE health_diary (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR NOT NULL,
    entry_date DATE,
    entry_time TIME,
    entry_type VARCHAR, -- food, activity, habit, mood, sleep, measurement
    description TEXT,
    data JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Настройки пользователя
CREATE TABLE user_preferences (
    user_id VARCHAR PRIMARY KEY,
    mode VARCHAR DEFAULT 'executor', -- executor, advisor, silent, detailed
    give_advice BOOLEAN DEFAULT false,
    language VARCHAR DEFAULT 'ru',
    timezone VARCHAR DEFAULT 'Europe/Moscow',
    metadata JSONB DEFAULT '{}'
);

-- Индексы для быстрого поиска
CREATE INDEX idx_user_projects ON user_projects(user_id);
CREATE INDEX idx_user_tasks ON user_tasks(user_id);
CREATE INDEX idx_project_files ON project_files(project_id);
CREATE INDEX idx_receipts ON receipts(user_id);
CREATE INDEX idx_health_diary ON health_diary(user_id);
```

**Чек-лист:**
- [ ] Все таблицы созданы в Supabase
- [ ] Индексы созданы
- [ ] Роль доступа настроена
- [ ] RLS политики установлены

---

#### ДЕНЬ 2: ВТ 14 ДЕКАБРЯ
**TASK-BOT-FIX-002: Архитектура и структура кода**

Создать правильную структуру в superbrain-backend repo:

```
bots/personal-assistant-bot/
├── __init__.py
├── main.py                          # Точка входа
├── config.py                        # Конфигурация
├── handlers/
│   ├── __init__.py
│   ├── commands.py                  # Все /команды
│   ├── projects_handler.py          # Проекты
│   ├── tasks_handler.py             # Задачи
│   ├── receipts_handler.py          # Чеки
│   ├── health_handler.py            # Здоровье
│   └── settings_handler.py          # Настройки
├── services/
│   ├── __init__.py
│   ├── ocr_service.py               # Google Vision API
│   ├── receipt_parser.py            # Парсинг структуры чека
│   ├── market_service.py            # Yandex Market API
│   ├── health_analytics.py          # Анализ здоровья
│   ├── storage_service.py           # Supabase Storage
│   └── supabase_service.py          # БД операции
├── models/
│   ├── __init__.py
│   ├── project.py
│   ├── task.py
│   ├── receipt.py
│   ├── health_entry.py
│   └── user_preferences.py
├── utils/
│   ├── __init__.py
│   ├── formatter.py                 # Форматирование сообщений
│   ├── validators.py                # Валидация данных
│   └── helpers.py
└── tests/
    ├── __init__.py
    ├── test_handlers.py
    ├── test_services.py
    └── test_integration.py
```

**Чек-лист:**
- [ ] Все папки и файлы созданы
- [ ] __init__.py файлы добавлены
- [ ] Импорты настроены
- [ ] Git структура готова

---

#### ДЕНЬ 3: СР 15 ДЕКАБРЯ
**TASK-BOT-FIX-003: Базовые обработчики команд**

```python
# handlers/commands.py

from telegram import Update
from telegram.ext import ContextTypes
from services.supabase_service import SupabaseService

class CommandHandler:
    def __init__(self):
        self.db = SupabaseService()
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        user_id = update.effective_user.id
        first_name = update.effective_user.first_name
        
        # Создать пользователя если не существует
        await self.db.ensure_user_exists(user_id)
        
        message = f"Привет, {first_name}! 👋\n\n"
        message += "Я твой персональный помощник!\n\n"
        message += "📋 **Команды:**\n"
        message += "/project list - Твои проекты\n"
        message += "/task list - Активные задачи\n"
        message += "/receipt analyze - Анализ чека\n"
        message += "/health diary - Дневник здоровья\n"
        message += "/mode executor - Режим работы\n"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def project_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /project list"""
        user_id = update.effective_user.id
        
        projects = await self.db.get_user_projects(user_id)
        
        if not projects:
            await update.message.reply_text("📂 У тебя еще нет проектов.\nСоздай первый проект: /project add [название]")
            return
        
        message = "📂 **Твои проекты:**\n\n"
        for i, project in enumerate(projects, 1):
            message += f"{i}. {project['project_name']} ({project['status']})\n"
            message += f"   📄 Файлов: {len(project.get('files', []))}\n"
            message += f"   📋 Задач: {len(project.get('tasks', []))}\n\n"
        
        await update.message.reply_text(message, parse_mode='Markdown')
```

**Чек-лист:**
- [ ] /start команда работает
- [ ] /project list работает
- [ ] /task list работает
- [ ] Пользователь создается в БД

---

#### ДЕНЬ 4: ЧТ 16 ДЕКАБРЯ
**TASK-BOT-FIX-004: Система проектов**

```python
# handlers/projects_handler.py

async def project_add(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Создать проект /project add [название]"""
    user_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text("Использование: /project add [название проекта]")
        return
    
    project_name = ' '.join(context.args)
    
    project = await self.db.create_project(
        user_id=user_id,
        project_name=project_name,
        description=None
    )
    
    message = f"✅ Проект '{project_name}' создан!\n\n"
    message += "📎 Загрузить файл: /project upload\n"
    message += "📋 Добавить задачу: /task add [описание]\n"
    
    await update.message.reply_text(message)

async def project_upload(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Загрузить файл в проект"""
    if not update.message.document:
        await update.message.reply_text("Пожалуйста, загрузите документ")
        return
    
    file = update.message.document
    user_id = update.effective_user.id
    
    # Скачать файл
    file_path = await file.download()
    
    # Загрузить в Supabase Storage
    file_url = await self.storage.upload_file(
        bucket='projects',
        path=f"{user_id}/{file.file_name}",
        file_path=file_path
    )
    
    # Сохранить в БД
    await self.db.save_project_file(
        project_id=None,  # Пока без проекта
        file_name=file.file_name,
        file_url=file_url,
        file_size=file.file_size,
        file_type=file.mime_type
    )
    
    await update.message.reply_text(f"✅ Файл '{file.file_name}' загружен!")
```

**Чек-лист:**
- [ ] /project add работает
- [ ] /project upload работает
- [ ] Файлы сохраняются в Supabase Storage
- [ ] Данные в БД сохраняются

---

#### ДЕНЬ 5: ПТ 17 ДЕКАБРЯ
**TASK-BOT-FIX-005: Система управления задачами**

```python
# handlers/tasks_handler.py

async def task_add(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавить задачу /task add [описание]"""
    user_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text("Использование: /task add [описание задачи]")
        return
    
    task_description = ' '.join(context.args)
    
    task = await self.db.create_task(
        user_id=user_id,
        task_description=task_description,
        priority='medium'
    )
    
    await update.message.reply_text(f"✅ Задача добавлена: '{task_description}'")

async def task_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Список активных задач /task list"""
    user_id = update.effective_user.id
    
    tasks = await self.db.get_user_tasks(user_id, status='pending')
    
    if not tasks:
        await update.message.reply_text("✅ У тебя нет активных задач!")
        return
    
    message = "📋 **Активные задачи:**\n\n"
    for i, task in enumerate(tasks, 1):
        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task['priority'], "⚪")
        message += f"{i}. {priority_emoji} {task['task_description']}\n"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def task_done(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отметить задачу выполненной /task done [id]"""
    if not context.args:
        await update.message.reply_text("Использование: /task done [номер задачи]")
        return
    
    task_id = context.args[0]
    await self.db.update_task_status(task_id, 'done')
    
    await update.message.reply_text("✅ Задача завершена!")
```

**Чек-лист:**
- [ ] /task add работает
- [ ] /task list работает
- [ ] /task done работает
- [ ] Статусы обновляются в БД

---

#### ДЕНЬ 6-7: СБ-ВС 18-19 ДЕКАБРЯ
**TASK-BOT-FIX-006: Тестирование НЕДЕЛИ 1**

```bash
# Прогнать все тесты
python -m pytest tests/ -v

# Тест начиная с /start
1. /start → должен ответить с меню
2. /project add "Тест" → должен создать проект
3. /task add "Тест задача" → должен создать задачу
4. /project list → должен показать проект
5. /task list → должен показать задачу
6. /task done 1 → должен отметить выполненной
```

**Чек-лист:**
- [ ] Все команды НЕДЕЛИ 1 работают
- [ ] Бд правильно сохраняет данные
- [ ] Нет ошибок в логах
- [ ] Тесты проходят на 100%

---

### НЕДЕЛЯ 2 (20-26 ДЕКАБРЯ): АНАЛИЗ ЧЕКОВ

#### ДЕНЬ 8: ПН 20 ДЕКАБРЯ
**TASK-BOT-FIX-007: Google Vision API (OCR)**

```python
# services/ocr_service.py

from google.cloud import vision
import os

class OCRService:
    def __init__(self):
        self.client = vision.ImageAnnotatorClient()
    
    async def extract_text_from_image(self, image_path: str) -> str:
        """Распознать текст со скана/фото"""
        with open(image_path, 'rb') as image_file:
            image = vision.Image(content=image_file.read())
        
        response = self.client.text_detection(image=image)
        texts = response.text_annotations
        
        if texts:
            return texts[0].description
        return None
    
    async def extract_from_url(self, image_url: str) -> str:
        """Распознать текст с URL"""
        image = vision.Image()
        image.source.image_uri = image_url
        
        response = self.client.text_detection(image=image)
        texts = response.text_annotations
        
        if texts:
            return texts[0].description
        return None
```

**Чек-лист:**
- [ ] Google Cloud API ключ установлен
- [ ] OCR Service работает
- [ ] Текст распознается корректно

---

#### ДЕНЬ 9: ВТ 21 ДЕКАБРЯ
**TASK-BOT-FIX-008: Парсинг структуры чека**

```python
# services/receipt_parser.py

from typing import Dict, List
from datetime import datetime
import re

class ReceiptParser:
    
    async def parse_receipt_text(self, text: str) -> Dict:
        """Парсит текст чека и извлекает структуру"""
        
        parsed = {
            'store_name': self._extract_store_name(text),
            'receipt_date': self._extract_date(text),
            'receipt_time': self._extract_time(text),
            'items': self._extract_items(text),
            'total_sum': self._extract_total(text),
            'address': self._extract_address(text),
            'raw_text': text
        }
        
        return parsed
    
    def _extract_store_name(self, text: str) -> str:
        """Найти название магазина"""
        stores = {
            'пятёрочка': 'Пятёрочка',
            'метро': 'Метро',
            'ашан': 'Ашан',
            'дикси': 'Дикси',
            'окей': 'Окей',
            'magnit': 'Магнит',
            'маршал': 'Маршал'
        }
        
        text_lower = text.lower()
        for key, value in stores.items():
            if key in text_lower:
                return value
        return 'Неизвестный магазин'
    
    def _extract_items(self, text: str) -> List[Dict]:
        """Извлечь список товаров"""
        items = []
        
        # Регулярное выражение для поиска товаров и цен
        pattern = r'([\w\s]+)\s+(\d+[.,]\d{2})'
        matches = re.findall(pattern, text)
        
        for item_name, price in matches:
            items.append({
                'name': item_name.strip(),
                'price': float(price.replace(',', '.')),
                'category': self._categorize_item(item_name)
            })
        
        return items
    
    def _categorize_item(self, item_name: str) -> str:
        """Категоризация товара"""
        categories = {
            'молочка': ['молоко', 'йогурт', 'масло', 'сыр', 'кефир'],
            'мясо': ['курица', 'филе', 'говядина', 'свинина', 'колбаса'],
            'хлеб': ['хлеб', 'булка', 'батон'],
            'напитки': ['сок', 'вода', 'чай', 'кофе', 'напиток'],
            'фрукты': ['яблоко', 'банан', 'апельсин', 'груша'],
            'овощи': ['помидор', 'огурец', 'салат', 'морковь']
        }
        
        item_lower = item_name.lower()
        for category, keywords in categories.items():
            if any(keyword in item_lower for keyword in keywords):
                return category
        
        return 'прочее'
    
    def _extract_total(self, text: str) -> float:
        """Извлечь сумму"""
        # Ищем "ИТОГО:", "СУММА:", "TOTAL:" и следующее число
        pattern = r'(?:итого|сумма|total)[:\s]+(\d+[.,]\d{2})'
        match = re.search(pattern, text, re.IGNORECASE)
        
        if match:
            return float(match.group(1).replace(',', '.'))
        return 0.0
    
    def _extract_date(self, text: str) -> str:
        """Извлечь дату"""
        pattern = r'(\d{2}[./]\d{2}[./]\d{4})'
        match = re.search(pattern, text)
        return match.group(1) if match else None
    
    def _extract_time(self, text: str) -> str:
        """Извлечь время"""
        pattern = r'(\d{2}:\d{2})'
        match = re.search(pattern, text)
        return match.group(1) if match else None
    
    def _extract_address(self, text: str) -> str:
        """Извлечь адрес магазина"""
        pattern = r'(?:ул\.?|улица)\s+([\w\s.,]+)'
        match = re.search(pattern, text)
        return match.group(1) if match else None
```

**Чек-лист:**
- [ ] Парсер работает на примерах чеков
- [ ] Товары извлекаются корректно
- [ ] Сумма вычисляется правильно
- [ ] Категории определяются

---

#### ДЕНЬ 10: СР 22 ДЕКАБРЯ
**TASK-BOT-FIX-009: Интеграция анализа чеков в бота**

```python
# handlers/receipts_handler.py

from PIL import Image
import io

class ReceiptsHandler:
    def __init__(self):
        self.ocr = OCRService()
        self.parser = ReceiptParser()
        self.db = SupabaseService()
    
    async def analyze_receipt(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработать фото чека"""
        user_id = update.effective_user.id
        
        if not update.message.photo:
            await update.message.reply_text("Пожалуйста, загрузите фото чека")
            return
        
        # Скачать фото
        photo = update.message.photo[-1]
        file = await photo.get_file()
        file_path = f"/tmp/{file.file_id}.jpg"
        await file.download(file_path)
        
        # Отправить сообщение о обработке
        processing_msg = await update.message.reply_text("⏳ Анализирую чек...")
        
        try:
            # Распознать текст
            text = await self.ocr.extract_text_from_image(file_path)
            
            if not text:
                await update.message.reply_text("❌ Не удалось распознать текст. Пожалуйста, загрузите более ясное фото")
                return
            
            # Парсить структуру
            parsed = await self.parser.parse_receipt_text(text)
            
            # Сохранить в БД
            receipt = await self.db.save_receipt(
                user_id=user_id,
                store_name=parsed['store_name'],
                receipt_date=parsed['receipt_date'],
                total_sum=parsed['total_sum'],
                items=parsed['items'],
                file_path=file_path
            )
            
            # Отправить результат
            message = self._format_receipt_analysis(parsed)
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {str(e)}")
        
        finally:
            # Удалить обработанное сообщение
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=processing_msg.message_id
            )
    
    def _format_receipt_analysis(self, parsed: Dict) -> str:
        """Форматировать результат анализа"""
        message = f"✅ **Чек проанализирован:**\n\n"
        message += f"🏪 **{parsed['store_name']}**\n"
        message += f"📅 {parsed['receipt_date']} {parsed['receipt_time']}\n\n"
        
        message += "🛒 **Товары:**\n"
        total = 0
        for item in parsed['items']:
            message += f"• {item['name']} - {item['price']}₽\n"
            total += item['price']
        
        message += f"\n💰 **ИТОГО: {parsed['total_sum']}₽**\n"
        
        return message
```

**Чек-лист:**
- [ ] /receipt analyze работает
- [ ] Фото обрабатывается
- [ ] Чек сохраняется в БД
- [ ] Результат выводится правильно

---

#### ДЕНЬ 11: ЧТ 23 ДЕКАБРЯ
**TASK-BOT-FIX-010: Сравнение цен (Yandex Market API)**

```python
# services/market_service.py

import aiohttp
import os

class MarketService:
    def __init__(self):
        self.yandex_token = os.getenv('YANDEX_MARKET_API_KEY')
        self.base_url = "https://api.market.yandex.ru/v2/search"
    
    async def find_cheaper_items(self, items: List[Dict]) -> List[Dict]:
        """Найти товары дешевле в других магазинах"""
        results = []
        
        async with aiohttp.ClientSession() as session:
            for item in items:
                cheaper_options = await self._search_item(session, item)
                if cheaper_options:
                    results.append(cheaper_options)
        
        return results
    
    async def _search_item(self, session: aiohttp.ClientSession, item: Dict) -> Dict:
        """Поиск товара по названию"""
        params = {
            'text': item['name'],
            'pageId': 1
        }
        
        headers = {
            'Authorization': f'Bearer {self.yandex_token}'
        }
        
        try:
            async with session.get(
                self.base_url,
                params=params,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    
                    if data.get('search', {}).get('results'):
                        results = data['search']['results']
                        
                        # Найти самый дешевый
                        cheapest = min(results, key=lambda x: x.get('price', float('inf')))
                        
                        if cheapest['price'] < item['price']:
                            return {
                                'item_name': item['name'],
                                'original_price': item['price'],
                                'cheaper_price': cheapest['price'],
                                'savings': item['price'] - cheapest['price'],
                                'store': cheapest.get('shop', 'Unknown'),
                                'url': cheapest.get('url')
                            }
        except Exception as e:
            print(f"Error searching {item['name']}: {e}")
        
        return None
```

**Чек-лист:**
- [ ] Yandex Market API ключ установлен
- [ ] Поиск товаров работает
- [ ] Сравнение цен работает
- [ ] Рекомендации выводятся

---

#### ДЕНЬ 12-13: ПТ-ВС 24-25 ДЕКАБРЯ
**TASK-BOT-FIX-011: Дневник здоровья**

```python
# handlers/health_handler.py

class HealthHandler:
    async def record_health(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Записать в дневник здоровья"""
        user_id = update.effective_user.id
        text = update.message.text
        
        # Парсить что записал пользователь
        # Примеры:
        # - "Съел молоко"
        # - "Пошел курить"
        # - "Проехался на велосипеде"
        # - "Спал 8 часов"
        
        entry_type, data = self._parse_health_entry(text)
        
        await self.db.save_health_entry(
            user_id=user_id,
            entry_type=entry_type,
            data=data
        )
        
        if entry_type == 'food':
            emoji = "🍽️"
            category = "Еда"
        elif entry_type == 'habit':
            emoji = "🧘"
            category = "Привычка"
        elif entry_type == 'activity':
            emoji = "🚴"
            category = "Активность"
        else:
            emoji = "📝"
            category = "Запись"
        
        await update.message.reply_text(f"{emoji} Записано в дневник: {category}")
    
    def _parse_health_entry(self, text: str) -> tuple:
        """Определить тип и распарсить запись"""
        text_lower = text.lower()
        
        # Еда
        food_keywords = ['съел', 'съела', 'выпил', 'выпила', 'поел', 'попил']
        if any(kw in text_lower for kw in food_keywords):
            return 'food', {'description': text}
        
        # Привычка
        habit_keywords = ['курил', 'курила', 'пил', 'пила']
        if any(kw in text_lower for kw in habit_keywords):
            return 'habit', {'description': text}
        
        # Активность
        activity_keywords = ['пошел', 'пошла', 'проехал', 'занимался']
        if any(kw in text_lower for kw in activity_keywords):
            return 'activity', {'description': text}
        
        # Сон
        if 'спал' in text_lower or 'спала' in text_lower:
            return 'sleep', {'description': text}
        
        return 'note', {'description': text}
    
    async def health_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Вывести отчет о здоровье /health report"""
        user_id = update.effective_user.id
        
        entries = await self.db.get_health_entries(user_id, days=1)
        
        message = "📊 **ОТЧЕТ О ЗДОРОВЬЕ (Сегодня)**\n\n"
        
        if not entries:
            message += "Записей пока нет."
            await update.message.reply_text(message, parse_mode='Markdown')
            return
        
        # Группировать по типам
        by_type = {}
        for entry in entries:
            entry_type = entry['entry_type']
            if entry_type not in by_type:
                by_type[entry_type] = []
            by_type[entry_type].append(entry)
        
        for entry_type, items in by_type.items():
            if entry_type == 'food':
                message += "🍽️ **ПИТАНИЕ:**\n"
                for item in items:
                    message += f"• {item['data'].get('description', 'Неизвестно')}\n"
            elif entry_type == 'habit':
                message += "\n🧘 **ПРИВЫЧКИ:**\n"
                for item in items:
                    message += f"• {item['data'].get('description', 'Неизвестно')}\n"
            elif entry_type == 'activity':
                message += "\n💪 **АКТИВНОСТЬ:**\n"
                for item in items:
                    message += f"• {item['data'].get('description', 'Неизвестно')}\n"
        
        await update.message.reply_text(message, parse_mode='Markdown')
```

**Чек-лист:**
- [ ] /health diary работает
- [ ] Записи сохраняются
- [ ] /health report показывает данные
- [ ] Анализ работает

---

### НЕДЕЛЯ 3 (26-31 ДЕКАБРЯ): ПОЛИРОВКА И ТЕСТИРОВАНИЕ

#### ДЕНЬ 14-15: ПТ-ВС 26-27 ДЕКАБРЯ
**TASK-BOT-FIX-012: Режимы взаимодействия и настройки**

```python
# handlers/settings_handler.py

class SettingsHandler:
    async def set_mode(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Установить режим /mode [режим]"""
        if not context.args:
            modes = ['executor', 'advisor', 'silent', 'detailed']
            message = "Доступные режимы:\n"
            for mode in modes:
                message += f"• /mode {mode}\n"
            await update.message.reply_text(message)
            return
        
        mode = context.args[0].lower()
        valid_modes = ['executor', 'advisor', 'silent', 'detailed']
        
        if mode not in valid_modes:
            await update.message.reply_text(f"❌ Неизвестный режим '{mode}'")
            return
        
        user_id = update.effective_user.id
        await self.db.update_user_preferences(user_id, mode=mode)
        
        mode_descriptions = {
            'executor': 'Только выполняю задачи, без советов',
            'advisor': 'Даю рекомендации и советы',
            'silent': 'Минимум текста, только результаты',
            'detailed': 'Подробные объяснения всего'
        }
        
        message = f"✅ Режим '{mode}' активирован!\n\n"
        message += f"📝 {mode_descriptions[mode]}"
        
        await update.message.reply_text(message)
```

---

#### ДЕНЬ 16-17: ПН-ВТ 29-30 ДЕКАБРЯ
**TASK-BOT-FIX-013: Полное тестирование**

```bash
# Интеграционное тестирование

ТЕСТ 1: Проекты
✅ /start
✅ /project add "Мой первый проект"
✅ /project list
✅ Загрузить файл

ТЕСТ 2: Задачи
✅ /task add "Купить молоко"
✅ /task list
✅ /task done 1

ТЕСТ 3: Чеки
✅ Отправить фото чека
✅ /receipt analyze
✅ Проверить сравнение цен

ТЕСТ 4: Здоровье
✅ Записать "Съел молоко"
✅ /health report
✅ Проверить аналитику

ТЕСТ 5: Режимы
✅ /mode executor
✅ /mode advisor
✅ /mode silent

ТЕСТ 6: Производительность
✅ Нагрузочное тестирование
✅ Проверка памяти
✅ Проверка БД
```

**Чек-лист:**
- [ ] Все команды работают
- [ ] Нет ошибок
- [ ] БД работает
- [ ] Производительность нормальная

---

#### ДЕНЬ 18: СР 31 ДЕКАБРЯ
**TASK-BOT-FIX-014: Финальное развертывание и документация**

```bash
# Развертывание на production

1. Обновить в Kubernetes:
   kubectl apply -f k8s/bot-deployment.yaml
   kubectl rollout status deployment/digital-twin-bot

2. Проверить логи:
   kubectl logs -f deployment/digital-twin-bot

3. Запустить health check:
   curl https://97v.ru/health

4. Создать документацию:
   - BOT_USER_GUIDE.md (как пользоваться)
   - BOT_API_DOCUMENTATION.md (API для интеграций)
   - BOT_TROUBLESHOOTING.md (решение проблем)

5. Запустить полный тест:
   python run_integration_tests.py
```

---

## 📊 SUMMARY

### Что было:
✅ Инфраструктура (Kubernetes, DNS, API)
❌ Функциональность бота

### Что будет (после 1 января 2026):
✅ Инфраструктура
✅ Система проектов
✅ Управление задачами
✅ Анализ чеков
✅ Сравнение цен
✅ Дневник здоровья
✅ Режимы взаимодействия
✅ Полная документация

### KPI по окончанию:
- 🎯 14+ основных функций реализовано
- 🎯 100+ строк документации
- 🎯 80+ тестов (все зеленые)
- 🎯 0 критических ошибок
- 🎯 <100ms moyenne response time

---

## 🚀 СТАРТ РЕАЛИЗАЦИИ

**НАЧИНАЕМ: 13 ДЕКАБРЯ 2025, 22:00 MSK**

```bash
# Шаг 1: Клонировать репозиторий
git clone https://github.com/vik9541/superbrain-backend.git
cd superbrain-backend

# Шаг 2: Создать ветку
git checkout -b feature/personal-assistant-bot

# Шаг 3: Установить зависимости
pip install -r requirements.txt
pip install google-cloud-vision aiohttp python-telegram-bot supabase

# Шаг 4: Запустить первый тест
python -m pytest tests/test_handlers.py -v

# Шаг 5: Начать разработку
echo "ДЕНЬ 1: TASK-BOT-FIX-001 готов к запуску!"
```

---

**Статус:** 🟢 READY TO IMPLEMENT  
**Приоритет:** 🔴 CRITICAL  
**Deadline:** 🎯 1 ЯНВАРЯ 2026  
**Задач:** 14 (TASK-BOT-FIX-001 to 014)  

> 🚀 **ПЕРСОНАЛЬНЫЙ ПОМОЩНИК БОТ - ПОЛНАЯ РЕАЛИЗАЦИЯ!**
