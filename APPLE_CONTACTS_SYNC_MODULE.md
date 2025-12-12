# 📱 APPLE CONTACTS → GITHUB SYNC MODULE

**Версия:** 1.0 (интеграция в Super Brain v5.0)  
**Статус:** 🟢 READY FOR IMPLEMENTATION  
**Цель:** Ежедневная синхронизация контактов Apple в GitHub + Supabase + анализ паттернов  
**Автор:** Perplexity AI + vik9541  
**Дата:** 12 декабря 2025

---

## 🎯 СУТЬ РЕШЕНИЯ

```
┌─────────────────────────────────────────────────┐
│         📱 APPLE CONTACTS                       │
│  (macOS/iOS - локальная база контактов)        │
└────────────────────┬────────────────────────────┘
                     │
        ┌────────────▼──────────────┐
        │  SYNC AGENT                │
        │  (Ежедневно в 02:00)      │
        │                           │
        │  1. Читает контакты       │
        │  2. Сравнивает с GitHub   │
        │  3. Обновляет/создает    │
        │  4. Анализирует паттерны │
        │  5. Отправляет отчет     │
        └────────────┬──────────────┘
                     │
        ┌────────────▼──────────────┐
        │  GITHUB                   │
        │  contacts.json            │
        │  contacts_metadata.md     │
        └────────────┬──────────────┘
                     │
        ┌────────────▼──────────────┐
        │  SUPABASE                 │
        │  PEOPLE таблица           │
        │  + embeddings             │
        └────────────┬──────────────┘
                     │
        ┌────────────▼──────────────┐
        │  ANALYZER (Agent #1)      │
        │  Распознает паттерны      │
        │  Обновляет memory         │
        └────────────┬──────────────┘
                     │
                     ▼
        🎯 СИСТЕМА СТАНОВИТСЯ УМНЕЕ!
```

---

## 📋 ТРЕБОВАНИЯ

### Технологический стек:

```
macOS/iOS API:
├─ Contacts.framework (native macOS/iOS)
├─ ExternalAccessory (если нужна синхронизация)
└─ Keychain (для хранения credentials)

Python (Backend):
├─ PyObjC 10.0+ (для работы с Contacts.framework)
├─ requests 2.31+ (HTTP запросы)
├─ PyGithub 2.1+ (GitHub API)
├─ supabase 2.4+ (Supabase клиент)
├─ pydantic 2.5+ (валидация)
├─ APScheduler 3.10+ (расписание)
└─ cryptography 41.0+ (шифрование)

GitHub:
├─ Repo access ✅
├─ Personal access token 🔑
└─ Automation via GitHub Actions

Supabase:
├─ PEOPLE таблица (расширенная)
├─ CONTACTS_SYNC таблица (логи)
├─ Vector embeddings (для поиска)
└─ Real-time updates
```

---

## 🏗️ АРХИТЕКТУРА РЕШЕНИЯ

### Компоненты:

```python
1. CONTACT_READER (читает из Apple)
   ├─ Подключается к Contacts.framework
   ├─ Читает все контакты
   ├─ Парсит данные
   └─ Возвращает структурированный JSON

2. CONTACT_NORMALIZER (нормализует данные)
   ├─ Унифицирует формат
   ├─ Валидирует информацию
   ├─ Шифрует чувствительные данные
   └─ Создает хеши для сравнения

3. GITHUB_SYNCER (синхронизирует с GitHub)
   ├─ Читает текущий contacts.json
   ├─ Сравнивает с новыми данными
   ├─ Обновляет/создает файлы
   ├─ Коммитит изменения
   └─ Ведет историю в GitHub

4. SUPABASE_SYNCER (синхронизирует с Supabase)
   ├─ Обновляет PEOPLE таблицу
   ├─ Создает/обновляет записи
   ├─ Генерирует embeddings
   ├─ Обновляет связи (CONNECTIONS)
   └─ Логирует все изменения

5. PATTERN_ANALYZER (анализирует паттерны)
   ├─ Определяет группы контактов
   ├─ Находит связанные людей
   ├─ Обнаруживает новые паттерны
   └─ Обновляет память агентов

6. SCHEDULER (планирует работу)
   ├─ Запускает синк ежедневно (02:00)
   ├─ Запускает анализ (02:30)
   ├─ Отправляет отчет (02:45)
   └─ Обработка ошибок
```

