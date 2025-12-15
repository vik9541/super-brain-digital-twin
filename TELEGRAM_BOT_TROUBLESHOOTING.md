# Telegram Bot Troubleshooting - Полный отчёт
**Дата:** 15 декабря 2025, 09:25 МСК  
**Бот:** @astra_VIK_bot  
**Проблема:** Бот не отвечает на сообщения

---

## 🔴 ТЕКУЩАЯ ПРОБЛЕМА

**Симптом:** Пользователь отправляет сообщения боту @astra_VIK_bot, но **никакой реакции нет**

**Ожидаемое поведение:**
- Telegram → POST запрос на webhook → Обработка → Ответ/сохранение в БД
- Бот должен ответить подтверждением или молча сохранить сообщение

**Фактическое поведение:**
- Сообщения отправляются
- Никакой реакции от бота
- Никаких логов в Kubernetes pod

---

## 📊 ТЕКУЩЕЕ СОСТОЯНИЕ СИСТЕМЫ

### Telegram Webhook
```
✅ URL: https://victor.97v.ru/api/telegram/webhook
✅ Pending Updates: 0
✅ Last Error: None
✅ Webhook установлен (выполнено: python set_webhook.py)
```

**Вывод:** Telegram знает URL webhook, ошибок нет, но запросы НЕ ПРИХОДЯТ на сервер.

### Kubernetes Deployment
```bash
# Текущий pod
NAME: victor-bot-v2-69c8d8ff7f-rnvvj
STATUS: Running (1/1)
AGE: ~2 минуты (создан после kubectl rollout restart)
IMAGE: registry.digitalocean.com/digital-twin-registry/victor-bot:2.0.0

# Логи
🚀 Starting Victor Bot v2.0...
⚠️ Background worker disabled (use pooler workaround)
Uvicorn running on http://0.0.0.0:8000

# Health checks работают
INFO: 10.108.0.106 - "GET /health HTTP/1.1" 200 OK
```

**Вывод:** Pod запущен, health checks проходят, но **webhook POST запросов НЕТ**.

### GitHub Actions Build #12
```
✅ Status: completed / success
✅ Commit: 646843f (chore: trigger deployment)
✅ Build Time: 2025-12-15T06:19:37Z
✅ Image: registry.digitalocean.com/digital-twin-registry/victor-bot:2.0.0
```

**Вывод:** Новый Docker образ собран, содержит REST API fallback код.

### Database Connection
```python
# Проблема: Supabase Pooler несовместим с psycopg3
DATABASE_URL: postgresql://postgres.lvixtpatqrtuwhygtpjx:PASSWORD@aws-0-eu-central-1.pooler.supabase.com:5432/postgres

# Результат теста (test_psycopg_connection.py)
❌ Connection FAILED after 30 seconds (timeout)
```

**Вывод:** psycopg3 pool НЕ ПОДКЛЮЧИТСЯ (это ожидаемо), REST API fallback должен сработать.

---

## 🛠️ ЧТО БЫЛО СДЕЛАНО

### 1. Диагностика Webhook (ВЫПОЛНЕНО ✅)
```python
# Создан скрипт: check_webhook.py
Response:
{
  "url": "https://victor.97v.ru/api/telegram/webhook",  # ✅ Установлен
  "has_custom_certificate": false,
  "pending_update_count": 0,  # ✅ Нет накопленных сообщений
  "last_error_date": null     # ✅ Нет ошибок
}
```

### 2. Установка Webhook (ВЫПОЛНЕНО ✅)
```python
# Выполнено: python set_webhook.py
BOT_TOKEN = "8457627946:AAEKY9QoV4yI8A9D5u6lJflralz480uazp8"
WEBHOOK_URL = "https://victor.97v.ru/api/telegram/webhook"

# Результат
✅ WEBHOOK УСТАНОВЛЕН! URL: https://victor.97v.ru/api/telegram/webhook
```

### 3. REST API Fallback Implementation (ВЫПОЛНЕНО ✅)
**Commit:** 6452507 - "fix: Add REST API fallback for all handlers when pool fails"

**Изменения в api/victor_bot_router.py:**
```python
# get_db_pool() теперь возвращает None при ошибке (не блокирует)
async def get_db_pool():
    global _db_pool
    if _db_pool is None:
        try:
            _db_pool = AsyncConnectionPool(DATABASE_URL, ...)
            await _db_pool.open()
        except Exception as e:
            logger.error(f"❌ Failed to create DB pool: {e}")
            logger.warning("⚠️ Falling back to Supabase REST API")
            return None  # ← НЕ БЛОКИРУЕТ!
    return _db_pool

# Все 8 handle_* функций поддерживают pool=None
async def handle_text(text: str, message_id: int, pool: Optional[AsyncConnectionPool] = None):
    if pool is None:
        # REST API fallback
        data = {"content": text, "message_id": message_id, ...}
        await save_to_supabase_rest(data)
    else:
        # psycopg3 pool (никогда не сработает)
        async with pool.connection() as conn:
            ...
```

