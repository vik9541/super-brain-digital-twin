# MASTER_README.md - UPDATED (Dec 9, 2025)

## 🧭 ГЛАВНАЯ НАВИГАЦИЯ ПО ПРОЕКТУ

**НОВАЯ СЕКЦИЯ ДОБАВЛЕНА:** `Supabase Projects Clarity`

Если тебе нужно понять **какой Supabase проект используется**, **где брать API ключи**, **какой Project ID правильный** и **как обновлять Kubernetes Secrets** —

👉 **ВСЕ ОТВЕТЫ ЗДЕСЬ:** [`SUPABASE_PROJECTS_CLARITY.md`](./SUPABASE_PROJECTS_CLARITY.md)

ЭТО ГЛАВНЫЙ ДОКУМЕНТ по Supabase. Если старая документация где-то расходится с ним — **считать правильным ИМЕННО ЕГО.**

---

## 🔗 КЛЮЧЕВЫЕ ДОКУМЕНТЫ

- `SUPABASE_PROJECTS_CLARITY.md` — полный справочник по Supabase проектам (97v.ru vs 97k.ru)
- `TASK-PRD-03-UPDATED.md` — новое ТЗ по обновлению Kubernetes Secrets (production)
- `CREDENTIALS_MANAGEMENT.md` — общая логика по управлению секретами
- `PROJECT_STATUS.md` — статус проекта
- `CHECKLIST.md` — общий чеклист

---

## 🧱 СТРУКТУРА SUPABASE

Сейчас в организации **Vëktor_Base_2025** два проекта:

1. `Knowledge_DBnanoAWS` → **Super Brain / 97v.ru / Project ID: lvixtpatqrtuwhygtpjx**  
2. `InternetMagazin` → **Интернет-магазин / 97k.ru / Project ID: bvspfvshgpidpbhkvykb**

ВСЕ, что относится к **super-brain-digital-twin**, должно использовать **ТОЛЬКО**:

```text
Project: Knowledge_DBnanoAWS
Project ID: lvixtpatqrtuwhygtpjx
Region: eu-central-1
```

Подробности и все ссылки → в `SUPABASE_PROJECTS_CLARITY.md`.