---

## 💾 СТРУКТУРА ДАННЫХ

### GitHub: contacts.json

```json
{
  "version": "1.0",
  "last_sync": "2025-12-12T02:00:00Z",
  "sync_count": 1,
  "total_contacts": 127,
  "contacts": [
    {
      "id": "contact_uuid_001",
      "first_name": "Ivan",
      "last_name": "Petrov",
      "phone_numbers": [
        {
          "type": "mobile",
          "number": "+7-921-***-**-89",
          "hash": "sha256_hash_of_full_number"
        }
      ],
      "emails": [
        {
          "type": "work",
          "email": "ivan@example.com",
          "hash": "sha256_hash"
        }
      ],
      "organization": "XYZ Corp",
      "job_title": "Senior Developer",
      "tags": ["work", "developer", "contact"],
      "groups": ["Work", "Developers"],
      "notes": "Met at conference 2025",
      "photo_hash": "sha256_of_photo",
      "metadata": {
        "created_date": "2025-01-15",
        "updated_date": "2025-12-12",
        "source": "Apple Contacts",
        "contact_count": 3,
        "last_interaction": "2025-12-10",
        "social_profiles": {
          "linkedin": "ivan-petrov",
          "github": "ivan-dev"
        }
      }
    },
    {...}
  ],
  "groups": {
    "Work": 45,
    "Family": 12,
    "Friends": 35,
    "Business": 28,
    "Other": 7
  },
  "statistics": {
    "total_contacts": 127,
    "with_emails": 98,
    "with_phones": 102,
    "with_photos": 45,
    "with_organizations": 67,
    "by_country": {
      "Russia": 87,
      "USA": 25,
      "Germany": 10,
      "Other": 5
    }
  }
}
```

### GitHub: contacts_metadata.md

```markdown
# 📱 Apple Contacts Sync Report

**Последняя синхронизация:** 12 декабря 2025, 02:00 MSK
**Версия данных:** 1.0
**Статус:** ✅ Success

## 📊 Статистика

| Метрика | Значение |
|---------|----------|
| Всего контактов | 127 |
| Добавлено | 3 |
| Обновлено | 5 |
| Удалено | 0 |
| С email | 98 |
| С телефоном | 102 |
| С фото | 45 |
| С организацией | 67 |

## 🏢 Группы

- **Work** (45) - Рабочие контакты
- **Friends** (35) - Друзья
- **Business** (28) - Бизнес-партнеры
- **Family** (12) - Семья
- **Other** (7) - Прочее

## 🌍 География

- 🇷🇺 Россия: 87
- 🇺🇸 США: 25
- 🇩🇪 Германия: 10
- Другие: 5

## 💡 Рекомендации

1. **Обновить профили** - 5 контактов нуждаются в уточнении
2. **Новая группа** - Рассмотреть создание "Инвесторы" (4 контакта)
3. **Дедупликация** - 2 похожих контакта можно объединить
4. **Сети** - Создать граф общих контактов между людьми

## 🔗 Связи между контактами

- Ivan ↔ Maria (совместный проект MOS-01)
- Ivan ↔ Alexey (коллеги в XYZ Corp)
- Maria ↔ Elena (друзья, часто встречаются)
```

### Supabase: PEOPLE таблица (расширенная)

