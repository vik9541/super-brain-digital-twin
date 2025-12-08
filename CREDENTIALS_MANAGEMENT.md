# 🔐 УПРАВЛЕНИЕ СЕКРЕТАМИ И ТОКЕНАМИ

**Версия:** 2.1 (Production Fix)  
**Дата:** 8 декабря 2025  
**Статус:** ✅ Production Ready  

---

## 📋 СОДЕРЖАНИЕ

1. [Уровни безопасности](#уровни-безопасности)
2. [Где хранить каждый токен](#где-хранить-каждый-токен)
3. [Как добавлять токены](#как-добавлять-токены)
4. [GitHub Secrets](#github-secrets)
5. [Локальное хранилище](#локальное-хранилище)
6. [Kubernetes Secrets](#kubernetes-secrets)
7. [Ротация токенов](#ротация-токенов)
8. [Безопасность и аудит](#безопасность-и-аудит)

---

## 🔐 УРОВНИ БЕЗОПАСНОСТИ

### Уровень 1: Разработка (Local Development)
```
✅ Место:        CREDENTIALS/.env (локально)
✅ Видимость:    Только ваша машина (в .gitignore)
✅ Используется: Локальная разработка
✅ Риск:         Средний (машина должна быть защищена)
✅ Доступ:       Только разработчик
```

### Уровень 2: CI/CD Pipeline (GitHub Actions)
```
✅ Место:        GitHub Settings → Secrets and variables
✅ Видимость:    Зашифрованы GitHub
✅ Используется: GitHub Actions workflows
✅ Риск:         Низкий (GitHub шифрует все)
✅ Доступ:       GitHub Actions + Admin доступ
```

### Уровень 3: Production (Kubernetes)
```
✅ Место:        K8s Secrets в namespace production
✅ Видимость:    etcd зашифрован
✅ Используется: Pod'ы в production
✅ Риск:         Очень низкий (etcd encryption)
✅ Доступ:       RBAC controlled
```

### Уровень 4: Team Access (Optional)
```
✅ Место:        1Password / Bitwarden / LastPass
✅ Видимость:    End-to-End зашифрована
✅ Используется: Командный доступ
✅ Риск:         Минимальный (E2E encryption)
✅ Доступ:       Выбранные члены команды
```

---

## 📍 ГДЕ ХРАНИТЬ КАЖДЫЙ ТОКЕН

### DigitalOcean API Token
```
🎯 Локально:        CREDENTIALS/.env → DO_API_TOKEN
🎯 GitHub Secrets:  DO_API_TOKEN_PROD
🎯 K8s Secret:      digital-twin-secrets → do-api-token
🎯 Ротация:         Каждые 90 дней
⚠️  КРИТИЧНО:       НИКОГДА не выкладывай в GitHub
```

### Kubernetes Kubeconfig
```
🎯 Локально:        ~/.kube/config-super-brain-prod
🎯 GitHub Secrets:  KUBECONFIG_PROD (base64 encoded)
🎯 K8s Secret:      kubernetes-config (NEVER!)
🎯 Ротация:         При обновлении K8s версии
⚠️  КРИТИЧНО:       НИКОГДА не коммитить
```

### Supabase Credentials (3 типа)
```
# Production: Knowledge_DBnanoAWS (lvixtpatqrtuwnygtpjx, eu-central-1)
# Staging: internetMagazinmicroAWS (bvspfvshgpidpbhkvykb, eu-west-1)

🎯 ANON KEY:
   Локально:       CREDENTIALS/.env → SUPABASE_ANON_KEY
   GitHub Secrets: SUPABASE_ANON_KEY
   K8s Secret:     supabase-credentials
   
🎯 SERVICE ROLE KEY:
   Локально:       CREDENTIALS/.env → SUPABASE_SERVICE_ROLE_KEY
   GitHub Secrets: SUPABASE_SERVICE_ROLE_KEY
   K8s Secret:     supabase-credentials
   
🎯 DB PASSWORD:
   Локально:       CREDENTIALS/.env → SUPABASE_DB_PASSWORD
   GitHub Secrets: SUPABASE_DB_PASSWORD
   K8s Secret:     supabase-db-password
```

### Telegram Bot Token
```
🎯 Локально:        CREDENTIALS/.env → TELEGRAM_BOT_TOKEN
🎯 GitHub Secrets:  TELEGRAM_BOT_TOKEN
🎯 K8s Secret:      telegram-credentials
🎯 Ротация:         Только при компрометации
⚠️  КРИТИЧНО:       Никогда не деббюгить в логах
```

### N8N Webhooks
```
🎯 Локально:        CREDENTIALS/.env → N8N_WEBHOOK_URL + workflow IDs
🎯 GitHub Secrets:  N8N_WEBHOOK_URL, N8N_WORKFLOW_IDS
🎯 K8s Secret:      n8n-webhooks
🎯 Ротация:         Не требуется (внутренние)
⚠️  КРИТИЧНО:       Workflow IDs должны быть тайными
```

### Docker Registry Token
```
🎯 Локально:        CREDENTIALS/.env → DO_REGISTRY_TOKEN
🎯 GitHub Secrets:  DO_REGISTRY_TOKEN
🎯 K8s Secret:      do-registry (docker-registry type)
🎯 Ротация:         Каждые 180 дней
⚠️  КРИТИЧНО:       Нужен для pull образов из DO Registry
```

---

## ✅ КАК ДОБАВЛЯТЬ ТОКЕНЫ

### Шаг 1: Создать/Получить токен

#### DigitalOcean Token
```bash
# Перейти: https://cloud.digitalocean.com/account/api/tokens
# Generate New Token
# - Имя: kubernetes-api-access-prod-v2
# - Разрешения: 8 scopes (kubernetes, regions, sizes, actions)
# - Копировать токен
```

#### Supabase Keys
```bash
# Production Project: Knowledge_DBnanoAWS
# Перейти: https://app.supabase.com/project/lvixtpatqrtuwnygtpjx/settings/api
# Получить:
# - Public API key (ANON_KEY)
# - Service Role key (SERVICE_ROLE_KEY)
# - Project URL
# - Database password
```

### Шаг 2: Добавить в CREDENTIALS/.env

```bash
# Скопировать template
cp CREDENTIALS/.env.example CREDENTIALS/.env

# Открыть и заполнить
vim CREDENTIALS/.env

# Проверить что .env в .gitignore
grep -i '.env' .gitignore  # должен включать CREDENTIALS/.env

# НИКОГДА не коммитить .env
git status  # должен показать "nothing to commit"
```

### Шаг 3: Добавить в GitHub Secrets

```bash
# Способ 1: Через UI
# Settings → Secrets and variables → Actions → New repository secret
# Name: DO_API_TOKEN_PROD
# Value: dop_v1_xxxxxxxxxxxx

# Способ 2: Через CLI (если установлен gh)
gh secret set DO_API_TOKEN_PROD -b"$(grep DO_API_TOKEN CREDENTIALS/.env | cut -d= -f2)"
gh secret set KUBECONFIG_PROD -b"$(cat ~/.kube/config-super-brain-prod | base64)"
```

### Шаг 4: Проверить что всё работает

```bash
# Локально
source CREDENTIALS/.env
echo "DO_API_TOKEN=$DO_API_TOKEN" | head -c 20

# GitHub Actions
# Посмотреть logs workflow'а (должны быть замаскированы)
# ***

# Kubernetes
kubectl get secrets -n production
kubectl get secret supabase-credentials -n production -o yaml
```

---

## 🚀 GITHUB SECRETS

### Как добавить GitHub Secret

1. **Перейти в Settings**
   ```
   https://github.com/vik9541/super-brain-digital-twin/settings/secrets/actions
   ```

2. **Нажать "New repository secret"**

3. **Заполнить данные**
   ```
   Name:  DO_API_TOKEN_PROD
   Value: dop_v1_xxxxxxxxxxxx
   ```

4. **Сохранить (Save)**

### Все необходимые GitHub Secrets

```bash
# DigitalOcean
DO_API_TOKEN_PROD
DO_REGISTRY_TOKEN

# Kubernetes
KUBECONFIG_PROD            # base64 encoded
K8S_CLUSTER_ID
K8S_NAMESPACE

# Supabase (Production: lvixtpatqrtuwnygtpjx)
SUPABASE_URL
SUPABASE_ANON_KEY
SUPABASE_SERVICE_ROLE_KEY
SUPABASE_DB_PASSWORD

# Telegram
TELEGRAM_BOT_TOKEN

# N8N
N8N_WEBHOOK_URL
N8N_WORKFLOW_IDS

# API
API_SECRET_KEY
API_JWT_SECRET

# Monitoring
GRAFANA_ADMIN_PASSWORD
```

### Использование в GitHub Actions

```yaml
name: Deploy

on: [push]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to K8s
        env:
          DO_API_TOKEN: ${{ secrets.DO_API_TOKEN_PROD }}
          KUBECONFIG: ${{ secrets.KUBECONFIG_PROD }}
        run: |
          echo "Deploying..."
          # GitHub автоматически маскирует значение secrets в логах
          # Будет показано: ***
```

---

## 💾 ЛОКАЛЬНОЕ ХРАНИЛИЩЕ

### Структура CREDENTIALS папки

```
CREDENTIALS/
├── .env.example              ← Template (в Git) ✅
├── .env                       ← Реальные значения (в .gitignore) 🔐
├── .env.staging              ← Для staging (опционально) 🔐
├── secrets/                   ← Дополнительные файлы
│   ├── kubeconfig-prod.yaml   ← K8s config (в .gitignore) 🔐
│   └── docker-config.json     ← Docker auth (в .gitignore) 🔐
└── README.md                  ← Инструкции
```

### Как использовать CREDENTIALS/.env

```bash
# Загрузить все переменные
source CREDENTIALS/.env

# Проверить что загрузились
echo "API Token: $DO_API_TOKEN" | head -c 20
echo "..."

# Использовать в скриптах
#!/bin/bash
source CREDENTIALS/.env
curl -H "Authorization: Bearer $DO_API_TOKEN" \
  "https://api.digitalocean.com/v2/kubernetes/clusters"
```

### Безопасность локального хранилища

```bash
# 1. Убедиться что .gitignore содержит
grep -i 'credentials/.env' .gitignore
grep -i '.env.local' .gitignore
grep -i 'kubeconfig' .gitignore

# 2. Проверить права доступа
ls -la CREDENTIALS/.env
# должно быть: -rw-r--r-- или -rw------- (лучше)
# изменить если нужно:
chmod 600 CREDENTIALS/.env

# 3. Никогда не выкладывать
git status  # должен показать, что .env не отслеживается

# 4. Резервная копия
cp CREDENTIALS/.env ~/Desktop/super-brain-credentials-backup.env
chmod 600 ~/Desktop/super-brain-credentials-backup.env
# Хранить в защищенном месте!
```

---

## 🐳 KUBERNETES SECRETS

### Текущие Kubernetes Secrets

```bash
# Просмотреть все secrets
kubectl get secrets -n production

# Просмотреть конкретный secret
kubectl describe secret supabase-credentials -n production

# Декодировать значение (только для проверки!)
kubectl get secret supabase-credentials -n production \
  -o jsonpath='{.data.url}' | base64 -d
```

### Создать новый Kubernetes Secret

```bash
# Способ 1: Из файла
kubectl create secret generic my-secret \
  --from-file=CREDENTIALS/.env \
  -n production

# Способ 2: Из переменных
kubectl create secret generic do-api-token \
  --from-literal=token=$DO_API_TOKEN \
  -n production

# Способ 3: Из YAML (рекомендуется)
cat > k8s/secrets/do-token.yaml << EOF
apiVersion: v1
kind: Secret
metadata:
  name: do-api-token
  namespace: production
type: Opaque
stringData:
  token: $(grep DO_API_TOKEN CREDENTIALS/.env | cut -d= -f2)
EOF

kubectl apply -f k8s/secrets/do-token.yaml
```

### НИКОГДА не делай этого!

```bash
# ❌ НИКОГДА не выкладывай secrets в GitHub!
git add CREDENTIALS/.env

# ❌ НИКОГДА не логируй токены!
echo "Token: $DO_API_TOKEN"

# ❌ НИКОГДА не вставляй в код!
DO_API_TOKEN = "dop_v1_xxxx"  # BAD!

# ❌ НИКОГДА не отправляй по почте/чату!
# Используй только защищенные каналы (1Password, etc)
```

---

## 🔄 РОТАЦИЯ ТОКЕНОВ

### График ротации

| Токен | Частота | Последняя | Следующая |
|-------|---------|-----------|----------|
| DigitalOcean API | 90 дней | 8 дек 2025 | 8 мар 2026 |
| Supabase Keys | 90 дней | 1 дек 2025 | 1 мар 2026 |
| Telegram Bot | При компрометации | - | - |
| Docker Registry | 180 дней | 1 ноя 2025 | 1 май 2026 |
| Kubernetes Certs | 1 год | - | - |

### Как ротировать DigitalOcean Token

```bash
# Шаг 1: Создать новый токен
# https://cloud.digitalocean.com/account/api/tokens
# Generate New Token

# Шаг 2: Обновить CREDENTIALS/.env
vim CREDENTIALS/.env
# DO_API_TOKEN=dop_v1_new_token_here

# Шаг 3: Обновить GitHub Secret
gh secret set DO_API_TOKEN_PROD -b"dop_v1_new_token_here"

# Шаг 4: Обновить K8s Secret
kubectl patch secret digital-twin-secrets -n production \
  -p "{\"data\":{\"do-api-token\":\"$(echo -n dop_v1_new_token_here | base64)\"}}"

# Шаг 5: Удалить старый токен
# https://cloud.digitalocean.com/account/api/tokens
# Найти старый токен и нажать Delete

# Шаг 6: Проверить что всё работает
kubectl rollout restart deployment -n production

# Шаг 7: Задокументировать
echo "Token rotated on $(date)" >> ROTATION_LOG.txt
```

---

## 🔒 БЕЗОПАСНОСТЬ И АУДИТ

### Чеклист безопасности

```bash
# ✅ Проверить что .env в .gitignore
grep -i '.env' .gitignore

# ✅ Проверить что нет secrets в Git history
git log -S 'dop_v1_' --all  # должно быть пусто

# ✅ Проверить права доступа
ls -la CREDENTIALS/.env  # должно быть 600

# ✅ Проверить что нет hardcoded токенов
grep -r 'dop_v1_' --include='*.py' --include='*.js' --include='*.go'
grep -r 'TELEGRAM_BOT_TOKEN=' --include='*.py' --include='*.js'

# ✅ Проверить GitHub Secrets
# Settings → Secrets and variables → Actions
# Должны быть все необходимые

# ✅ Проверить K8s Secrets
kubectl get secrets -n production

# ✅ Проверить Vault (если используется)
# vault list secret/
```

### Аудит доступа

```bash
# Кто может видеть CREDENTIALS/.env?
ls -la CREDENTIALS/
# должно быть рядом с владельцем только

# Кто может видеть GitHub Secrets?
# Settings → Access → Collaborators
# Должны быть только нужные люди

# Кто может видеть K8s Secrets?
kubectl get rolebindings,clusterrolebindings -n production

# Логирование доступа
# kubectl logs -n kube-system -l component=apiserver | grep secret
```

---

## 📞 ПРОЦЕСС ПРИ КОМПРОМЕТАЦИИ

### Если токен выложен случайно в Git

```bash
# 1. НЕМЕДЛЕННО удалить токен в источнике
# DigitalOcean, Supabase, etc

# 2. Очистить Git history
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch CREDENTIALS/.env' \
  -- --all
git push --force

# 3. Создать новый токен
# (см. процесс ротации выше)

# 4. Обновить везде (GitHub Secrets, K8s, CREDENTIALS/.env)

# 5. Проверить логи
kubectl logs -n production -l app=api | grep token

# 6. Задокументировать инцидент
echo "[SECURITY INCIDENT] Token leaked on $(date)" >> SECURITY_LOG.txt
```

---

## ✅ ФИНАЛЬНЫЙ ЧЕКЛИСТ

```
✅ CREDENTIALS/.env.example создан с полной структурой
✅ CREDENTIALS/.env.example в Git (без реальных значений)
✅ CREDENTIALS/.env в .gitignore
✅ Все токены заполнены в CREDENTIALS/.env (локально)
✅ GitHub Secrets созданы и заполнены
✅ K8s Secrets созданы в namespace production
✅ Права доступа (RBAC) настроены
✅ Логирование и аудит включены
✅ График ротации установлен
✅ Документация обновлена
✅ Команда обучена процессам
```

---

## 📚 ПОЛЕЗНЫЕ ССЫЛКИ

- [GitHub Encrypted Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)
- [DigitalOcean API Tokens](https://docs.digitalocean.com/reference/api/)
- [OWASP Secret Management](https://owasp.org/)

---

**Версия:** 2.1  
**Статус:** ✅ Production Ready  
**Последнее обновление:** 8 декабря 2025  
**Ответственный:** DevOps Team  
**Изменения:** Обновлен Supabase Project ID (lvixtpatqrtuwnygtpjx) для Production  