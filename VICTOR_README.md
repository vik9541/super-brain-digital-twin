# 🚀 Victor Bot v2.0 - Production Deployment

## Quick Start (3 команды)

```powershell
# 1. Установи registry
$env:DO_REGISTRY = "registry.digitalocean.com/YOUR_REGISTRY"

# 2. Деплой
.\DEPLOY_NOW.ps1

# 3. Настрой webhook
.\setup_telegram_webhook.ps1 -NgrokUrl "https://victor.97v.ru"
```

**Готово!** Бот работает на https://victor.97v.ru 🎉

---

## Детальная инструкция

### Шаг 1: Подготовка

#### 1.1 DigitalOcean CLI
```powershell
# Установка (если еще нет)
# https://docs.digitalocean.com/reference/doctl/how-to/install/

# Авторизация
doctl auth init

# Проверка
doctl account get
```

#### 1.2 Kubernetes Cluster
```powershell
# Список кластеров
doctl kubernetes cluster list

# Подключение к кластеру
doctl kubernetes cluster kubeconfig save YOUR_CLUSTER_NAME

# Проверка
kubectl cluster-info
kubectl get nodes
```

#### 1.3 Container Registry
```powershell
# Получить имя registry
doctl registry get

# Логин
doctl registry login

# Сохранить в переменную
$env:DO_REGISTRY = "registry.digitalocean.com/YOUR_REGISTRY"
```

### Шаг 2: Настройка DNS

#### 2.1 Получить IP LoadBalancer
```powershell
kubectl get svc -n ingress-nginx ingress-nginx-controller
```

Скопируй EXTERNAL-IP

#### 2.2 Создать DNS запись

**В DigitalOcean Dashboard:**
1. Networking → Domains → 97v.ru
2. Add Record
3. Type: `A`
4. Hostname: `victor`
5. Will direct to: `[EXTERNAL-IP LoadBalancer]`
6. TTL: 3600
7. Create Record

#### 2.3 Проверить DNS
```powershell
# Подожди 1-2 минуты, затем:
nslookup victor.97v.ru

# Должен вернуть IP LoadBalancer
```

### Шаг 3: Деплой

#### 3.1 Обновить манифесты

Открой `k8s/victor-bot/03-deployment.yaml` и замени:
```yaml
image: registry.digitalocean.com/YOUR_REGISTRY/victor-bot:2.0.0
```

На свой registry:
```yaml
image: registry.digitalocean.com/my-registry/victor-bot:2.0.0
```

#### 3.2 Запустить деплой
```powershell
# Полный деплой (build + push + deploy)
.\deploy_victor_production.ps1 -Registry "registry.digitalocean.com/YOUR_REGISTRY"

# Или через quick start
.\DEPLOY_NOW.ps1
```

Процесс займет 3-5 минут.

#### 3.3 Дождаться готовности
```powershell
# Смотреть статус
kubectl rollout status deployment/victor-bot-v2

# Проверить pods
kubectl get pods -l app=victor-bot-v2

# Должен быть STATUS: Running, READY: 1/1
```

### Шаг 4: SSL Certificate

cert-manager автоматически создаст Let's Encrypt сертификат.

```powershell
# Проверить статус
kubectl get certificate victor-bot-tls

# Подождать пока STATUS не станет True
# Обычно 1-3 минуты
```

### Шаг 5: Проверка API

```powershell
# Health check
curl https://victor.97v.ru/health

# Ожидаемый ответ:
# {"status":"ok"}

# Root endpoint
curl https://victor.97v.ru/

# Должен вернуть info о сервисе
```

### Шаг 6: Telegram Webhook

```powershell
# Автоматическая настройка
.\setup_telegram_webhook.ps1 -NgrokUrl "https://victor.97v.ru"

# Проверка
$token = "8457627946:AAEKY9QoV4yI8A9D5u6lJflralz480uazp8"
Invoke-RestMethod "https://api.telegram.org/bot$token/getWebhookInfo" | ConvertTo-Json -Depth 5
```

Должно показать:
- `url`: "https://victor.97v.ru/api/telegram/webhook"
- `pending_update_count`: 0
- `last_error_date`: null

### Шаг 7: Тестирование

#### 7.1 Отправить сообщение боту
Открой Telegram и отправь любое сообщение боту.

#### 7.2 Проверить логи
```powershell
kubectl logs -f -l app=victor-bot-v2
```

Должны появиться записи:
```
INFO: Received webhook from Telegram
INFO: Processing message...
```

#### 7.3 Проверить Supabase
Открой Supabase Dashboard → Table Editor → victor_inbox

Должна появиться новая запись с твоим сообщением!

---

## Управление

### Просмотр логов
```powershell
# Все логи
kubectl logs -l app=victor-bot-v2

# Последние 50 строк
kubectl logs -l app=victor-bot-v2 --tail=50

# В реальном времени
kubectl logs -f -l app=victor-bot-v2
```

