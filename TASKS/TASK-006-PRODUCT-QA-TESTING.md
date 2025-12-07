# 🎯 TASK-006: Product & QA Testing
## End-to-End Testing (E2E) + User Acceptance Testing (UAT)

**Дата:** 7 декабря 2025, 18:10 MSK  
**Статус:** 🔵 READY FOR ASSIGNMENT  
**Команда:** PRODUCT + QA Team  
**Ответственные:** Elena R. (PM), Dmitry P. (QA Lead), Olga K. (UX/UI)  
**Начало:** 16 декабря 2025, 09:00 MSK  
**Дедлайн:** 18 декабря 2025, 17:00 MSK  
**Приоритет:** 🟡 **HIGH**  
**Дни:** 3 дня (параллельно с TASK-005 завершением)

---

## 🎯 ЦЕЛЬ

Тестирование всех 4 новых API endpoints + интеграция с Telegram Bot.

**Success Criteria:**
- ✅ Все 4 endpoints работают без ошибок
- ✅ Bot корректно вызывает endpoints
- ✅ E2E сценарии пройдены
- ✅ Load testing >100 req/s passed
- ✅ UAT с реальными данными
- ✅ Баги залогированы/исправлены

---

## 📋 ТЕСТИРУЕМЫЕ КОМПОНЕНТЫ

### 🌐 API Endpoints

| # | Endpoint | Тип теста | Примечание |
|:---:|:---|:---|:---|
| 1 | GET `/api/v1/analysis/{id}` | Unit + Integration | Получить результат анализа |
| 2 | POST `/api/v1/batch-process` | Unit + Integration | Массовая обработка |
| 3 | GET `/api/v1/metrics` | Unit + Integration | Метрики системы |
| 4 | WebSocket `/api/v1/live-events` | Integration + Load | Real-time события |

### 📱 Bot Integration

| Компонент | Тест |
|:---|:---|
| `/show` команда | ✓ Показывает данные |
| `/categories` | ✓ Все категории |
| File upload | ✓ Analyzer работает |
| WebSocket events | ✓ Real-time работает |

---

## 🧪 ТЕСТОВЫЕ СЦЕНАРИИ

### Сценарий 1: API /analysis/{id}

```gherkin
Given: Файл проанализирован (есть ID)
When: GET /api/v1/analysis/{id}
Then:
  - Status 200
  - JSON response с type, subtype, tags
  - confidence >= 80
  - Время ответа < 500ms
```

**Test Cases:**
- [ ] Valid ID returns correct data
- [ ] Invalid ID returns 404
- [ ] Missing token returns 401
- [ ] Large ID field tested
- [ ] Performance: <500ms

### Сценарий 2: API /batch-process

```gherkin
Given: 5-10 файлов готовы
When: POST /api/v1/batch-process с file_ids
Then:
  - Status 202 Accepted
  - batch_id returned
  - GET /batch-process/id показывает прогресс
  - Все файлы обработаны
```

**Test Cases:**
- [ ] 5 files batch processing
- [ ] Progress tracking working
- [ ] Webhook callback received
- [ ] Rate limiting tested (>50 req/s)
- [ ] Error handling (invalid file ID)

### Сценарий 3: API /metrics

```gherkin
Given: Система работает сутки
When: GET /api/v1/metrics?period=1d
Then:
  - System uptime > 99.5%
  - Total requests > 1000
  - Error rate < 1%
  - Response time < 100ms (cached)
```

**Test Cases:**
- [ ] Period filter: 1h, 1d, 7d, 30d
- [ ] Cache working (second call <50ms)
- [ ] All metrics present
- [ ] Numbers reasonable

### Сценарий 4: WebSocket /live-events

```gherkin
Given: WebSocket подключение открыто
When: Файл загружается
Then:
  - analysis_started event received
  - analysis_progress events received
  - analysis_completed event received
  - Total events = 3+
```

**Test Cases:**
- [ ] WebSocket connection established
- [ ] Multiple subscribers (5+)
- [ ] Event ordering correct
- [ ] No message loss
- [ ] Disconnection handled

---

## 📊 LOAD TESTING

**Tools:** Locust + K6

### Load Test 1: API Endpoints

```bash
# Test all 4 endpoints under load
locust -f loadtest.py --host=https://97v.ru \
  --users=100 --spawn-rate=10 --run-time=10m
```

**Success Criteria:**
- ✅ GET /api/v1/analysis: >50 req/s, p95 <500ms
- ✅ POST /api/v1/batch-process: >20 req/s, p95 <1000ms
- ✅ GET /api/v1/metrics: >100 req/s, p95 <100ms
- ✅ WebSocket: 50+ concurrent connections

### Load Test 2: Bot Integration

```bash
# Simulate 10 concurrent users uploading files
locust -f bot_loadtest.py --users=10 --spawn-rate=2
```

---