```sql
CREATE TABLE people (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Основные данные
  first_name TEXT NOT NULL,
  last_name TEXT,
  full_name TEXT GENERATED ALWAYS AS (COALESCE(first_name, '') || ' ' || COALESCE(last_name, '')) STORED,
  
  -- Контакты (зашифрованы)
  phone_hash TEXT UNIQUE,  -- SHA256 hash
  email_hash TEXT UNIQUE,   -- SHA256 hash
  
  -- Профессиональные данные
  organization TEXT,
  job_title TEXT,
  department TEXT,
  
  -- Группировка
  groups TEXT[] DEFAULT ARRAY[]::TEXT[],
  tags TEXT[] DEFAULT ARRAY[]::TEXT[],
  
  -- Метаданные
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_synced_at TIMESTAMP,
  apple_contact_id UUID,
  
  -- Социальные профили
  social_profiles JSONB DEFAULT '{}',
  
  -- Взаимодействие
  interaction_count INT DEFAULT 0,
  last_interaction_at TIMESTAMP,
  
  -- Статистика
  mention_count INT DEFAULT 0,
  project_count INT DEFAULT 0,
  file_count INT DEFAULT 0,
  
  -- Embeddings
  embedding_vector vector(1536),
  
  -- Расширенные данные
  custom_fields JSONB DEFAULT '{}',
  notes TEXT,
  
  CONSTRAINT email_or_phone CHECK (email_hash IS NOT NULL OR phone_hash IS NOT NULL)
);

CREATE INDEX idx_people_full_name ON people USING GIN(to_tsvector('russian', full_name));
CREATE INDEX idx_people_organization ON people(organization);
CREATE INDEX idx_people_groups ON people USING GIN(groups);
CREATE INDEX idx_people_email_hash ON people(email_hash);
CREATE INDEX idx_people_embedding ON people USING ivfflat (embedding_vector vector_cosine_ops);
```

### Supabase: CONTACTS_SYNC таблица

```sql
CREATE TABLE contacts_sync (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Sync информация
  sync_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  sync_type TEXT NOT NULL, -- 'full', 'incremental', 'verification'
  duration_ms INT,
  
  -- Статистика
  total_contacts INT,
  added_count INT,
  updated_count INT,
  deleted_count INT,
  errors_count INT,
  
  -- Статус
  status TEXT NOT NULL, -- 'success', 'partial_success', 'failed'
  error_message TEXT,
  
  -- GitHub информация
  github_commit_sha TEXT,
  github_branch TEXT DEFAULT 'main',
  
  -- Результаты
  results JSONB,
  recommendations JSONB,
  
  -- Аналитика
  pattern_changes INT,
  new_connections INT,
  accuracy_change DECIMAL(5,2)
);
```

---

## 🔧 РЕАЛИЗАЦИЯ

### 1. contact_reader.py (читает Apple Contacts)