### Рестарт
```powershell
kubectl rollout restart deployment/victor-bot-v2
```

### Масштабирование
```powershell
# 2 реплики для высокой доступности
kubectl scale deployment victor-bot-v2 --replicas=2
```

### Обновление версии
```powershell
# Новая версия
.\deploy_victor_production.ps1 -Version "2.0.1"
```

### Откат к предыдущей версии
```powershell
kubectl rollout undo deployment/victor-bot-v2
```

### Удаление
```powershell
kubectl delete -f k8s/victor-bot/
```

---

## Troubleshooting

### Pod не запускается

**Симптомы:**
```powershell
kubectl get pods -l app=victor-bot-v2
# STATUS: CrashLoopBackOff или ImagePullBackOff
```

**Решение:**
```powershell
# Детали ошибки
kubectl describe pod -l app=victor-bot-v2

# Логи
kubectl logs -l app=victor-bot-v2
```

### ImagePullBackOff

**Причина:** Kubernetes не может загрузить Docker образ из registry

**Решение:**
```powershell
# Создать registry secret
doctl registry kubernetes-manifest | kubectl apply -f -

# Рестарт
kubectl rollout restart deployment/victor-bot-v2
```

### SSL не работает

**Проверка:**
```powershell
kubectl get certificate victor-bot-tls
kubectl describe certificate victor-bot-tls
```

**Если STATUS не Ready:**
```powershell
# Проверить cert-manager
kubectl get pods -n cert-manager

# Проверить challenges
kubectl get challenges

# Логи cert-manager
kubectl logs -n cert-manager -l app=cert-manager
```

### Webhook не работает

**Симптомы:** Бот не отвечает на сообщения

**Проверка:**
```powershell
# Webhook info
$token = "8457627946:AAEKY9QoV4yI8A9D5u6lJflralz480uazp8"
Invoke-RestMethod "https://api.telegram.org/bot$token/getWebhookInfo"

# Если есть last_error_message - смотри его
```

**Решение:**
```powershell
# Проверить Ingress
kubectl describe ingress victor-bot-ingress

# Логи NGINX Ingress
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx --tail=100

# Проверить что API работает
curl https://victor.97v.ru/health
```

---

## Архитектура

```
Internet
   ↓
[DigitalOcean LoadBalancer]
   ↓
[NGINX Ingress Controller]
   ↓
[victor.97v.ru/api/telegram/webhook]
   ↓
[Victor Bot Pod]
   ↓
[Supabase PostgreSQL]
```

### Компоненты:
- **LoadBalancer**: DigitalOcean LB с публичным IP
- **Ingress**: NGINX с SSL от Let's Encrypt
- **Victor Bot**: FastAPI приложение в Docker контейнере
- **Supabase**: PostgreSQL база данных (managed)

---

## Production Checklist

- [x] Kubernetes кластер готов
- [x] NGINX Ingress Controller установлен
- [x] cert-manager установлен
- [x] DNS запись создана
- [x] Docker образ собран
- [x] Secrets настроены
- [x] Deployment применен
- [x] SSL сертификат получен
- [x] API доступен через HTTPS
- [x] Webhook настроен
- [x] Логи работают
- [ ] Мониторинг настроен (опционально)
- [ ] Алерты настроены (опционально)

---

## Мониторинг (опционально)

### Prometheus
```yaml
# Добавить в Deployment
annotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "8000"
  prometheus.io/path: "/metrics"
```

### Grafana Dashboard
Импортируй дашборд для FastAPI приложений.

---

## Безопасность

✅ **Реализовано:**
- Secrets в Kubernetes (не в коде)
- Non-root user в Docker
- HTTPS с валидным SSL
- Rate limiting в Ingress
- Security context в Pod

⚠️ **Рекомендации:**
- Включи Network Policies
- Настрой Pod Security Policies
- Регулярно обновляй dependencies
- Включи автобэкапы Supabase

---

## Поддержка

**Документация:**
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Полный чеклист
- [VICTOR_PRODUCTION_DEPLOY.md](VICTOR_PRODUCTION_DEPLOY.md) - Детальный гайд
- [VICTOR_TELEGRAM_SETUP.md](VICTOR_TELEGRAM_SETUP.md) - Настройка Telegram

**Логи:**
```powershell
kubectl logs -f -l app=victor-bot-v2
```

**Статус:**
```powershell
kubectl get all -l app=victor-bot-v2
```

---

## 🎉 Success!

После успешного деплоя:

✅ Victor Bot работает на https://victor.97v.ru  
✅ SSL сертификат активен  
✅ Telegram webhook настроен  
✅ Сообщения сохраняются в Supabase  
✅ Логи доступны в реальном времени  

**Отправь сообщение боту и наслаждайся работой!** 🚀

---

**Version:** 2.0.0  
**Date:** 14 декабря 2025  
**Status:** Production Ready  
