# 🚀 CONTACT INTELLIGENCE - DEPLOYMENT GUIDE

## ШАГ 1: Supabase Setup

```bash
# 1. Откройте Supabase Dashboard
https://app.supabase.com/project/lvixtpatqrtuwnygtpjx

# 2. Перейдите в SQL Editor
# 3. Выполните скрипт из:
https://github.com/vik9541/super-brain-digital-twin/blob/main/SECURE_SCHEMA_V2.sql
```

## ШАГ 2: Генерация ключа шифрования

```bash
# В терминале:
ENCRYPTION_KEY=$(openssl rand -base64 32)
echo "Сохраните этот ключ: $ENCRYPTION_KEY"
```

## ШАГ 3: Создание K8s Secrets

```bash
# Создайте secret для Contact Intelligence
kubectl create secret generic contact-secrets \
  --from-literal=encryption-key="$ENCRYPTION_KEY" \
  -n default

# Проверьте
kubectl get secrets contact-secrets
```

## ШАГ 4: Сборка Docker образа

```bash
cd modules/contact_intelligence/fastapi_service

# Соберите образ
docker build -t contact-ai:latest .

# Залогиньтесь в DigitalOcean Registry
docker login registry.digitalocean.com

# Тегируйте
docker tag contact-ai:latest registry.digitalocean.com/YOUR_REGISTRY/contact-ai:latest

# Загрузите
docker push registry.digitalocean.com/YOUR_REGISTRY/contact-ai:latest
```

## ШАГ 5: Развертывание в K8s

```bash
# Примените манифест
kubectl apply -f k8s/deployment.yaml

# Проверьте статус
kubectl get pods -l app=contact-ai
kubectl logs -f deployment/contact-ai-service
```

## ШАГ 6: Тестирование

```bash
# Port-forward для локального теста
kubectl port-forward service/contact-ai-service 8000:80

# Отправьте тестовый запрос
curl -X POST http://localhost:8000/api/v1/contact/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "contact_name": "Test User",
    "contact_telegram_id": 123456,
    "message_text": "Hello world",
    "channel": "telegram"
  }'
```

## ✅ ГОТОВО!

Теперь сервис работает и готов принимать сообщения через API.