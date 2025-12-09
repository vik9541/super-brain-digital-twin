# TASK-PRD-03: Обновление Kubernetes Secrets на production

**Status:** 🚨 UPDATED - New clear instructions  
**Deadline:** 48 часов с 8 декабря 2025 (до 10 декабря 10:00 MSK)  
**Ответственный:** INFRA Team  
**Связано с:** Issue #37  
**GitHub Issue:** https://github.com/vik9541/super-brain-digital-twin/issues/37

---

## 🔛 ГЛАВНАЯ ИНСТРУКЦИЯ: ИСПОЛЬЗУЙ ЭТОТ ДОКУМЕНТ

**ДА ВСЕ ОТВЕТЫ ЗДЕСЬ:**  
👉 https://github.com/vik9541/super-brain-digital-twin/blob/main/SUPABASE_PROJECTS_CLARITY.md

**ПРОЧИТАЙ ЭТО СНАЧАЛА!** Это полный справочник со скриншотами и прямыми ссылками.

---

## 📎 КРАТКОЕ РЕЗЮМЕ ЧТО НУЖНО СДЕЛАТЬ

### 1️⃣ На Supabase (https://supabase.com/dashboard/organizations)

```
✅ Открыть организацию: Vëktor_Base_2025
✅ Выбрать проект: Knowledge_DBnanoAWS
   └─ Project ID: lvixtpatqrtuwhygtpjx ← ЭТО ПРАВИЛЬНЫЙ!
✅ Скопировать учетные данные из Settings
```

### 2️⃣ В Kubernetes (kubectl commands)

```
✅ Создать/обновить secret: digital-twin-secrets
✅ Заполнить все 6 параметров
✅ Проверить что secret создался
```

### 3️⃣ Результат

```
✅ Issue #38 может начаться (развертывание API)
```

---

## 📊 ПОЛНЫЙ CHECKLIST

### ПШАГ-1: Получить учетные данные из Supabase

**URL для копирования данных:**

#### ОТ ВСЕ ЗНАЧЕНИЯ ОТСЮДА:
```
https://supabase.com/dashboard/project/lvixtpatqrtuwhygtpjx/settings/api
```

**Что скопировать:**

- [ ] 🔐 **SUPABASE_URL** (API URL section)
  ```
  https://lvixtpatqrtuwhygtpjx.supabase.co
  ```
  - [ ] Убедиться что это именно `.supabase.co` (не `.supabase.io`)
  - [ ] Убедиться что это Project ID: `lvixtpatqrtuwhygtpjx`
  - [ ] Убедиться что это Project Name: `Knowledge_DBnanoAWS`

- [ ] 🔐 **SUPABASE_KEY** (service_role secret key)
  ```
  eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  ```
  - [ ] ⚠️ КОПИ РОВ **service_role key**, НЕ anon key!
  - [ ] Это должна быть ДЛИННАЯ строка (200+ символов)
  - [ ] Начинается с `eyJ...`

- [ ] 🔐 **SUPABASE_JWT_SECRET** (JWT Secret)
  ```
  super-secret-jwt-token-1234567890
  ```
  - [ ] Расположен в том же разделе (API Settings)
  - [ ] Это может быть короче (обычно 30-50 символов)

#### ОТ ЭТ СТРАНИЦЫ:
```
https://supabase.com/dashboard/project/lvixtpatqrtuwhygtpjx/settings/database
```

**Что скопировать:**

- [ ] 🔐 **SUPABASE_DB_HOST**
  ```
  db.lvixtpatqrtuwhygtpjx.supabase.co
  ```
  - [ ] Начинается с `db.`
  - [ ] Заканчивается на `.supabase.co`
  - [ ] Содержит Project ID: `lvixtpatqrtuwhygtpjx`

- [ ] 🔐 **SUPABASE_DB_USER**
  ```
  postgres
  ```
  - [ ] Обычно это `postgres`

- [ ] 🔐 **SUPABASE_DB_PASSWORD**
  ```
  [Your secure password]
  ```
  - [ ] Находится в Database Settings
  - [ ] Если не помнишь, можно сбросить (Reset Password)

---

## 📄 COPY-PASTE БЛОК ДЛЯ KUBECTL

### Шаг 1: Установи переменные (замени значения)

```bash
# Скопируй это в терминал и замени [ЗНАЧЕНИЯ] на реальные из Supabase

export SUPABASE_URL="https://lvixtpatqrtuwhygtpjx.supabase.co"
export SUPABASE_KEY="[СКОПИРОВАТЬ service_role key ИЗ SUPABASE]"
export SUPABASE_DB_HOST="db.lvixtpatqrtuwhygtpjx.supabase.co"
export SUPABASE_DB_USER="postgres"
export SUPABASE_DB_PASSWORD="[СКОПИРОВАТЬ пароль ИЗ DATABASE SETTINGS]"
export SUPABASE_JWT_SECRET="[СКОПИРОВАТЬ JWT Secret ИЗ API SETTINGS]"

# Проверь что все переменные установлены
echo "URL: $SUPABASE_URL"
echo "HOST: $SUPABASE_DB_HOST"
# (остальные не выводим для безопасности)
```

### Шаг 2: Создай secret в Kubernetes