### 4. GitHub Actions Workflow Trigger (ВЫПОЛНЕНО ✅)
**Проблема:** Commit 6452507 не запустил workflow (изменён deploy_victor_schema.py, которого нет в trigger paths)

**Решение:**
1. Создан .trigger-deploy файл (ПОТЕРЯН при git merge)
2. Изменён main_victor_bot.py (добавлен комментарий "Deployment: 2025-12-15 09:17")
3. Commit 646843f запустил Build #12

**Результат:** Build #12 завершён успешно

### 5. Kubernetes Deployment Update (ВЫПОЛНЕНО ✅)
**Проблема:** Workflow НЕ обновляет deployment автоматически

**Решение:**
```bash
kubectl rollout restart deployment/victor-bot-v2
# deployment.apps/victor-bot-v2 restarted ✅

# Новый pod запущен
victor-bot-v2-69c8d8ff7f-rnvvj   1/1     Running   0          2m
```

---

## ❌ ВСТРЕЧЕННЫЕ ОШИБКИ

### Ошибка 1: Method Not Allowed (405)
```bash
# Тест: curl https://victor.97v.ru/api/telegram/webhook
{"detail":"Method Not Allowed"}
```
**Причина:** GET запрос к POST-only endpoint  
**Статус:** Это нормально (браузер делает GET, webhook должен быть POST)

### Ошибка 2: Webhook не установлен
```python
# Первая проверка показала
"url": ""  # ← ПУСТО!
```
**Решение:** Выполнено `python set_webhook.py`  
**Статус:** ИСПРАВЛЕНО ✅

### Ошибка 3: Deployment не обновился после Build #12
```
Pod Created: 2025-12-14T18:39:45Z  # ← СТАРЫЙ!
```
**Решение:** `kubectl rollout restart deployment/victor-bot-v2`  
**Статус:** ИСПРАВЛЕНО ✅

### Ошибка 4: Git merge потерял .trigger-deploy
```bash
git pull origin main --no-rebase
# Fast-forward → .trigger-deploy LOST
```
**Решение:** Изменён main_victor_bot.py вместо .trigger-deploy  
**Статус:** ОБОЙДЕНО ✅

---

## 🔍 АНАЛИЗ: ПОЧЕМУ НИЧЕГО НЕ РАБОТАЕТ?

### ❓ Вопрос 1: Приходят ли POST запросы от Telegram на webhook?

**Проверка:**
```bash
kubectl logs victor-bot-v2-69c8d8ff7f-rnvvj --tail=50 | grep POST
# Результат: ПУСТО (только GET /health)
```

**Вывод:** POST запросы **НЕ ПРИХОДЯТ** на pod!

**Возможные причины:**
1. NGINX Ingress не настроен для /api/telegram/webhook
2. DNS не указывает на Kubernetes ingress
3. SSL сертификат не настроен (Telegram требует HTTPS)
4. Webhook URL указывает на неправильный сервис

### ❓ Вопрос 2: Настроен ли NGINX Ingress?

**Нужно проверить:**
```bash
kubectl get ingress
kubectl describe ingress <ingress-name>
```

**Ожидаемая конфигурация:**
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: victor-bot-ingress
spec:
  rules:
  - host: victor.97v.ru
    http:
      paths:
      - path: /api/telegram/webhook
        pathType: Prefix
        backend:
          service:
            name: victor-bot-v2
            port:
              number: 8000
  tls:
  - hosts:
    - victor.97v.ru
    secretName: victor-tls-cert
