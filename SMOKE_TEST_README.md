# 🧪 Smoke Tests - Руководство

## 📋 Описание

Полный набор smoke-тестов для проверки критических компонентов инфраструктуры 97v.ru Platform после развёртывания.

## ✅ Что проверяется

| # | Компонент | Статус | Описание |
|---|-----------|--------|----------|
| 1 | API Health | ✅ | Liveness probe |
| 2 | API Readiness | ✅ | Readiness probe + dependencies |
| 3 | Redis | ✅ | Connection, Write, Read, TTL (12h) |
| 4 | PostgreSQL | ✅ | Connection, queries, performance |
| 5 | Telegram Auth | ✅ | Bot authentication |
| 6 | Telegram Send | ✅ | Send message capability |
| 7 | File Upload | ✅ | TZ-001 file storage |
| 8 | File List | ✅ | Storage retrieval |
| 9 | Batch Processing | ✅ | Background jobs |
| 10 | Performance | ✅ | API < 1s, DB < 2s |
| 11 | Monitoring | ✅ | Metrics endpoints |

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
pip install pytest pytest-asyncio httpx redis asyncpg python-dotenv
```

### 2. Настройка окружения

Создайте файл `.env` в корне проекта:

```bash
# API Configuration
API_URL=https://api.97v.ru

# Redis (TZ-001)
REDIS_URL=redis://localhost:6379

# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Telegram Bot
TELEGRAM_BOT_TOKEN=1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ
TELEGRAM_CHAT_ID=123456789
```

### 3. Запуск тестов

```bash
# Все тесты
pytest tests/smoke_test.py -v -s

# Один тест
pytest tests/smoke_test.py::test_01_api_health_liveness -v -s

# С подробным выводом
pytest tests/smoke_test.py -v -s --tb=short

# Остановка при первой ошибке
pytest tests/smoke_test.py -v -s -x
```

## 📊 Ожидаемый результат

```
🔍 Test 1: API Liveness Probe
   Status: 200
   Response time: 245ms
   ✅ API is alive (245ms)

🔍 Test 2: API Readiness Probe
   Status: 200
   Database: ✅
   Redis: ✅
   ✅ API is ready with all dependencies

🔍 Test 3: Redis Connection & TTL
   ✅ Redis ping successful
   ✅ Write successful (TTL: 12h)
   ✅ Read successful
   ✅ TTL verified: 43198s (~12.0h)

🔍 Test 4: Database Connection
   ✅ Connection successful (123ms)
   Tables found: 5
     - users
     - files
     - batches
     - metrics
     - logs

🔍 Test 5: Telegram Bot
   Bot: @astra_VIK_bot
   ID: 8457627946
   Name: Astra VIK
   ✅ Telegram bot authenticated

🔍 Test 6: Telegram Send Message
   ✅ Message sent successfully

🔍 Test 7: File Upload
   ✅ File uploaded: abc123-def456

🔍 Test 8: File List
   Files in storage: 42
   ✅ File list retrieved

🔍 Test 9: Batch Processing
   ✅ Batch job triggered: job-789

🔍 Test 10: API Performance
   /health: 200 (24ms)
   /ready: 200 (156ms)
   /: 200 (89ms)
   ✅ Average response time: 90ms

🔍 Test 11: Monitoring Endpoints
   ✅ Prometheus metrics: 200
   ✅ Health check: 200

============================================================
📊 SMOKE TEST SUMMARY
============================================================
✅ All critical components tested
🌐 API URL: https://api.97v.ru
⚡ Redis: Configured
🗄️  Database: Configured
🤖 Telegram: Configured
============================================================
🎯 Ready for production deployment!
============================================================

======================== 11 passed in 3.45s ========================
```

## 🔧 Диагностика проблем

### ❌ API Health Failed

**Проблема**: `API health check failed`

**Причины**:
- API не запущен
- Неверный URL
- Firewall блокирует доступ

**Решение**:
```bash
# Проверить доступность
curl https://api.97v.ru/health

# Проверить в Kubernetes
kubectl get pods -n production
kubectl logs deployment/digital-twin-api -n production

# Проверить ingress
kubectl get ingress -n production
```

### ❌ Redis Connection Failed

**Проблема**: `Redis ping failed`

**Причины**:
- Redis не запущен
- Неверный REDIS_URL
- Сетевая проблема

**Решение**:
```bash
# Проверить Redis в Kubernetes
kubectl get pods -n production | grep redis
kubectl logs deployment/redis -n production

# Проверить connection string
echo $REDIS_URL

# Тест вручную
redis-cli -u redis://localhost:6379 ping
```

### ❌ Database Connection Failed

**Проблема**: `Database query failed`

**Причины**:
- PostgreSQL недоступен
- Неверные credentials
- Database не существует

**Решение**:
```bash
# Проверить connection string
echo $DATABASE_URL

# Тест вручную
psql $DATABASE_URL -c "SELECT 1"

# Проверить в Supabase
# Dashboard → Project Settings → Database
```

### ❌ Telegram Bot Failed

**Проблема**: `Telegram bot authentication failed`

**Причины**:
- Неверный токен
- Токен revoked
- Webhook конфликт

**Решение**:
```bash
# Проверить токен
curl https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getMe

