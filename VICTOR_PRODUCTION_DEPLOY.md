# 🚀 Victor Bot v2.0 - Production Deployment Guide

## Предварительная подготовка

### 1. Проверь доступ к DigitalOcean
```powershell
# Установи doctl если еще нет
# https://docs.digitalocean.com/reference/doctl/how-to/install/

# Авторизуйся
doctl auth init

# Проверь кластеры
doctl kubernetes cluster list
```

### 2. Подключись к кластеру
```powershell
# Замени YOUR_CLUSTER_NAME на реальное имя
doctl kubernetes cluster kubeconfig save YOUR_CLUSTER_NAME

# Проверь подключение
kubectl cluster-info
kubectl get nodes
```

### 3. Проверь Container Registry
```powershell
# Список registry
doctl registry get

# Логин (если нужно)
doctl registry login
```

---

## 🎯 Быстрый деплой (5 шагов)

### Шаг 1: Обнови registry имя в манифестах

Открой файл `k8s/victor-bot/03-deployment.yaml` и замени:
```yaml
image: registry.digitalocean.com/YOUR_REGISTRY/victor-bot:2.0.0
```

На твой реальный registry (например):
```yaml
image: registry.digitalocean.com/my-registry/victor-bot:2.0.0
```

### Шаг 2: Запусти полный деплой
```powershell
# Опция 1: Полный деплой (build + push + deploy)
.\deploy_victor_production.ps1 -Registry "registry.digitalocean.com/YOUR_REGISTRY"

# Опция 2: Только деплой (если образ уже в registry)
.\deploy_victor_production.ps1 -SkipBuild -SkipPush
```

### Шаг 3: Настрой DNS для victor.97v.ru

**В DigitalOcean Dashboard:**
1. Networking → Domains → 97v.ru
2. Add Record → Type: A
3. Hostname: `victor`
4. IP Address: ← **IP адрес твоего LoadBalancer**

**Получи IP LoadBalancer:**
```powershell
kubectl get service -n ingress-nginx ingress-nginx-controller

# Или
kubectl get ingress victor-bot-ingress
```

**Проверь DNS:**
```powershell
nslookup victor.97v.ru
# Должен вернуть IP LoadBalancer
```

### Шаг 4: Дождись SSL сертификата

cert-manager автоматически создаст Let's Encrypt сертификат.

**Проверь статус:**
```powershell
kubectl get certificate victor-bot-tls

# Детали
kubectl describe certificate victor-bot-tls
```

Обычно занимает 1-3 минуты.

### Шаг 5: Проверь работу API
```powershell
# Health check
curl https://victor.97v.ru/health

# Должно вернуть: {"status":"ok"}
```

---

## 🤖 Настройка Telegram Webhook

После того как API работает на https://victor.97v.ru:

```powershell
# Автоматическая настройка
.\setup_telegram_webhook.ps1 -NgrokUrl "https://victor.97v.ru"

# Или вручную
$token = "8457627946:AAEKY9QoV4yI8A9D5u6lJflralz480uazp8"
$url = "https://victor.97v.ru/api/telegram/webhook"

Invoke-RestMethod "https://api.telegram.org/bot$token/setWebhook?url=$url"

# Проверь
Invoke-RestMethod "https://api.telegram.org/bot$token/getWebhookInfo"
```

---

## 🔧 Управление

### Просмотр логов
```powershell
# Все логи
kubectl logs -l app=victor-bot-v2

# Последние 100 строк
kubectl logs -l app=victor-bot-v2 --tail=100

# Follow (в реальном времени)
kubectl logs -f -l app=victor-bot-v2
```

### Рестарт
```powershell
kubectl rollout restart deployment/victor-bot-v2
```

### Масштабирование
```powershell
# 2 реплики для надежности
kubectl scale deployment victor-bot-v2 --replicas=2
```

### Обновление
```powershell
# Новая версия
.\deploy_victor_production.ps1 -Version "2.0.1"
```

### Откат
```powershell
kubectl rollout undo deployment/victor-bot-v2
```

### Удаление
```powershell
kubectl delete -f k8s/victor-bot/
```

---

## 🐛 Troubleshooting

### Pod не запускается?
```powershell
# Статус pod
kubectl get pods -l app=victor-bot-v2

# Детальное описание
kubectl describe pod -l app=victor-bot-v2

# События
kubectl get events --sort-by='.lastTimestamp'
```

### ImagePullBackOff?
```powershell
# Проверь registry secret
kubectl get secrets

# Создай если нужно
doctl registry kubernetes-manifest | kubectl apply -f -
```

### Не работает Ingress?
```powershell
# Проверь NGINX Ingress Controller
kubectl get pods -n ingress-nginx

# Если нет - установи
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/do/deploy.yaml
```

### Не работает cert-manager?
```powershell
# Проверь cert-manager
kubectl get pods -n cert-manager

# Если нет - установи
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

### Database connection issues?
```powershell
# Проверь секреты
kubectl get secret victor-bot-secrets -o yaml

# Обнови DATABASE_URL если нужно
kubectl create secret generic victor-bot-secrets \
  --from-literal=database-url="postgresql://..." \
  --dry-run=client -o yaml | kubectl apply -f -

# Рестарт после обновления секретов
kubectl rollout restart deployment/victor-bot-v2
```

---

## 📊 Мониторинг

### Prometheus Metrics (если настроен)
```powershell
# Проверь metrics endpoint
curl https://victor.97v.ru/metrics
```

### Grafana Dashboard
Если у тебя есть Grafana - импортируй дашборд для FastAPI приложений.

---

## 🎉 Готово!

После успешного деплоя:

1. ✅ API доступен на https://victor.97v.ru
2. ✅ SSL сертификат активен
3. ✅ Telegram webhook настроен
4. ✅ Данные сохраняются в Supabase

**Отправь сообщение боту и проверь логи:**
```powershell
kubectl logs -f -l app=victor-bot-v2
```

Должны появиться записи о входящих webhook запросах! 🚀
