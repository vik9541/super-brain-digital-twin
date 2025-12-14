# 🤖 Victor Bot v2.0 - Telegram Webhook Setup

## Текущее состояние
✅ API сервер запущен локально на :8000
✅ SQL схема развернута в Supabase
✅ 4 таблицы готовы к работе

## Следующие шаги

### Вариант 1: Локальное тестирование через ngrok

```powershell
# 1. Установи ngrok (если еще нет)
# https://ngrok.com/download

# 2. Запусти туннель
ngrok http 8000

# 3. Скопируй HTTPS URL (например: https://abc123.ngrok.io)

# 4. Установи webhook
$url = "https://ABC123.ngrok.io/api/telegram/webhook"
$token = "8457627946:AAEKY9QoV4yI8A9D5u6lJflralz480uazp8"
Invoke-RestMethod "https://api.telegram.org/bot$token/setWebhook?url=$url"

# 5. Проверь webhook
Invoke-RestMethod "https://api.telegram.org/bot$token/getWebhookInfo"
```

### Вариант 2: Деплой на 97v.ru (Production)

У тебя есть домен **97v.ru** на DigitalOcean DOKS!

#### Шаг 1: Создай Docker образ
```powershell
# Создай Dockerfile для Victor Bot
docker build -t victor-bot:v2.0 -f Dockerfile.victor-bot .

# Push в registry
docker tag victor-bot:v2.0 registry.digitalocean.com/YOUR_REGISTRY/victor-bot:v2.0
docker push registry.digitalocean.com/YOUR_REGISTRY/victor-bot:v2.0
```

#### Шаг 2: Deploy в Kubernetes
```yaml
# k8s/victor-bot-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: victor-bot-v2
spec:
  replicas: 1
  selector:
    matchLabels:
      app: victor-bot-v2
  template:
    metadata:
      labels:
        app: victor-bot-v2
    spec:
      containers:
      - name: victor-bot
        image: registry.digitalocean.com/YOUR_REGISTRY/victor-bot:v2.0
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: victor-bot-secrets
              key: database-url
        - name: TELEGRAM_BOT_TOKEN
          valueFrom:
            secretKeyRef:
              name: victor-bot-secrets
              key: bot-token
---
apiVersion: v1
kind: Service
metadata:
  name: victor-bot-service
spec:
  selector:
    app: victor-bot-v2
  ports:
  - port: 80
    targetPort: 8000
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: victor-bot-ingress
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - victor.97v.ru
    secretName: victor-bot-tls
  rules:
  - host: victor.97v.ru
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: victor-bot-service
            port:
              number: 80
```

#### Шаг 3: Деплой
```powershell
kubectl apply -f k8s/victor-bot-deployment.yaml

# Проверь
kubectl get pods | Select-String "victor"
kubectl get ingress
```

#### Шаг 4: Установи webhook на production URL
```powershell
$url = "https://victor.97v.ru/api/telegram/webhook"
$token = "8457627946:AAEKY9QoV4yI8A9D5u6lJflralz480uazp8"
Invoke-RestMethod "https://api.telegram.org/bot$token/setWebhook?url=$url"
```

---

## Быстрый старт (рекомендую ngrok для тестов)

1. **Скачай ngrok**: https://ngrok.com/download
2. **Запусти**: `ngrok http 8000`
3. **Скопируй HTTPS URL**
4. **Выполни**:

```powershell
$ngrokUrl = "ВАШ_NGROK_URL"  # например https://abc123.ngrok.io
$webhookUrl = "$ngrokUrl/api/telegram/webhook"
$token = "8457627946:AAEKY9QoV4yI8A9D5u6lJflralz480uazp8"

# Установить webhook
Invoke-RestMethod "https://api.telegram.org/bot$token/setWebhook?url=$webhookUrl"
```

5. **Тестируй**: Отправь сообщение боту в Telegram!

---

## Проблемы и решения

### Webhook не работает?
```powershell
# Проверь статус
$token = "8457627946:AAEKY9QoV4yI8A9D5u6lJflralz480uazp8"
Invoke-RestMethod "https://api.telegram.org/bot$token/getWebhookInfo" | ConvertTo-Json -Depth 5
```

### API не отвечает?
```powershell
# Проверь локально
Invoke-RestMethod http://localhost:8000/health
```

### Логи
```powershell
# Смотри вывод сервера в терминале где запущен python test_api_minimal.py
```

---

## Что выбрать?

- **Для тестов сегодня**: ngrok (5 минут)
- **Для production**: 97v.ru Kubernetes (30 минут)

**Готов начать?** Какой вариант выбираешь? 🚀