# Удалить webhook (если есть)
curl https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/deleteWebhook

# Получить новый токен от @BotFather
```

### ❌ Performance Test Failed

**Проблема**: `Average response time exceeds threshold`

**Причины**:
- Высокая нагрузка
- Медленные queries
- Network latency

**Решение**:
```bash
# Проверить ресурсы в Kubernetes
kubectl top pods -n production
kubectl top nodes

# Проверить Grafana metrics
# https://grafana.97v.ru

# Проверить логи
kubectl logs deployment/digital-twin-api -n production --tail=100
```

## 🐳 Docker интеграция

### Dockerfile для тестов

```dockerfile
FROM python:3.11-slim

WORKDIR /tests

COPY requirements-test.txt .
RUN pip install --no-cache-dir -r requirements-test.txt

COPY tests/ tests/
COPY .env .env

CMD ["pytest", "tests/smoke_test.py", "-v", "-s"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  smoke-tests:
    build:
      context: .
      dockerfile: Dockerfile.test
    environment:
      - API_URL=https://api.97v.ru
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=${DATABASE_URL}
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
    depends_on:
      - redis
    networks:
      - test-network

  redis:
    image: redis:7-alpine
    networks:
      - test-network

networks:
  test-network:
    driver: bridge
```

### Запуск в Docker

```bash
# Build
docker build -t smoke-tests -f Dockerfile.test .

# Run
docker run --env-file .env smoke-tests

# С Docker Compose
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## 🔄 CI/CD интеграция

### GitHub Actions

```yaml
name: Smoke Tests

on:
  deployment_status:

jobs:
  smoke-tests:
    if: github.event.deployment_status.state == 'success'
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install pytest pytest-asyncio httpx redis asyncpg python-dotenv
      
      - name: Run smoke tests
        env:
          API_URL: https://api.97v.ru
          REDIS_URL: ${{ secrets.REDIS_URL }}
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
        run: |
          pytest tests/smoke_test.py -v -s
      
      - name: Notify on failure
        if: failure()
        uses: appleboy/telegram-action@master
        with:
          to: ${{ secrets.TELEGRAM_CHAT_ID }}
          token: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          message: |
            ❌ Smoke tests FAILED
            Deployment: ${{ github.event.deployment.environment }}
            Commit: ${{ github.sha }}
```

## 📈 Kubernetes CronJob

Запуск тестов каждый час для проверки здоровья:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: smoke-tests
  namespace: production
spec:
  schedule: "0 * * * *"  # Каждый час
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: smoke-tests
            image: registry.digitalocean.com/digital-twin-registry/smoke-tests:latest
            env:
            - name: API_URL
              value: "https://api.97v.ru"
            - name: REDIS_URL
              valueFrom:
                secretKeyRef:
                  name: redis-credentials
                  key: url
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: supabase-credentials
                  key: DATABASE_URL
            - name: TELEGRAM_BOT_TOKEN
              valueFrom:
                secretKeyRef:
                  name: telegram-credentials
                  key: TELEGRAM_BOT_TOKEN
          restartPolicy: OnFailure
```

## 📝 Требования (TZ-001)

Smoke тесты покрывают требования технического задания:

- ✅ **TZ-001.1**: Redis TTL 12 часов
- ✅ **TZ-001.2**: Файловое хранилище
- ✅ **TZ-001.3**: Telegram bot интеграция
- ✅ **TZ-001.4**: Batch processing
- ✅ **TZ-001.5**: Performance < 1s для API
- ✅ **TZ-001.6**: Database queries < 2s

## 🎯 Best Practices

1. **Запускайте после каждого deploy**
   ```bash
   kubectl apply -f k8s/deployments/
   sleep 30  # Подождать старта
   pytest tests/smoke_test.py
   ```

2. **Мониторьте результаты**
   - Сохраняйте логи в файл
   - Отправляйте в Telegram при ошибках
   - Интегрируйте с Grafana

3. **Используйте в пайплайне**
   - После успешного deploy
   - Перед переключением traffic
   - Блокируйте rollout при failure

4. **Настройте alerts**
   ```yaml
   # prometheus-alerts.yml
   - alert: SmokeTestsFailed
     expr: smoke_tests_failed > 0
     for: 5m
     annotations:
       summary: "Smoke tests failing"
   ```

## 🔗 Связанные документы

- [DEPLOYMENT-SUMMARY.txt](../viktor-agent/DEPLOYMENT-SUMMARY.txt) - Deployment summary
- [CLUSTER-ANALYSIS-FULL.txt](../viktor-agent/CLUSTER-ANALYSIS-FULL.txt) - Infrastructure analysis
- [k8s/deployments/](../k8s/deployments/) - Kubernetes manifests

## 📞 Поддержка

При проблемах:
1. Проверьте логи: `pytest tests/smoke_test.py -v -s --tb=long`
2. Проверьте Kubernetes: `kubectl get pods -n production`
3. Проверьте Grafana: https://grafana.97v.ru
4. Откройте issue в GitHub

---

**Дата**: 15 декабря 2025  
**Версия**: 1.0  
**Статус**: Production Ready ✅
