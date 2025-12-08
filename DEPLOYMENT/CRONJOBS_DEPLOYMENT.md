# CronJobs Deployment Guide - TEAM-2

## Обзор

Этот документ описывает процесс развёртывания двух CronJob сервисов:
- **Batch Analyzer** (TASK-002) - обрабатывает файлы каждые 2 часа
- **Reports Generator** (TASK-003) - генерирует отчёты каждый час

---

## Предварительные требования

- Доступ к Kubernetes кластеру DigitalOcean DOKS
- Docker установлен локально
- kubectl настроен для работы с кластером
- Доступ к DigitalOcean Container Registry

---

## TASK-002: Batch Analyzer Deployment

### 1. Сборка Docker образа

```bash
# Перейти в корневую директорию проекта
cd super-brain-digital-twin

# Собрать Docker образ
docker build -f Dockerfile.batch-analyzer -t batch-analyzer:latest .

# Пометить образ для registry
docker tag batch-analyzer:latest registry.digitalocean.com/digital-twin-registry/batch-analyzer:latest
```

### 2. Push в Container Registry

```bash
# Логин в DigitalOcean registry
doctl registry login

# Push образа
docker push registry.digitalocean.com/digital-twin-registry/batch-analyzer:latest
```

### 3. Применение Kubernetes манифестов

```bash
# Применить RBAC (если ещё не применён)
kubectl apply -f k8s/batch-analyzer-rbac.yaml

# Применить CronJob
kubectl apply -f k8s/batch-analyzer-cronjob.yaml
```

### 4. Проверка статуса

```bash
# Проверить CronJob
kubectl get cronjob -n production batch-analyzer

# Проверить последние запуски
kubectl get jobs -n production | grep batch-analyzer

# Просмотр логов последнего job
kubectl logs -n production job/batch-analyzer-<timestamp> -f
```

---

## TASK-003: Reports Generator Deployment

### 1. Сборка Docker образа

```bash
# Перейти в корневую директорию проекта
cd super-brain-digital-twin

# Собрать Docker образ
docker build -f Dockerfile.reports-generator -t reports-generator:latest .

# Пометить образ для registry
docker tag reports-generator:latest registry.digitalocean.com/digital-twin-registry/reports-generator:latest
```

### 2. Push в Container Registry

```bash
# Логин в DigitalOcean registry (если ещё не выполнен)
doctl registry login

# Push образа
docker push registry.digitalocean.com/digital-twin-registry/reports-generator:latest
```

### 3. Применение Kubernetes манифестов

```bash
# Применить ConfigMap для email настроек (если ещё не применён)
kubectl apply -f k8s/reports-generator-config.yaml

# Применить CronJob
kubectl apply -f k8s/reports-generator-cronjob.yaml
```

### 4. Проверка статуса

```bash
# Проверить CronJob
kubectl get cronjob -n production reports-generator

# Проверить последние запуски
kubectl get jobs -n production | grep reports-generator

# Просмотр логов последнего job
kubectl logs -n production job/reports-generator-<timestamp> -f
```

---

## Настройка Secrets

Оба CronJob используют следующие secrets. Убедитесь, что они созданы в namespace production:

### Supabase Credentials
```bash
kubectl create secret generic supabase-credentials \
  --from-literal=url=$SUPABASE_URL \
  --from-literal=key=$SUPABASE_KEY \
  -n production
```

### API Credentials
```bash
kubectl create secret generic api-credentials \
  --from-literal=perplexity=$PERPLEXITY_API_KEY \
  --from-literal=telegram=$TELEGRAM_BOT_TOKEN \
  --from-literal=telegram-chat-id=$TELEGRAM_CHAT_ID \
  -n production
```

### Email Credentials (для Reports Generator)
```bash
kubectl create secret generic email-credentials \
  --from-literal=user=$SMTP_USER \
  --from-literal=password=$SMTP_PASSWORD \
  -n production
```

---

## Расписание выполнения

- **Batch Analyzer**: Каждые 2 часа (00:00, 02:00, 04:00, ..., 22:00 UTC)
  - Schedule: `0 */2 * * *`
  
- **Reports Generator**: Каждый час (00:00, 01:00, 02:00, ..., 23:00 UTC)
  - Schedule: `0 * * * *`

---

## Мониторинг

### Просмотр всех CronJobs
```bash
kubectl get cronjobs -n production
```

### Просмотр истории выполнений
```bash
# Последние 5 успешных jobs
kubectl get jobs -n production --sort-by=.status.completionTime | tail -n 5

# Неудачные jobs
kubectl get jobs -n production --field-selector status.successful=0
```

### Логи и отладка
```bash
# Логи конкретного pod
kubectl logs -n production <pod-name> -f

# Описание job для отладки
kubectl describe job -n production <job-name>
```

---

## Удаление CronJobs

При необходимости удалить CronJobs:

```bash
# Удалить Batch Analyzer
kubectl delete cronjob -n production batch-analyzer

# Удалить Reports Generator
kubectl delete cronjob -n production reports-generator
```

**Примечание**: Удаление CronJob не удаляет автоматически связанные Jobs. Для их удаления:

```bash
# Удалить все jobs batch-analyzer
kubectl delete jobs -n production -l batch=analyzer

# Удалить все jobs reports-generator
kubectl delete jobs -n production -l reports=generator
```

---

## Troubleshooting

### CronJob не запускается

1. Проверить статус CronJob:
```bash
kubectl describe cronjob -n production <cronjob-name>
```

2. Проверить наличие необходимых secrets:
```bash
kubectl get secrets -n production
```

3. Проверить права ServiceAccount:
```bash
kubectl get sa -n production
kubectl describe sa -n production <service-account-name>
```

### Pod завершается с ошибкой

1. Проверить логи:
```bash
kubectl logs -n production <pod-name>
```

2. Проверить environment variables:
```bash
kubectl exec -n production <pod-name> -- env
```

3. Проверить подключение к Supabase:
```bash
kubectl exec -n production <pod-name> -- python -c "from supabase import create_client; print('OK')"
```

---

## Контакты

При проблемах с развёртыванием обращайтесь:
- **Email**: 9541@bk.ru
- **GitHub**: @vik9541
- **Issue Tracker**: https://github.com/vik9541/super-brain-digital-twin/issues

---

**Дата создания**: 8 декабря 2025  
**Версия**: 1.0  
**Автор**: vik9541