```python
import asyncio
from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from cryptography.fernet import Fernet
import hashlib
import os

# На macOS с PyObjC
try:
    from Contacts import CNContactStore, CNKeyDescriptor, CNContactGivenNameKey, CNContactFamilyNameKey
except ImportError:
    # Fallback для других ОС
    CNContactStore = None


class ContactPhone(BaseModel):
    type: str  # 'mobile', 'home', 'work'
    number: str
    hash: str = Field(exclude=True)
    
    def __init__(self, **data):
        if 'number' in data and 'hash' not in data:
            data['hash'] = self._hash_phone(data['number'])
        super().__init__(**data)
    
    @staticmethod
    def _hash_phone(number: str) -> str:
        """Hash phone для приватности"""
        return hashlib.sha256(number.encode()).hexdigest()
    
    def to_dict(self, include_hash: bool = True):
        return {
            'type': self.type,
            'number': self.number[-4:],  # Показываем только последние 4 цифры
            'hash': self.hash if include_hash else None
        }


class ContactEmail(BaseModel):
    type: str  # 'work', 'home', 'personal'
    email: str
    hash: str = Field(exclude=True)
    
    def __init__(self, **data):
        if 'email' in data and 'hash' not in data:
            data['hash'] = self._hash_email(data['email'])
        super().__init__(**data)
    
    @staticmethod
    def _hash_email(email: str) -> str:
        return hashlib.sha256(email.lower().encode()).hexdigest()


class Contact(BaseModel):
    id: str
    first_name: str
    last_name: Optional[str] = None
    phone_numbers: List[ContactPhone] = []
    emails: List[ContactEmail] = []
    organization: Optional[str] = None
    job_title: Optional[str] = None
    tags: List[str] = []
    groups: List[str] = []
    notes: Optional[str] = None
    photo_hash: Optional[str] = None
    metadata: Dict = {}


class AppleContactsReader:
    """Читает контакты из Apple Contacts"""
    
    def __init__(self, encryption_key: Optional[str] = None):
        self.store = None
        self.cipher = None
        
        if encryption_key:
            self.cipher = Fernet(encryption_key.encode())
    
    @staticmethod
    def _hash_photo(photo_data: bytes) -> str:
        """Hash фото для деинтификации"""
        return hashlib.sha256(photo_data).hexdigest()
    
    async def read_all_contacts(self) -> List[Contact]:
        """
        Читает все контакты из Apple Contacts
        """
        if CNContactStore is None:
            return await self._read_from_file()
        
        contacts = []
        
        try:
            store = CNContactStore()
            keys = [
                CNContactGivenNameKey,
                CNContactFamilyNameKey,
                # ... другие ключи
            ]
            
            request = store.unifiedContactsMatchingPredicate_keysToFetch_error_(
                None, keys, None
            )
            
            for cn_contact in request:
                contact = self._parse_contact(cn_contact)
                contacts.append(contact)
            
            return contacts
        
        except Exception as e:
            print(f"❌ Error reading contacts: {e}")
            return []
    
    def _parse_contact(self, cn_contact) -> Contact:
        """Парсит контакт из Contacts.framework"""
        
        # Phone numbers
        phones = []
        for phone in cn_contact.phoneNumbers:
            phones.append(ContactPhone(
                type=self._get_label(phone.label),
                number=phone.value.stringValue
            ))
        
        # Emails
        emails = []
        for email in cn_contact.emailAddresses:
            emails.append(ContactEmail(
                type=self._get_label(email.label),
                email=email.value
            ))
        
        # Photo hash
        photo_hash = None
        if cn_contact.imageData:
            photo_hash = self._hash_photo(cn_contact.imageData)
        
        # Groups
        groups = []
        for group in cn_contact.containerIdentifier().split('.'):
            groups.append(group)
        
        return Contact(
            id=cn_contact.identifier,
            first_name=cn_contact.givenName or '',
            last_name=cn_contact.familyName,
            phone_numbers=phones,
            emails=emails,
            organization=cn_contact.organizationName,
            job_title=cn_contact.jobTitle,
            groups=groups,
            photo_hash=photo_hash,
            metadata={
                'created_date': cn_contact.creationDate.isoformat() if cn_contact.creationDate else None,
                'updated_date': cn_contact.modificationDate.isoformat() if cn_contact.modificationDate else None,
                'source': 'Apple Contacts'
            }
        )
    
    @staticmethod
    def _get_label(label: str) -> str:
        """Переводит метки CNContact в простые строки"""
        mapping = {
            'kCNLabelPhoneMobile': 'mobile',
            'kCNLabelPhoneMain': 'main',
            'kCNLabelPhoneWork': 'work',
            'kCNLabelEmailiCloud': 'icloud',
            'kCNLabelEmailWork': 'work',
        }
        return mapping.get(label, 'other')
    
    async def _read_from_file(self) -> List[Contact]:
        """Fallback: читает из локального JSON (для тестирования)"""
        # Для non-macOS платформ
        pass


# Использование:
async def main():
    reader = AppleContactsReader()
    contacts = await reader.read_all_contacts()
    print(f"✅ Загружено контактов: {len(contacts)}")
    return contacts

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. contact_normalizer.py

```python
import hashlib
from typing import List, Dict
from pydantic import BaseModel