```

### ❓ Вопрос 3: Указывает ли DNS на Kubernetes?

**Нужно проверить:**
```bash
nslookup victor.97v.ru
# Должен вернуть IP адрес Load Balancer в DigitalOcean
```

### ❓ Вопрос 4: Работает ли Service?

**Нужно проверить:**
```bash
kubectl get service victor-bot-v2
kubectl describe service victor-bot-v2
```

**Ожидаемая конфигурация:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: victor-bot-v2
spec:
  selector:
    app: victor-bot-v2
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

---

## 📁 ФАЙЛОВАЯ СТРУКТУРА

### Kubernetes Manifests
```
k8s/victor-bot/
├── deployment.yaml      # Deployment для victor-bot-v2
├── service.yaml         # Service для victor-bot-v2
└── ingress.yaml         # Ingress для victor.97v.ru (?)
```

**Статус:** Нужно проверить наличие ingress.yaml

### Docker Images
```
registry.digitalocean.com/digital-twin-registry/victor-bot:2.0.0
registry.digitalocean.com/digital-twin-registry/victor-bot:latest
```

**Статус:** Build #12 запушил оба тега ✅

### Application Code
```
api/victor_bot_router.py   # ✅ REST API fallback реализован
main_victor_bot.py          # ✅ FastAPI app с webhook endpoint
workers/                    # (не используется, отключён worker)
```

---

## 🔧 СЛЕДУЮЩИЕ ШАГИ (ПРИОРИТЕТ)

### 🔴 КРИТИЧНО: Проверить Ingress конфигурацию
```bash
# 1. Проверить существующие ingress
kubectl get ingress

# 2. Описать ingress для victor-bot
kubectl describe ingress <имя>

# 3. Проверить, что путь /api/telegram/webhook настроен
```

### 🔴 КРИТИЧНО: Проверить Service
```bash
# 1. Проверить существующие services
kubectl get service -l app=victor-bot-v2

# 2. Описать service
kubectl describe service victor-bot-v2

# 3. Проверить селекторы и порты
```

### 🔴 КРИТИЧНО: Проверить DNS
```bash
# 1. Проверить A-запись
nslookup victor.97v.ru

# 2. Проверить доступность напрямую
curl -v https://victor.97v.ru/health

# 3. Проверить webhook endpoint
curl -X POST https://victor.97v.ru/api/telegram/webhook \
  -H "Content-Type: application/json" \
  -d '{"message":{"text":"test"}}'
```

### 🟡 ВАЖНО: Проверить Load Balancer
```bash
# 1. Получить External IP NGINX Ingress
kubectl get service -n ingress-nginx

# 2. Проверить, совпадает ли IP с DNS записью victor.97v.ru
```

### 🟡 ВАЖНО: Проверить логи NGINX Ingress
```bash
# 1. Найти pod NGINX Ingress
kubectl get pods -n ingress-nginx

# 2. Проверить логи
kubectl logs <nginx-ingress-pod> -n ingress-nginx | grep victor
```

### 🟢 ПОЛЕЗНО: Проверить SSL сертификат
```bash
# 1. Проверить TLS secret
kubectl get secret victor-tls-cert

# 2. Проверить сертификат
openssl s_client -connect victor.97v.ru:443 -servername victor.97v.ru
```

---

## 📝 КОНФИГУРАЦИОННЫЕ ФАЙЛЫ

### Telegram Bot Config
```
BOT_TOKEN: 8457627946:AAEKY9QoV4yI8A9D5u6lJflralz480uazp8
CHAT_ID: 1743141472
WEBHOOK_URL: https://victor.97v.ru/api/telegram/webhook
```

### Database Config
```
DATABASE_URL: postgresql://postgres.lvixtpatqrtuwhygtpjx:<PASSWORD>@aws-0-eu-central-1.pooler.supabase.com:5432/postgres
SUPABASE_URL: https://lvixtpatqrtuwhygtpjx.supabase.co
SUPABASE_KEY: <ANON_KEY>
REST_API_URL: https://lvixtpatqrtuwhygtpjx.supabase.co/rest/v1/
```

### Kubernetes Config
```
CLUSTER: super-brain-prod (DigitalOcean DOKS, nyc2)
NAMESPACE: default
DEPLOYMENT: victor-bot-v2
SERVICE: victor-bot-v2
INGRESS: <НЕИЗВЕСТНО - НУЖНО ПРОВЕРИТЬ>
```

---

## 🐛 DEBUGGING COMMANDS

```bash
# === KUBERNETES STATUS ===
kubectl get all -l app=victor-bot-v2
kubectl get ingress
kubectl get service victor-bot-v2
kubectl describe deployment victor-bot-v2

# === LOGS ===
kubectl logs victor-bot-v2-69c8d8ff7f-rnvvj --follow
kubectl logs victor-bot-v2-69c8d8ff7f-rnvvj | grep -E "(POST|webhook|error)"

# === INGRESS ===
kubectl get ingress -A
kubectl describe ingress <name>
kubectl get service -n ingress-nginx

# === NETWORK TESTS ===
nslookup victor.97v.ru
curl -v https://victor.97v.ru/health
curl -X POST https://victor.97v.ru/api/telegram/webhook -d '{"test":"data"}'

# === TELEGRAM WEBHOOK ===
python check_webhook.py
python test_webhook_now.py

