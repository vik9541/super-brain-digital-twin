# 📋 TASK-005: API Extensions — AI-ML TEAM CHECKLIST

**🟠 Статус:** ГОТОВА К СТАРТУ
**👤 Команда:** AI-ML
**💼 Ответственные:** Andrey M., Dmitry K., Igor S.
**📅 Дедлайн:** 12 декабря 2025, 17:00 MSK
**⚡ Приоритет:** 🟡 HIGH

---

## 📝 ТЕХНИЧЕСКОЕ ЗАДАНИЕ

**Цель:** Внедрение 4 новых API endpoints в production с полным тестированием, документацией и мониторингом.

**4 Новых Endpoints:**
1. `GET /api/v1/analysis/{id}` - Получение результата анализа по ID
2. `POST /api/v1/batch-process` - Пакетная обработка данных
3. `GET /api/v1/metrics` - Системные метрики
4. `WebSocket /api/v1/live-events` - Real-time события

---

## 📄 PHASE 1: PREPARATION (30 min)

### Step 1.1: Прочтите документацию

- [ ] Код API: https://github.com/vik9541/super-brain-digital-twin/blob/main/api/main.py
- [ ] Tests: https://github.com/vik9541/super-brain-digital-twin/blob/main/tests/test_api_extensions.py
- [ ] Requirements: https://github.com/vik9541/super-brain-digital-twin/blob/main/requirements.api.txt
- [ ] Dockerfile: https://github.com/vik9541/super-brain-digital-twin/blob/main/Dockerfile.api

### Step 1.2: Настройка окружения

```bash
# Clone repository
$ cd /tmp && git clone https://github.com/vik9541/super-brain-digital-twin.git
$ cd super-brain-digital-twin
$ git pull origin main

# Create virtual environment
$ python3 -m venv venv
$ source venv/bin/activate

# Install dependencies
$ pip install -r requirements.api.txt
```

- [ ] Repository клонирован
- [ ] Venv создан
- [ ] Dependencies установлены

### Step 1.3: Получите credentials

```bash
# Supabase credentials
$ echo "SUPABASE_URL=$SUPABASE_URL"
$ echo "SUPABASE_KEY=$SUPABASE_KEY"

# Test credentials
$ curl -H "apikey: $SUPABASE_KEY" $SUPABASE_URL/rest/v1/
```

- [ ] Supabase credentials проверены
- [ ] Connection test OK

---

## 🧪 PHASE 2: TESTING LOCALLY (1.5 hours)

### Step 2.1: Запустите API локально

```bash
# Run FastAPI
$ cd api
$ uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Check health
$ curl http://localhost:8000/health
# Expected: {"status":"healthy","timestamp":"..."}
```

- [ ] API запущено на localhost:8000
- [ ] Health check passed

### Step 2.2: Тестирование Endpoint 1 - GET /api/v1/analysis/{id}

```bash
# Test GET analysis
$ curl http://localhost:8000/api/v1/analysis/test-123

# Expected response:
# {
#   "id": "test-123",
#   "status": "completed",
#   "input_text": "Sample analysis text",
#   "analysis_result": {"score": 0.95, "tags": ["important"]},
#   "created_at": "2025-12-12T...",
#   "updated_at": "2025-12-12T...",
#   "error": null
# }
```

- [ ] GET /api/v1/analysis/{id} работает
- [ ] Response format correct
- [ ] Status 200 OK

### Step 2.3: Тестирование Endpoint 2 - POST /api/v1/batch-process

```bash
# Test batch process
$ curl -X POST http://localhost:8000/api/v1/batch-process \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"id": "1", "data": {"text": "Sample 1"}, "priority": 5},
      {"id": "2", "data": {"text": "Sample 2"}, "priority": 8}
    ],
    "timeout": 300
  }'

# Expected:
# {
#   "batch_id": "550e8400-e29b-41d4-a716-446655440000",
#   "total_items": 2,
#   "processed": 2,
#   "failed": 0,
#   "results": [...],
#   "total_processing_time_ms": 150.5
# }
```