## 🧩 UAT (User Acceptance Testing)

### Real User Scenarios

**Scenario A: File Upload Flow**
```
1. User uploads document.pdf
2. Bot returns: Type=document, tags=[finance, 2025]
3. User confirms: Correct!
4. File saved with metadata
5. GET /api/v1/analysis/{id} returns same data
✅ PASS
```

**Scenario B: Batch Processing**
```
1. User uploads 5 invoices
2. POST /api/v1/batch-process queues them
3. GET /api/v1/batch-process/{batch_id} shows progress
4. All analyzed within 5 minutes
✅ PASS
```

**Scenario C: Real-time Monitoring**
```
1. Analyst opens WebSocket /api/v1/live-events
2. User uploads file in Bot
3. WebSocket shows: analysis_started → progress → completed
4. Analyst sees results in real-time
✅ PASS
```

---

## 🐛 BUG TRACKING

**Format for bug reports:**

```markdown
## BUG: [Endpoint] - [Issue]

**Severity:** 🔴 Critical / 🟡 High / 🟢 Low
**Steps to Reproduce:**
1. Step 1
2. Step 2
3. Step 3

**Expected:** ...
**Actual:** ...

**Logs:** [paste logs]
**Screenshot:** [if applicable]
```

**Bugs stored in:**
```
TASKS/TASK-006-BUGS-FOUND.md
```

---

## 📝 TESTING CHECKLIST

### Preparation (30 min)
- [ ] Read TASK-005-AI-ML-CHECKLIST.md
- [ ] Understand 4 endpoints
- [ ] Setup test environment
- [ ] Prepare test data
- [ ] Review Bot documentation

### Unit Testing (2 hours)
- [ ] Test GET /api/v1/analysis/{id} (10 test cases)
- [ ] Test POST /api/v1/batch-process (8 test cases)
- [ ] Test GET /api/v1/metrics (6 test cases)
- [ ] Test WebSocket /api/v1/live-events (8 test cases)

### Integration Testing (2 hours)
- [ ] Bot → GET /api/v1/analysis works
- [ ] Bot → POST /api/v1/batch-process works
- [ ] Metrics reflect Bot activity
- [ ] WebSocket events for Bot uploads

### Load Testing (1.5 hours)
- [ ] Run Locust load test
- [ ] Monitor response times
- [ ] Check error rates
- [ ] Verify autoscaling
- [ ] Document results

### UAT (1.5 hours)
- [ ] Real-world scenario 1: File upload
- [ ] Real-world scenario 2: Batch processing
- [ ] Real-world scenario 3: Real-time monitoring
- [ ] Edge cases testing

### Bug Reporting (1 hour)
- [ ] Document all bugs
- [ ] Assign severity levels
- [ ] Create GitHub Issues for critical bugs
- [ ] Escalate if needed

---

## 🎯 SUCCESS CRITERIA

✅ **API Testing:**
- All 4 endpoints pass unit tests
- 95%+ success rate on integration tests
- Response times within limits
- Error handling working

✅ **Load Testing:**
- >50 req/s for analysis endpoint
- >100 req/s for metrics endpoint
- 50+ concurrent WebSocket connections
- <1% error rate under load

✅ **UAT:**
- 3 real-world scenarios completed
- All critical bugs resolved
- Product team sign-off

✅ **Documentation:**
- Test plan completed
- Bug report written
- Results documented
- Recommendations provided

---

## 📄 COMPLETION REPORT

**File:** `TASKS/TASK-006-PRODUCT-QA-TESTING-COMPLETED.md`

**Include:**
- Test execution summary
- Pass/fail rates by endpoint
- Load test results
- Bug list and resolution status
- UAT results
- Performance metrics
- Recommendations
- Sign-off

---

## 🔗 RESOURCES

**Documentation:**
- https://github.com/vik9541/super-brain-digital-twin/blob/main/TASKS/TASK-005-AI-ML-CHECKLIST.md
- https://github.com/vik9541/super-brain-digital-twin/blob/main/SUPER_BRAIN_FLEXIBLE_TZ_v4.0.md

**Tools:**
- pytest: Unit testing
- Locust: Load testing
- Postman: API testing
- Selenium: Bot UI testing

**Examples:**
- [TASK-002-INFRA-CHECKLIST.md](./TASK-002-INFRA-CHECKLIST.md) - Template
- [TASK-004-GRAFANA-DASHBOARD-COMPLETED.md](./TASK-004-GRAFANA-DASHBOARD-COMPLETED.md) - Completed example

---

**Status:** 🔵 READY FOR ASSIGNMENT  
**Team:** PRODUCT + QA  
**Start Date:** 16 Dec 2025, 09:00 MSK  
**Deadline:** 18 Dec 2025, 17:00 MSK  
**Expected Duration:** 3 days

**Next:** TASK-007 (Integration & DevOps final checks)