# === LOCAL TEST POD ===
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- sh
# Inside pod:
curl http://victor-bot-v2:8000/health
curl -X POST http://victor-bot-v2:8000/api/telegram/webhook -d '{"message":{"text":"test"}}'
```

---

## 🎯 ГИПОТЕЗЫ

### Гипотеза 1: NGINX Ingress не настроен ❓
**Вероятность:** 80%  
**Симптомы:** POST запросы не приходят на pod  
**Проверка:** `kubectl get ingress`

### Гипотеза 2: DNS не указывает на Load Balancer ❓
**Вероятность:** 60%  
**Симптомы:** curl https://victor.97v.ru/health не работает  
**Проверка:** `nslookup victor.97v.ru`

### Гипотеза 3: Service неправильно настроен ❓
**Вероятность:** 40%  
**Симптомы:** Ingress не может найти backend  
**Проверка:** `kubectl describe service victor-bot-v2`

### Гипотеза 4: Telegram webhook URL неправильный ❓
**Вероятность:** 20%  
**Симптомы:** getWebhookInfo показывает правильный URL  
**Проверка:** URL выглядит корректно

### Гипотеза 5: SSL сертификат недействителен ❓
**Вероятность:** 30%  
**Симптомы:** Telegram не доверяет сертификату  
**Проверка:** `openssl s_client -connect victor.97v.ru:443`

---

## 📊 TIMELINE СОБЫТИЙ

```
14 декабря 22:28 - Build #11 (commit 6bd8511) - psycopg3 migration
14 декабря 18:39 - Pod создан (СТАРЫЙ, без REST API fallback)

15 декабря 09:00 - Пользователь обнаружил: бот не отвечает
15 декабря 09:05 - Проверка webhook: URL НЕ УСТАНОВЛЕН
15 декабря 09:07 - Выполнено: python set_webhook.py ✅
15 декабря 09:10 - Тест webhook: 405 "Method Not Allowed" (это OK для GET)
15 декабря 09:12 - Обнаружено: commit 6452507 не задеплоен
15 декабря 09:15 - Создан .trigger-deploy → ПОТЕРЯН при merge
15 декабря 09:17 - Изменён main_victor_bot.py → commit 646843f
15 декабря 09:18 - Build #12 ЗАПУЩЕН
15 декабря 09:19 - Build #12 ЗАВЕРШЁН (success)
15 декабря 09:20 - Обнаружено: Pod НЕ ОБНОВИЛСЯ
15 декабря 09:21 - kubectl rollout restart deployment/victor-bot-v2
15 декабря 09:22 - Новый pod ЗАПУЩЕН (victor-bot-v2-69c8d8ff7f-rnvvj)
15 декабря 09:23 - Проверка логов: только health checks, NO webhook POST
15 декабря 09:25 - ТЕКУЩЕЕ ВРЕМЯ - бот всё ещё не отвечает
```

---

## ✅ ПРОВЕРОЧНЫЙ СПИСОК

- [x] Telegram webhook URL установлен
- [x] GitHub Actions Build #12 завершён
- [x] Docker образ запушен в registry
- [x] Kubernetes pod обновлён (новый образ)
- [x] Pod в статусе Running
- [x] Health checks проходят
- [x] REST API fallback код присутствует
- [ ] **Ingress настроен для /api/telegram/webhook**
- [ ] **DNS victor.97v.ru указывает на Load Balancer**
- [ ] **Service victor-bot-v2 доступен**
- [ ] **SSL сертификат действителен**
- [ ] **POST запросы приходят на pod**
- [ ] **Бот отвечает на сообщения**

---

## 🔑 КЛЮЧЕВЫЕ ВЫВОДЫ

1. **Webhook установлен ✅** - Telegram знает URL
2. **Код готов ✅** - REST API fallback реализован
3. **Pod запущен ✅** - Новый образ с фиксом
4. **POST запросы НЕ ПРИХОДЯТ ❌** - Проблема в сетевой конфигурации

**Главная проблема:** Webhook POST запросы от Telegram НЕ доходят до Kubernetes pod.

**Наиболее вероятная причина:** Отсутствие или неправильная настройка NGINX Ingress.

---

## 🚨 НЕМЕДЛЕННЫЕ ДЕЙСТВИЯ

1. **Проверить Ingress:** `kubectl get ingress`
2. **Проверить DNS:** `nslookup victor.97v.ru`
3. **Проверить доступность:** `curl https://victor.97v.ru/health`
4. **Создать Ingress** (если отсутствует)
5. **Проверить логи NGINX Ingress**

---

**Конец отчёта**