- [ ] POST /api/v1/batch-process работает
- [ ] Batch processing успешен
- [ ] Все items обработаны

### Step 2.4: Тестирование Endpoint 3 - GET /api/v1/metrics

```bash
# Test metrics
$ curl http://localhost:8000/api/v1/metrics

# Expected:
# {
#   "timestamp": "2025-12-12T...",
#   "cpu_percent": 45.2,
#   "memory_percent": 62.3,
#   "memory_mb": 512.5,
#   "disk_percent": 35.1,
#   "uptime_seconds": 3600.5,
#   "http_metrics": {...},
#   "batch_metrics": {...},
#   "api_health": "healthy"
# }
```

- [ ] GET /api/v1/metrics работает
- [ ] Метрики собираются
- [ ] Health status правильный

### Step 2.5: Тестирование Endpoint 4 - WebSocket

```python
# test_websocket.py
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/api/v1/live-events"
    async with websockets.connect(uri) as websocket:
        # Subscribe
        await websocket.send(json.dumps({
            "action": "subscribe",
            "events": ["batch_completed", "error"]
        }))
        response = await websocket.recv()
        print(f"Received: {response}")
        
        # Ping
        await websocket.send(json.dumps({"action": "ping"})
        pong = await websocket.recv()
        print(f"Pong: {pong}")

asyncio.run(test_websocket())
```

```bash
$ python test_websocket.py
```

- [ ] WebSocket connection established
- [ ] Subscribe/unsubscribe работает
- [ ] Ping/pong работает

---

## 🐳 PHASE 3: DOCKER BUILD & DEPLOY (1 hour)

### Step 3.1: Build Docker image

```bash
$ docker build -f Dockerfile.api -t super-brain-api:v3.0.0 .
```

- [ ] Docker build успешен
- [ ] Image size разумный (<500MB)

### Step 3.2: Tag and push

```bash
$ REGISTRY="registry.digitalocean.com/your-account"
$ docker tag super-brain-api:v3.0.0 $REGISTRY/super-brain-api:v3.0.0
$ docker tag super-brain-api:v3.0.0 $REGISTRY/super-brain-api:latest
$ docker push $REGISTRY/super-brain-api:v3.0.0
$ docker push $REGISTRY/super-brain-api:latest
```

- [ ] Images pushed to registry
- [ ] Digest сохранен

### Step 3.3: Deploy to K8s

```bash
# Update K8s deployment
$ kubectl apply -f k8s/api-deployment.yaml
$ kubectl apply -f k8s/api-service.yaml

# Check status
$ kubectl get pods -n production | grep api
$ kubectl logs -f deployment/super-brain-api -n production
```

- [ ] K8s deployment updated
- [ ] Pods running
- [ ] No errors in logs

---

## ✅ PHASE 4: PRODUCTION TESTING (30 min)

### Step 4.1: Test endpoints в production

```bash
# Get production URL
$ PROD_URL=$(kubectl get svc super-brain-api -n production -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Test all endpoints
$ curl http://$PROD_URL:8000/api/v1/analysis/test-prod-123
$ curl -X POST http://$PROD_URL:8000/api/v1/batch-process -d '{...}'
$ curl http://$PROD_URL:8000/api/v1/metrics
```

- [ ] All endpoints работают в production
- [ ] Response times <500ms
- [ ] No 5xx errors

### Step 4.2: Load testing

```bash
# Use Apache Bench
$ ab -n 1000 -c 10 http://$PROD_URL:8000/api/v1/metrics

# Check results:
# - Requests per second > 50
# - Mean time per request < 200ms
# - Failed requests = 0
```

- [ ] Load test passed
- [ ] Performance acceptable

---

## 📊 PHASE 5: MONITORING & DOCUMENTATION (1 hour)

### Step 5.1: Verify Prometheus metrics

```bash
$ kubectl port-forward -n monitoring svc/prometheus-server 9090:80 &

# Check metrics in Prometheus:
# - http_requests_total
# - http_request_duration_seconds
# - batch_jobs_total
# - websocket_connections_active
```

- [ ] Prometheus collecting metrics
- [ ] All custom metrics present

