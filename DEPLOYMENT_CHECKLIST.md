# ✅ Victor Bot v2.0 Production Deployment Checklist

## Перед деплоем

### 1. DigitalOcean Setup
- [ ] doctl установлен и настроен (`doctl auth init`)
- [ ] Kubernetes кластер доступен (`kubectl cluster-info`)
- [ ] Container Registry создан (`doctl registry get`)
- [ ] Registry credentials настроены (`doctl registry login`)

### 2. Кластер готов
- [ ] NGINX Ingress Controller установлен
  ```powershell
  kubectl get pods -n ingress-nginx
  ```
- [ ] cert-manager установлен (для SSL)
  ```powershell
  kubectl get pods -n cert-manager
  ```
- [ ] LoadBalancer создан
  ```powershell
  kubectl get svc -n ingress-nginx ingress-nginx-controller
  ```

### 3. DNS конфигурация
- [ ] Получен IP LoadBalancer
  ```powershell
  kubectl get svc -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
  ```
- [ ] DNS запись создана: `victor.97v.ru` → LoadBalancer IP
- [ ] DNS пропагация проверена
  ```powershell
  nslookup victor.97v.ru
  ```

---

## Деплой

### 4. Обновить конфигурацию
- [ ] В `k8s/victor-bot/03-deployment.yaml` обновить:
  ```yaml
  image: registry.digitalocean.com/YOUR_REGISTRY/victor-bot:2.0.0
  ```
  Заменить `YOUR_REGISTRY` на реальное имя

- [ ] Проверить секреты в `k8s/victor-bot/01-secrets.yaml`:
  - [x] DATABASE_URL (Supabase)
  - [x] TELEGRAM_BOT_TOKEN
  - [x] VICTOR_CHAT_ID
  - [ ] OPENAI_API_KEY (если будет использоваться)

### 5. Build & Push Docker Image
```powershell
# Опция 1: Автоматически (через скрипт)
.\deploy_victor_production.ps1 -Registry "registry.digitalocean.com/YOUR_REGISTRY"

# Опция 2: Вручную
docker build -t victor-bot:2.0.0 -f Dockerfile.victor-bot .
docker tag victor-bot:2.0.0 registry.digitalocean.com/YOUR_REGISTRY/victor-bot:2.0.0
docker push registry.digitalocean.com/YOUR_REGISTRY/victor-bot:2.0.0
```

- [ ] Docker image собран
- [ ] Docker image запушен в registry
- [ ] Image виден в DigitalOcean Container Registry

### 6. Deploy to Kubernetes
```powershell
# Применить манифесты
kubectl apply -f k8s/victor-bot/01-secrets.yaml
kubectl apply -f k8s/victor-bot/02-configmap.yaml
kubectl apply -f k8s/victor-bot/03-deployment.yaml
kubectl apply -f k8s/victor-bot/04-service.yaml
kubectl apply -f k8s/victor-bot/05-ingress.yaml
```

- [ ] Secrets созданы
- [ ] ConfigMap создан
- [ ] Deployment создан
- [ ] Service создан
- [ ] Ingress создан

### 7. Дождаться запуска
```powershell
kubectl rollout status deployment/victor-bot-v2 --timeout=300s
```

- [ ] Deployment готов (READY 1/1)
- [ ] Pod запущен (Running)
- [ ] Health check проходит

---

## После деплоя

### 8. Проверить SSL сертификат
```powershell
kubectl get certificate victor-bot-tls
```

- [ ] Certificate STATUS = Ready
- [ ] HTTPS работает: `https://victor.97v.ru`

### 9. Тестирование API
```powershell
# Health check
curl https://victor.97v.ru/health

# Root endpoint
curl https://victor.97v.ru/
```

- [ ] `/health` возвращает `{"status":"ok"}`
- [ ] `/` возвращает информацию о сервисе

### 10. Настроить Telegram Webhook
```powershell
.\setup_telegram_webhook.ps1 -NgrokUrl "https://victor.97v.ru"
```

- [ ] Webhook установлен
- [ ] getWebhookInfo показывает правильный URL
- [ ] Нет ошибок в last_error_message

### 11. Финальное тестирование
- [ ] Отправить текстовое сообщение боту
- [ ] Проверить логи: `kubectl logs -f -l app=victor-bot-v2`
- [ ] Проверить запись в Supabase (таблица victor_inbox)

---

## Мониторинг

### 12. Настроить алерты (опционально)
- [ ] Prometheus scraping настроен
- [ ] Grafana dashboard импортирован
- [ ] Alertmanager правила созданы

### 13. Backup & Recovery
- [ ] Supabase автобэкапы включены
- [ ] Kubernetes манифесты в Git
- [ ] Docker образы в registry

---

## Troubleshooting

### Если Pod не запускается:
```powershell
kubectl describe pod -l app=victor-bot-v2
kubectl logs -l app=victor-bot-v2
```

### Если ImagePullBackOff:
```powershell
doctl registry kubernetes-manifest | kubectl apply -f -
kubectl rollout restart deployment/victor-bot-v2
```

### Если SSL не работает:
```powershell
kubectl describe certificate victor-bot-tls
kubectl get challenges
kubectl logs -n cert-manager -l app=cert-manager
```

### Если webhook не работает:
```powershell
# Проверить Ingress
kubectl describe ingress victor-bot-ingress

# Проверить логи NGINX
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx

# Проверить через Telegram API
$token = "8457627946:AAEKY9QoV4yI8A9D5u6lJflralz480uazp8"
Invoke-RestMethod "https://api.telegram.org/bot$token/getWebhookInfo" | ConvertTo-Json -Depth 5
```

---

## 🎉 Success Criteria

Деплой считается успешным когда:

✅ Pod в статусе Running  
✅ Health check проходит  
✅ HTTPS доступен с валидным SSL  
✅ Telegram webhook настроен без ошибок  
✅ Сообщения боту сохраняются в Supabase  
✅ Логи показывают корректную обработку  

---

## Команды для быстрой проверки

```powershell
# Статус всего
kubectl get all -l app=victor-bot-v2

# Логи в реальном времени
kubectl logs -f -l app=victor-bot-v2

# Проверка Ingress
kubectl get ingress victor-bot-ingress

# Проверка SSL
kubectl get certificate

# Тест API
curl -v https://victor.97v.ru/health

# Webhook info
$token = "8457627946:AAEKY9QoV4yI8A9D5u6lJflralz480uazp8"
Invoke-RestMethod "https://api.telegram.org/bot$token/getWebhookInfo"
```

---

**Дата последнего обновления:** 14 декабря 2025  
**Версия Victor Bot:** 2.0.0  
**Статус:** Ready for Production 🚀