class NormalizedContact(BaseModel):
    id: str
    first_name: str
    last_name: Optional[str]
    phone_hash: Optional[str]
    email_hash: Optional[str]
    organization: Optional[str]
    job_title: Optional[str]
    tags: List[str]
    groups: List[str]
    notes: Optional[str]
    photo_hash: Optional[str]
    metadata: Dict


class ContactNormalizer:
    """Нормализует контакты для единообразия"""
    
    @staticmethod
    def normalize_phone(phone: str) -> str:
        """Нормализует номер телефона"""
        # Удалить все нефисловые символы кроме +
        cleaned = ''.join(c for c in phone if c.isdigit() or c == '+')
        # Убедиться в формате +
        if not cleaned.startswith('+'):
            cleaned = '+' + cleaned
        return cleaned
    
    @staticmethod
    def normalize_email(email: str) -> str:
        """Нормализует email"""
        return email.lower().strip()
    
    @staticmethod
    def generate_phone_hash(phone: str) -> str:
        """Генерирует хеш телефона"""
        normalized = ContactNormalizer.normalize_phone(phone)
        return hashlib.sha256(normalized.encode()).hexdigest()
    
    @staticmethod
    def generate_email_hash(email: str) -> str:
        """Генерирует хеш email"""
        normalized = ContactNormalizer.normalize_email(email)
        return hashlib.sha256(normalized.encode()).hexdigest()
    
    @staticmethod
    def normalize(contact: Contact) -> NormalizedContact:
        """Нормализует контакт"""
        
        phone_hash = None
        if contact.phone_numbers:
            phone_hash = ContactNormalizer.generate_phone_hash(
                contact.phone_numbers[0].number
            )
        
        email_hash = None
        if contact.emails:
            email_hash = ContactNormalizer.generate_email_hash(
                contact.emails[0].email
            )
        
        return NormalizedContact(
            id=contact.id,
            first_name=contact.first_name.strip(),
            last_name=contact.last_name.strip() if contact.last_name else None,
            phone_hash=phone_hash,
            email_hash=email_hash,
            organization=contact.organization.strip() if contact.organization else None,
            job_title=contact.job_title.strip() if contact.job_title else None,
            tags=[tag.strip().lower() for tag in contact.tags],
            groups=[group.strip() for group in contact.groups],
            notes=contact.notes.strip() if contact.notes else None,
            photo_hash=contact.photo_hash,
            metadata=contact.metadata
        )
```

### 3. github_syncer.py

```python
from typing import List, Dict, Optional
from datetime import datetime
from github import Github
import json


