# 🧪 TEST EXECUTION GUIDE

**Date:** Dec 9, 2025  
**Status:** 🟢 READY TO RUN  
**Updated:** 08:50 AM MSK  
**ℹ️ Supabase Reference:** [SUPABASE_PROJECTS_CLARITY.md](./SUPABASE_PROJECTS_CLARITY.md) (⭐ All Supabase questions answered here!)  

---

## 🚀 QUICK START (5 minutes)

### Step 1: Setup Environment

```bash
# Clone/navigate to project
cd ~/super-brain-digital-twin

# Set environment variables
export SUPABASE_URL="https://lvixtpatqrtuwhygtpjx.supabase.co"
export SUPABASE_KEY="your-api-key-here"
export API_URL="http://97v.ru"
export API_TOKEN="your-token-here"  # Optional

# ℹ️ Project Info: Knowledge_DBnanoAWS (97v.ru - Super Brain)
# See: SUPABASE_PROJECTS_CLARITY.md for detailed Supabase structure
```

### Step 2: Install Dependencies

```bash
# Install test requirements
pip install -r requirements.test.txt

# OR for quick setup
pip install requests supabase python-dotenv
```

### Step 3: Create Supabase Testing Schema

```bash
# Option A: Using psql (direct database connection)
psql "postgresql://postgres:password@db.lvixtpatqrtuwhygtpjx.supabase.co:5432/postgres" \
  -f SUPABASE_TESTING_SCHEMA.sql

# Option B: Using Supabase Dashboard
# 1. Go to: https://app.supabase.com/project/lvixtpatqrtuwhygtpjx/sql
# 2. Copy content of SUPABASE_TESTING_SCHEMA.sql
# 3. Paste and run
```

### Step 4: Run Tests

```bash
# Run all tests
python3 run_tests.py --all

# Or run specific category
python3 run_tests.py --infrastructure
python3 run_tests.py --api
python3 run_tests.py --database
```

**Expected Output:**
```
✅ Kubernetes Pod Status: passed
✅ API Health Check: passed
✅ DNS Resolution (97v.ru): passed
✅ GET /api/v1/analysis/{id}: passed
✅ GET /api/v1/metrics: passed
✅ Database Connection: passed

======================================================================
📈 TEST EXECUTION SUMMARY
======================================================================
Total Tests: 6
✅ Passed: 6
❌ Failed: 0
⚠️  Errors: 0
⏳ Skipped: 0

Pass Rate: 100.0%
Avg Response Time: 245.32ms
======================================================================
```

---

## 💾 DETAILED TESTS BREAKDOWN

### 🔧 INFRASTRUCTURE TESTS (5-10 minutes)

#### Test 1: Kubernetes Cluster

```bash
# Check pod status
kubectl get pods -A

# Expected: api pod showing "Running 1/1 Ready"

# Full health check
kubectl get nodes
kubectl describe nodes
kubectl get services
```

**Validates:**
- ✅ All pods running
- ✅ Services active
- ✅ LoadBalancer accessible
- ✅ Networking functional

#### Test 2: DNS Resolution

```bash
# Check DNS
nslookup 97v.ru
nslookup 97v.ru 8.8.8.8
nslookup 97v.ru 1.1.1.1

# Expected: All resolve to 138.197.254.53
```

**Validates:**
- ✅ DNS propagation complete
- ✅ Correct IP mapping
- ✅ Global DNS availability

#### Test 3: Network Connectivity

```bash
# Test connectivity
ping -c 4 138.197.254.53
ping -c 4 97v.ru

# Test ports
nc -zv 97v.ru 80
nc -zv 97v.ru 443

# Expected: All < 100ms, ports open
```

---

### 🌐 API TESTS (5-10 minutes)

#### Test 1: Health Endpoint

```bash
curl -v http://97v.ru/health

# Expected:
# HTTP/1.1 200 OK
# {"status": "healthy", "uptime_seconds": ...}
```

#### Test 2: Analysis Endpoint

```bash
curl -X GET http://97v.ru/api/v1/analysis/test-id \
  -H "Authorization: Bearer YOUR_TOKEN"

# Expected:
# HTTP/1.1 200 OK or 404 Not Found (both OK for test)
```

#### Test 3: Metrics Endpoint

```bash
curl -X GET http://97v.ru/api/v1/metrics \
  -H "Authorization: Bearer YOUR_TOKEN"

# Expected:
# HTTP/1.1 200 OK
# {"system": {...}, "database": {...}}
```

#### Test 4: SSL Certificate

