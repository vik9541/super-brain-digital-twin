# 🏗️ SUPER BRAIN MODULAR ARCHITECTURE STANDARD
**Version:** 1.0
**Status:** ACTIVE
**Philosophy:** "Infinite Scalability via Standardization"

---

## 1. THE MODULE PHILOSOPHY
Super Brain — это не монолит. Это набор независимых, но интегрированных **Модулей**.
Каждая новая идея (как Contact Intelligence) — это отдельный модуль.
Каждый модуль должен быть **самодостаточным**: иметь своё ТЗ, свои схемы БД, свои API эндпоинты и свои тесты.

---

## 2. DIRECTORY STRUCTURE (The Standard)

Все будущие расширения должны следовать этой структуре:

```text
/modules
  ├── /_templates/                # 🆕 Шаблоны для быстрого старта
  │   ├── TZ_TEMPLATE.md
  │   ├── SCHEMA_TEMPLATE.sql
  │   └── SERVICE_SKELETON.py
  │
  ├── /contact_intelligence/      # 🟢 Пример (Текущий модуль)
  │   ├── 00_SPECIFICATION.md     # Главное ТЗ модуля
  │   ├── 01_SCENARIOS.md         # Пользовательские сценарии (Use Cases)
  │   ├── database/
  │   │   └── schema.sql          # SQL миграции
  │   ├── api/
  │   │   ├── main.py             # FastAPI сервис
  │   │   └── models.py           # Pydantic модели
  │   ├── workflows/
  │   │   └── ingestion.json      # n8n экспорты
  │   └── tests/                  # Тесты модуля
  │
  ├── /finance_tracker/           # 🟡 Пример будущего модуля
  │   ├── 00_SPECIFICATION.md
  │   └── ...
  │
  └── /health_monitor/            # 🟣 Пример будущего модуля
      ├── 00_SPECIFICATION.md
      └── ...
```

---

## 3. DOCUMENTATION STANDARDS

### 📄 00_SPECIFICATION.md (The "What" & "How")
Каждый модуль обязан иметь этот файл.
**Структура:**
1. **Executive Summary**: Зачем это нужно?
2. **Architecture Diagram**: Mermaid график.
3. **Data Security**: Как защищены данные?
4. **Database Schema**: Описание таблиц.
5. **Integration Points**: Какие вебхуки/API используются.

### 🎬 01_SCENARIOS.md (The "User Story")
Описывает, как пользователь взаимодействует с модулем.
**Пример:**
> **Scenario A: Urgent Message**
> 1. Nikita sends: "We need to fix this NOW!"
> 2. System detects `Urgency: Critical`.
> 3. System sends alert to Owner's private channel.
> 4. System drafts reply: "On it. Give me 10 mins."

---

## 4. DATABASE NAMESPACING
Чтобы избежать конфликтов в Supabase, используйте префиксы.

- **Таблицы:** `{module_name}_{table_name}`
  - Пример: `contact_interactions`, `finance_transactions`
- **Buckets:** `{module_name}-assets`
  - Пример: `contact-voice-notes`

---

## 5. API ROUTING STANDARD
Все модули подключаются к главному API Gateway через префиксы.

- **URL Pattern:** `/api/v1/modules/{module_name}/{action}`
- **Пример:**
  - `POST /api/v1/modules/contact/ingest`
  - `GET /api/v1/modules/finance/balance`

---

## 6. DEPLOYMENT STRATEGY
Модули могут деплоиться как:
1. **Part of Core:** Импортируются в главный `main.py` (для тесной интеграции).
2. **Microservice:** Отдельный Docker контейнер (для тяжелых задач).

*По умолчанию используем стратегию **Part of Core** для простоты поддержки, пока модуль не станет слишком большим.*