### Step 5.2: Create Grafana dashboard

- [ ] Dashboard created
- [ ] 4 panels (по одному на endpoint)
- [ ] Alerts configured

### Step 5.3: API Documentation

```bash
# Generate OpenAPI docs
$ curl http://$PROD_URL:8000/docs > api_docs.html
$ curl http://$PROD_URL:8000/openapi.json > openapi.json
```

- [ ] OpenAPI docs generated
- [ ] Docs pushed to repo

---

## 📝 PHASE 6: COMPLETION REPORT

### Step 6.1: Create completion report

**File:** `TASKS/TASK-005-API-EXTENSIONS-COMPLETED.md`

```markdown
# ✅ TASK-005: API Extensions — COMPLETION REPORT

**Статус:** 🟢 COMPLETED
**Дата Начала:** 12 дек 2025 09:00 MSK
**Дата Завершения:** [TODAY] [TIME] MSK
**Ответственные:** Andrey M., Dmitry K., Igor S.

## ✅ Что сделано

### 4 New Endpoints
- [x] GET /api/v1/analysis/{id}
- [x] POST /api/v1/batch-process
- [x] GET /api/v1/metrics
- [x] WebSocket /api/v1/live-events

### Testing
- [x] Unit tests: 100% coverage
- [x] Integration tests: PASSED
- [x] Load test: >100 req/s
- [x] WebSocket stress test: 50 concurrent connections

### Deployment
- [x] Docker image built and pushed
- [x] K8s deployed successfully
- [x] Production endpoints verified

### Monitoring
- [x] Prometheus metrics active
- [x] Grafana dashboard created
- [x] Alerts configured

## 📊 Key Metrics

| Metric | Value |
|:---|:---|
| API Response Time (p99) | [XX] ms |
| Batch Processing Time | [XX] sec |
| WebSocket Connections | [XX] active |
| Error Rate | 0% |
| Uptime | 100% |

## 🔗 GitHub References
- Code: https://github.com/vik9541/super-brain-digital-twin/blob/main/api/main.py
- Tests: https://github.com/vik9541/super-brain-digital-twin/blob/main/tests/test_api_extensions.py
- Dockerfile: https://github.com/vik9541/super-brain-digital-twin/blob/main/Dockerfile.api

## 📸 Screenshots
- API Docs: [screenshot]
- Grafana Dashboard: [screenshot]
- Prometheus Metrics: [screenshot]
- Load Test Results: [screenshot]

## ✅ Success Criteria
- [x] All 4 endpoints deployed
- [x] Tests passed
- [x] Performance >50 req/s
- [x] Documentation complete
- [x] Monitoring active

---
**Verified by:** [YOUR_MANAGER]
**Date:** [TODAY]
```

- [ ] Completion report created

### Step 6.2: Git commit

```bash
$ git add TASKS/TASK-005-API-EXTENSIONS-COMPLETED.md
$ git commit -m "Complete TASK-005: API Extensions deployed successfully"
$ git push origin main
```

- [ ] Report pushed to GitHub

---

## 🆘 TROUBLESHOOTING

**Problem:** Port 8000 already in use
**Solution:**
```bash
$ sudo lsof -i :8000
$ kill -9 [PID]
```

**Problem:** WebSocket connection failed
**Solution:** Check CORS settings and firewall rules

**Problem:** Prometheus metrics not appearing
**Solution:** Verify ServiceMonitor configuration

---

## 🎯 SUCCESS CRITERIA SUMMARY

- [ ] All 4 endpoints deployed and tested
- [ ] Docker image in registry
- [ ] K8s deployment active
- [ ] Load test passed (>50 req/s)
- [ ] Prometheus metrics collecting
- [ ] Grafana dashboard created
- [ ] Documentation complete
- [ ] Completion report in GitHub
- [ ] Zero production errors
- [ ] Team notified in Slack

---

**🎉 Upon successful completion:**
- ✅ Notify team in Slack #super-brain-deployment
- ✅ Update TASKS_ACTIVE.md
- ✅ Schedule celebration 🎊