```bash
openssl s_client -connect 97v.ru:443 -showcerts

# Check validity
openssl s_client -connect 97v.ru:443 2>/dev/null | \
  openssl x509 -noout -dates

# Expected: Certificate valid, > 30 days until expiry
```

---

### 💾 DATABASE TESTS (10-15 minutes)

#### Test 1: Connection

```bash
# Using psql
psql "postgresql://postgres:password@db.lvixtpatqrtuwhygtpjx.supabase.co:5432/postgres" \
  -c "SELECT version();"

# Expected: PostgreSQL 15+ version info
```

#### Test 2: Tables Exist

```sql
-- In Supabase SQL editor or psql:
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public'
ORDER BY table_name;

-- Expected:
-- test_results
-- test_runs
-- test_scenarios
-- test_metrics
-- test_alerts
```

#### Test 3: CRUD Operations

```sql
-- Test INSERT
INSERT INTO test_results 
  (test_name, test_category, test_type, status, environment, created_by)
VALUES 
  ('Test Insert', 'Database', 'Unit', 'passed', 'production', 'testing')
RETURNING *;

-- Test SELECT
SELECT * FROM test_results WHERE test_name = 'Test Insert';

-- Test UPDATE
UPDATE test_results SET status = 'failed' WHERE test_name = 'Test Insert' RETURNING *;

-- Test DELETE
DELETE FROM test_results WHERE test_name = 'Test Insert' RETURNING *;
```

**Expected:** All operations succeed

#### Test 4: Performance

```sql
-- Check query performance
SELECT query, calls, mean_time FROM pg_stat_statements
ORDER BY mean_time DESC LIMIT 5;

-- Expected: All < 100ms
```

---

### 🤖 SERVICE TESTS (10-20 minutes)

#### Test 1: N8N Workflows

```bash
# Check workflow status
curl -X GET "https://lavrentev.app.n8n.cloud/api/v1/workflows" \
  -H "Authorization: Bearer YOUR_N8N_TOKEN"

# Check executions
curl -X GET "https://lavrentev.app.n8n.cloud/api/v1/executions" \
  -H "Authorization: Bearer YOUR_N8N_TOKEN"

# Expected: All workflows active, recent successful executions
```

#### Test 2: Perplexity API

```bash
curl -X POST "https://api.perplexity.ai/chat/completions" \
  -H "Authorization: Bearer $PERPLEXITY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "sonar-reasoning-pro",
    "messages": [{"role": "user", "content": "test"}]
  }'

# Expected: HTTP/1.1 200 OK with response
```

#### Test 3: Telegram Bot

```bash
# Send test message
curl -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
  -H "Content-Type: application/json" \
  -d '{"chat_id": YOUR_CHAT_ID, "text": "🧪 Test"}'

# Expected: Message received by user
```

---

## 📈 AUTOMATED TEST RESULTS TRACKING

### View Latest Results

```sql
-- In Supabase SQL editor:
-- Project: lvixtpatqrtuwhygtpjx (Knowledge_DBnanoAWS)
SELECT 
  test_name,
  test_category,
  status,
  response_time_ms,
  created_at
FROM test_results
ORDER BY created_at DESC
LIMIT 20;
```

### View Health Summary

```sql
SELECT 
  ROUND(100.0 * COUNT(CASE WHEN status = 'passed' THEN 1 END) / COUNT(*), 2) as health_percent,
  COUNT(*) as total_tests_24h,
  SUM(CASE WHEN status = 'passed' THEN 1 ELSE 0 END) as passed,
  SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed
FROM test_results
WHERE created_at > NOW() - INTERVAL '24 hours';
```

### View Failed Tests

```sql
SELECT 
  test_name,
  error_message,
  created_at
FROM test_results
WHERE status = 'failed'
  AND created_at > NOW() - INTERVAL '24 hours'
ORDER BY created_at DESC;
```

---

## ⚠️ TROUBLESHOOTING

### Issue: "Supabase not connected"

**Solution:**
```bash
# Check credentials
echo $SUPABASE_URL
echo $SUPABASE_KEY

# ℹ️ Should be:
# SUPABASE_URL: https://lvixtpatqrtuwhygtpjx.supabase.co
# SUPABASE_KEY: (your-key-here)

# Verify connection manually
python3 << 'EOF'
from supabase import create_client
db = create_client("https://lvixtpatqrtuwhygtpjx.supabase.co", "YOUR_KEY")
print("Connected!")
EOF
```

### Issue: "API timeout"