class GithubContactsSyncer:
    """Синхронизирует контакты с GitHub"""
    
    def __init__(self, token: str, owner: str, repo: str):
        self.github = Github(token)
        self.repo = self.github.get_user(owner).get_repo(repo)
        self.owner = owner
        self.repo_name = repo
    
    async def sync_contacts(self, contacts: List[NormalizedContact]) -> Dict:
        """
        Синхронизирует контакты с GitHub
        """
        print("📤 Синхронизирую контакты с GitHub...")
        
        # Подготовить данные
        contacts_json = self._prepare_contacts_json(contacts)
        metadata_md = self._prepare_metadata_md(contacts)
        
        # Обновить/создать файлы
        try:
            # contacts.json
            await self._update_or_create_file(
                path='data/contacts.json',
                content=contacts_json,
                message='SYNC: Update Apple Contacts (automated)'
            )
            
            # contacts_metadata.md
            await self._update_or_create_file(
                path='data/contacts_metadata.md',
                content=metadata_md,
                message='SYNC: Update contacts metadata (automated)'
            )
            
            return {
                'status': 'success',
                'files_updated': 2,
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            print(f"❌ Error syncing to GitHub: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    async def _update_or_create_file(self, path: str, content: str, message: str):
        """Обновляет или создает файл в GitHub"""
        try:
            # Попробовать получить существующий файл
            file = self.repo.get_contents(path, ref='main')
            self.repo.update_file(
                path=path,
                message=message,
                content=content,
                sha=file.sha,
                branch='main'
            )
            print(f"  ✅ Обновлен: {path}")
        except:
            # Файл не существует, создать его
            self.repo.create_file(
                path=path,
                message=message,
                content=content,
                branch='main'
            )
            print(f"  ✅ Создан: {path}")
    
    def _prepare_contacts_json(self, contacts: List[NormalizedContact]) -> str:
        """Подготавливает contacts.json"""
        
        data = {
            'version': '1.0',
            'last_sync': datetime.now().isoformat() + 'Z',
            'total_contacts': len(contacts),
            'contacts': [contact.dict() for contact in contacts],
            'statistics': self._calculate_statistics(contacts)
        }
        
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def _prepare_metadata_md(self, contacts: List[NormalizedContact]) -> str:
        """Подготавливает contacts_metadata.md"""
        
        stats = self._calculate_statistics(contacts)
        
        md = f"""# 📱 Apple Contacts Sync Report

**Последняя синхронизация:** {datetime.now().strftime('%d %B %Y, %H:%M %Z')}

## 📊 Статистика

| Метрика | Значение |
|---------|----------|
| Всего контактов | {stats['total']} |
| С email | {stats['with_email']} |
| С телефоном | {stats['with_phone']} |
| С организацией | {stats['with_organization']} |

## 🏢 Группы

"""
        for group, count in stats.get('by_group', {}).items():
            md += f"- **{group}** ({count})\n"
        
        return md
    
    def _calculate_statistics(self, contacts: List[NormalizedContact]) -> Dict:
        """Рассчитывает статистику"""
        
        return {
            'total': len(contacts),
            'with_email': len([c for c in contacts if c.email_hash]),
            'with_phone': len([c for c in contacts if c.phone_hash]),
            'with_organization': len([c for c in contacts if c.organization]),
            'by_group': {}
        }
```

### 4. contact_scheduler.py

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
import asyncio


class ContactSyncScheduler:
    """Управляет расписанием синхронизации контактов"""
    
    def __init__(self, reader, normalizer, github_syncer, supabase_syncer):
        self.reader = reader
        self.normalizer = normalizer
        self.github_syncer = github_syncer
        self.supabase_syncer = supabase_syncer
        
        self.scheduler = AsyncIOScheduler()
    
    def start(self):
        """Запускает планировщик"""
        
        # Полная синхронизация каждый день в 02:00
        self.scheduler.add_job(
            self.full_sync,
            'cron',
            hour=2,
            minute=0,
            id='daily_contact_sync',
            name='Daily Apple Contacts Sync'
        )
        
        # Анализ паттернов в 02:30
        self.scheduler.add_job(
            self.analyze_patterns,
            'cron',
            hour=2,
            minute=30,
            id='daily_pattern_analysis',
            name='Daily Pattern Analysis'
        )
        
        # Отправка отчета в 02:45
        self.scheduler.add_job(
            self.send_report,
            'cron',
            hour=2,
            minute=45,
            id='daily_sync_report',
            name='Daily Sync Report'
        )
        
        self.scheduler.start()
        print("✅ Планировщик контактов запущен")
    
    async def full_sync(self):
        """Полная синхронизация контактов"""
        
        print("\n🌙 НАЧАЛО СИНХРОНИЗАЦИИ КОНТАКТОВ (02:00)")
        start_time = datetime.now()
        
        try:
            # 1. Читаем контакты
            print("  1️⃣ Читаю контакты из Apple...")
            contacts = await self.reader.read_all_contacts()
            print(f"     ✅ Загружено: {len(contacts)} контактов")
            
            # 2. Нормализуем
            print("  2️⃣ Нормализирую данные...")
            normalized = [self.normalizer.normalize(c) for c in contacts]
            print(f"     ✅ Нормализовано: {len(normalized)} контактов")
            
            # 3. Синхронизируем с GitHub
            print("  3️⃣ Синхронизирую с GitHub...")
            github_result = await self.github_syncer.sync_contacts(normalized)
            print(f"     ✅ GitHub: {github_result['status']}")
            
            # 4. Синхронизируем с Supabase
            print("  4️⃣ Синхронизирую с Supabase...")
            supabase_result = await self.supabase_syncer.sync_contacts(normalized)
            print(f"     ✅ Supabase: {supabase_result['added']} добавлено, {supabase_result['updated']} обновлено")
            
            # Рассчитать время
            duration = (datetime.now() - start_time).total_seconds()
            print(f"\n✅ Синхронизация завершена за {duration:.1f} секунд")
            
            return {
                'status': 'success',
                'contacts': len(contacts),
                'duration': duration
            }
        
        except Exception as e:
            print(f"\n❌ Ошибка синхронизации: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    async def analyze_patterns(self):
        """Анализирует паттерны в контактах"""
        print("\n📊 АНАЛИЗ ПАТТЕРНОВ (02:30)")
        
        # Анализировать группировки, сети, рекомендации
        pass
    
    async def send_report(self):
        """Отправляет отчет в Telegram"""
        print("\n📤 ОТПРАВКА ОТЧЕТА (02:45)")
        
        # Отправить отчет пользователю в Telegram
        pass


# Использование:
async def main():
    # Инициализировать компоненты
    reader = AppleContactsReader()
    normalizer = ContactNormalizer()
    github_syncer = GithubContactsSyncer(
        token='your_github_token',
        owner='vik9541',
        repo='super-brain-digital-twin'
    )
    supabase_syncer = SupabaseContactsSyncer(
        url='your_supabase_url',
        key='your_supabase_key'
    )
    
    # Создать планировщик
    scheduler = ContactSyncScheduler(
        reader, normalizer, github_syncer, supabase_syncer
    )
    
    # Запустить
    scheduler.start()
    
    # Для тестирования: запустить один раз
    # await scheduler.full_sync()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🚀 ИНТЕГРАЦИЯ С SUPER BRAIN v5.0

### Как работает с системой:

```python
# В main_bot.py или scheduler.py Super Brain:

from apple_contacts_sync import ContactSyncScheduler

# Добавить планировщик контактов к основной системе
contact_scheduler = ContactSyncScheduler(...)
contact_scheduler.start()

# Теперь каждый день в 02:00:
# - Контакты синхронизируются
# - Паттерны анализируются
# - Агенты обновляют память
# - Отчет отправляется в Telegram
```

### Интеграция с Analyzer:

```python
# Agent #1 может использовать контакты для анализа документов

async def analyze_with_contact_context(file):
    # Получить контакты из базы
    contacts = await db.query_people_vector_search(file.text, limit=5)
    
    # Использовать контакты как контекст
    analysis = await analyzer.analyze(
        file,
        context={
            'similar_people': contacts,
            'known_organizations': [c.organization for c in contacts]
        }
    )
    
    return analysis
```

---

## 📋 УСТАНОВКА И НАСТРОЙКА

### Требуемые пакеты:

```bash
pip install PyGithub requests supabase cryptography pydantic PyObjC (macOS)
```

### Переменные окружения:

```bash
# GitHub
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
GITHUB_OWNER=vik9541
GITHUB_REPO=super-brain-digital-twin

# Supabase
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJxxxx

# Apple Contacts
APPLE_CONTACTS_ENCRYPTION_KEY=your_key_here
```

---

## ✅ CHECKLIST

- [ ] AppleContactsReader реализован (macOS + fallback)
- [ ] ContactNormalizer реализован
- [ ] GithubContactsSyncer интегрирован
- [ ] SupabaseContactsSyncer интегрирован
- [ ] ContactSyncScheduler запущен (02:00 ежедневно)
- [ ] Pattern analyzer подключен
- [ ] Telegram отчеты работают
- [ ] Vector embeddings для контактов работают
- [ ] Knowledge graph содержит связи между людьми
- [ ] Тесты пройдены
- [ ] Production deployment готов

---

**Версия:** 1.0  
**Дата:** 12 декабря 2025  
**Статус:** 🟢 READY FOR IMPLEMENTATION