```bash
# Скопируй это целиком (работает только после шага 1)

kubectl create secret generic digital-twin-secrets \
  --from-literal=SUPABASE_URL="$SUPABASE_URL" \
  --from-literal=SUPABASE_KEY="$SUPABASE_KEY" \
  --from-literal=SUPABASE_DB_HOST="$SUPABASE_DB_HOST" \
  --from-literal=SUPABASE_DB_USER="$SUPABASE_DB_USER" \
  --from-literal=SUPABASE_DB_PASSWORD="$SUPABASE_DB_PASSWORD" \
  --from-literal=SUPABASE_JWT_SECRET="$SUPABASE_JWT_SECRET" \
  -n production \
  --dry-run=client -o yaml | kubectl apply -f -
```

### Шаг 3: Проверь что secret создался

```bash
# Посмотри что secret существует
kubectl get secrets -n production

# Должно вывести:
# NAME                    TYPE                  DATA   AGE
# digital-twin-secrets    Opaque                6      5s

# Посмотри детали
kubectl describe secret digital-twin-secrets -n production

# Должны быть 6 ключей:
# SUPABASE_DB_HOST
# SUPABASE_DB_PASSWORD
# SUPABASE_DB_USER
# SUPABASE_JWT_SECRET
# SUPABASE_KEY
# SUPABASE_URL
```

---

## ⚠️ ВАЖНЫЕ НАПОМИНАНИЯ

### ❌ НЕ ДЕЛАЙ ЭТО:

```
❌ НЕ используй Project ID: hbdrmgtcvlwjcecptfxd (deprecated)
❌ НЕ используй Project: InternetMagazin (это для 97k.ru)
❌ НЕ копируй anon key (используй service_role)
❌ НЕ используй старый URL с .supabase.io (используй .supabase.co)
❌ НЕ забудь db. в начале DB_HOST
❌ НЕ копируй с лишними пробелами или переводами строк
```

### ✅ ДЕЛАЙ ЭТО:

```
✅ Используй Project ID: lvixtpatqrtuwhygtpjx (Knowledge_DBnanoAWS)
✅ Используй Project: Knowledge_DBnanoAWS
✅ Копируй service_role key (это один из API keys)
✅ Используй современный URL с .supabase.co
✅ Начни DB_HOST с db.
✅ Копируй точные значения без пробелов
```

---

## 🔗 ПРЯМЫЕ ССЫЛКИ

### Для копирования данных:
1. **API Keys:** https://supabase.com/dashboard/project/lvixtpatqrtuwhygtpjx/settings/api
2. **Database:** https://supabase.com/dashboard/project/lvixtpatqrtuwhygtpjx/settings/database
3. **Полный справочник:** https://github.com/vik9541/super-brain-digital-twin/blob/main/SUPABASE_PROJECTS_CLARITY.md

### GitHub:
- **Это Issue:** https://github.com/vik9541/super-brain-digital-twin/issues/37
- **Репозиторий:** https://github.com/vik9541/super-brain-digital-twin

---

## 💰 ОТЧЕТ (После выполнения)

После выполнения задокументировать:

- [ ] Дата/время обновления: ____________
- [ ] Команда выполняющая: ____________
- [ ] Namespace куда обновили: `production`
- [ ] Secret name: `digital-twin-secrets`
- [ ] Все 6 ключей присутствуют: ✅
- [ ] Проверка прошла успешно:
  ```bash
  kubectl describe secret digital-twin-secrets -n production
  # [Вывод команды]
  ```
- [ ] Возможные проблемы: ____________
- [ ] Готовность к Issue #38: ✅ ДА / ❌ НЕТ

---

## 📞 ПОМОЩЬ ПРИ ОШИБКАХ

### Ошибка: "Secret already exists"

**Решение:**
```bash
# Удали старый secret
kubectl delete secret digital-twin-secrets -n production

# Создай новый (повтори шаг 2)
```

### Ошибка: "Permission denied"

**Проверь:**
- [ ] Есть ли доступ к production namespace?
- [ ] Установлен ли kubeconfig?
- [ ] Правильный ли кластер? (`kubectl config current-context`)

### Ошибка: "Project not found in Supabase"

**Проверь:**
- [ ] Используешь ли ты правильный Project ID: `lvixtpatqrtuwhygtpjx`?
- [ ] Правильный ли URL: `https://supabase.com/dashboard/project/lvixtpatqrtuwhygtpjx`?
- [ ] Залогинен ли в Supabase аккаунт?

### Ошибка: "Invalid API key"

**Проверь:**
- [ ] Скопировал ли ты **service_role key** (не anon)?
- [ ] Нет ли лишних пробелов в начале/конце?
- [ ] Полная ли строка скопирована (должна быть длинная)?

---

## 🎯 ОТВЕТСТВЕННОСТЬ

**Issue Owner:** INFRA Team  
**Deadline:** 10 декабря 2025, 10:00 MSK  
**Blocking:** Issue #38 (Cannot start until this is done)  
**Duration:** ~30 minutes (если есть доступ)

---

## 📌 СТАТУС

```
❌ Требует Supabase доступ: ДА
❌ Требует Kubernetes доступ: ДА
❌ Требует GitHub доступ: НЕТ
🟡 Статус: READY FOR EXECUTION
🔗 Зависит от: Issue #36 (Docker images ready)
```

---

**ГЛАВНЫЙ ДОКУМЕНТ ДЛЯ СПРАВКИ:**  
https://github.com/vik9541/super-brain-digital-twin/blob/main/SUPABASE_PROJECTS_CLARITY.md

**При любых вопросах читай этот документ!**
