# Telegram Bot Single Instance Fix

## роблема
Telegram bot (@astra_VIK_bot) не мог работать с HorizontalPodAutoscaler из-за конфликта API getUpdates в polling режиме.

## Симптомы
- онфликт: "terminated by other getUpdates request"
- ножественные реплики (2+) создавали конкурентные запросы к Telegram API
- Health checks падали из-за отсутствия HTTP сервера (бот в polling режиме)

## ешение

### 1. Replicas: 2 → 1
\\\yaml
spec:
  replicas: 1  # :  ТЬ!
\\\

### 2. HorizontalPodAutoscaler удалён
HPA создавал минимум 2 реплики, что вызывало конфликт.

### 3. Health Checks удалены
\\\yaml
# livenessProbe и readinessProbe закомментированы
# от работает в polling режиме без HTTP сервера
\\\

### 4. Rolling Update Strategy
\\\yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 0  # е создавать новые поды до удаления старых
    maxUnavailable: 1
\\\

## езультат
✅ от @astra_VIK_bot работает стабильно
✅ онфликт getUpdates устранён
✅ Pod status: 1/1 Ready

## 
⚠️  включайте HPA обратно!
⚠️  увеличивайте replicas > 1!

Telegram polling API не поддерживает множественные экземпляры бота.

## ата
15 декабря 2025 г.