**Solution:**
```bash
# Check if API is running
kubectl logs deployment/api

# Check network
ping 97v.ru
curl -v http://97v.ru/health
```

### Issue: "DNS not resolving"

**Solution:**
```bash
# Flush DNS cache (macOS)
dscacheutil -flushcache

# Flush DNS cache (Linux)
sudo systemctl restart systemd-resolved

# Test with different servers
nslookup 97v.ru 8.8.8.8
nslookup 97v.ru 1.1.1.1
```

### Issue: "Database table not found"

**Solution:**
```bash
# Re-run schema creation (using correct Project ID: lvixtpatqrtuwhygtpjx)
psql -f SUPABASE_TESTING_SCHEMA.sql

# Or verify table exists
psql -c "\\dt public.test_results"
```

---

## 📈 PERFORMANCE BASELINES

**Target Metrics:**

| Metric | Target | Status |
|:-------|:------:|:------:|
| API Health Response | < 10ms | ✅ |
| DNS Resolution | < 100ms | ✅ |
| Database Query | < 50ms | ✅ |
| API Endpoint | < 500ms | ✅ |
| Kubernetes Ready | 100% | ✅ |
| Pass Rate | > 95% | ✅ |

**How to check:**
```bash
# Run performance test
python3 run_tests.py --all

# View detailed metrics in Supabase (Project: lvixtpatqrtuwhygtpjx)
SELECT 
  test_name,
  AVG(response_time_ms) as avg_response_ms,
  MAX(response_time_ms) as max_response_ms,
  MIN(response_time_ms) as min_response_ms
FROM test_results
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY test_name
ORDER BY avg_response_ms DESC;
```

---

## 📁 LOGGING BEST PRACTICES

### Store in Supabase

```python
from datetime import datetime
import json

# Example: Logging a test result
test_result = {
    "test_name": "API Health Check",
    "test_category": "API",
    "test_type": "Unit",
    "status": "passed",
    "environment": "production",
    "response_time_ms": 8.5,
    "test_data": {"endpoint": "/health"},
    "created_by": "testing-suite"
}

supabase.table("test_results").insert(test_result).execute()
```

### Query Test History

```sql
-- Get test trends over time
SELECT 
  DATE(created_at) as date,
  test_category,
  ROUND(100.0 * SUM(CASE WHEN status = 'passed' THEN 1 ELSE 0 END) / COUNT(*), 2) as pass_rate
FROM test_results
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY DATE(created_at), test_category
ORDER BY date DESC, test_category;
```

---

## ✅ SIGN-OFF CHECKLIST

Before running production tests:

- [ ] All credentials set (SUPABASE_URL: https://lvixtpatqrtuwhygtpjx.supabase.co, SUPABASE_KEY, API_URL)
- [ ] Testing schema created in Supabase (Project: lvixtpatqrtuwhygtpjx)
- [ ] Dependencies installed (pip install -r requirements.test.txt)
- [ ] Kubernetes cluster accessible (kubectl working)
- [ ] DNS resolving correctly (nslookup working)
- [ ] API responding (curl http://97v.ru/health working)
- [ ] Database accessible (psql connection working)
- [ ] N8N workflows operational
- [ ] Perplexity API key valid
- [ ] Telegram bot token valid
- [ ] SUPABASE_PROJECTS_CLARITY.md reviewed (for Supabase structure)

---

## 🔗 USEFUL COMMANDS

```bash
# Quick health check
./quick_health_check.sh

# Run full test suite
python3 run_tests.py --all

# Run specific category
python3 run_tests.py --api

# Monitor real-time
watch kubectl get pods

# View logs
kubectl logs deployment/api -f

# Scale if needed
kubectl scale deployment api --replicas=3

# Check resource usage
kubectl top pods
kubectl top nodes
```

---

## 🔗 KEY REFERENCES

- **📚 Supabase Projects:** [SUPABASE_PROJECTS_CLARITY.md](./SUPABASE_PROJECTS_CLARITY.md) (⭐ Main reference)
- **🔧 Kubernetes Secrets:** [TASK-PRD-03-UPDATED.md](./TASK-PRD-03-UPDATED.md)
- **🧪 Full Testing Guide:** [TESTING.md](./TESTING.md)
- **📈 Test Summary:** [TEST_SUMMARY.md](./TEST_SUMMARY.md)

---

**Last Updated:** Dec 9, 2025, 08:50 AM MSK  
**Supabase Project:** Knowledge_DBnanoAWS (lvixtpatqrtuwhygtpjx)  
**Status:** 🟢 READY FOR TESTING
