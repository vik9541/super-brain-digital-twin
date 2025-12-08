# 🧪 COMPREHENSIVE TESTING GUIDE

**Date:** Dec 8, 2025, 07:59 AM MSK  
**Status:** 🟢 ACTIVE TESTING SESSION  
**Scope:** All services + Infrastructure + API + Database  

---

## 📊 TEST COVERAGE

```
┌─────────────────────────────────────────┐
│         COMPLETE TEST MATRIX             │
├─────────────────────────────────────────┤
│                                         │
│  🔧 INFRASTRUCTURE TESTS                │
│  ├─ Kubernetes Cluster                  │
│  ├─ Docker Registry                     │
│  ├─ Load Balancer                       │
│  └─ Networking                          │
│                                         │
│  🌐 API TESTS (97v.ru)                  │
│  ├─ Health Checks                       │
│  ├─ REST Endpoints                      │
│  ├─ WebSocket Connections               │
│  └─ Performance Metrics                 │
│                                         │
│  💾 DATABASE TESTS (Supabase)           │
│  ├─ Connection Pool                     │
│  ├─ CRUD Operations                     │
│  ├─ Transactions                        │
│  └─ Replication                         │
│                                         │
│  🤖 SERVICE TESTS                       │
│  ├─ N8N Workflows                       │
│  ├─ Perplexity API                      │
│  ├─ Telegram Bot                        │
│  └─ FastAPI Server                      │
│                                         │
│  ✅ INTEGRATION TESTS                   │
│  ├─ End-to-End Flows                    │
│  ├─ Cross-Service Calls                 │
│  └─ Error Handling                      │
│                                         │
└─────────────────────────────────────────┘
```

---

## 🔧 PART 1: INFRASTRUCTURE TESTS

### 1.1 Kubernetes Cluster Health

#### Command: Pod Status Check

```bash
#!/bin/bash
echo "🔍 Checking Kubernetes Pod Status..."

# Get all pods
kubectl get pods -A

# Check for any CrashLoopBackOff pods
echo ""
echo "⚠️ Checking for problematic pods..."
kubectl get pods -A --field-selector=status.phase!=Running

# Pod details
echo ""
echo "📊 Pod Resource Usage:"
kubectl top pods -A
```

**Expected Results:**
- ✅ api pod: `Running 1/1 Ready`
- ✅ No pods in `CrashLoopBackOff` or `Pending`
- ✅ All containers healthy
- ✅ CPU/Memory usage normal

#### Command: Service Status Check

```bash
#!/bin/bash
echo "🔍 Checking Kubernetes Services..."

# Get LoadBalancer service
kubectl get service api

# Get service details
echo ""
echo "📋 Service Details:"
kubectl describe service api

# Check external IP
EXTERNAL_IP=$(kubectl get service api -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo ""
echo "🌐 External IP: $EXTERNAL_IP"
```

**Expected Results:**
- ✅ Service Type: `LoadBalancer`
- ✅ External IP: `138.197.254.53`
- ✅ Port 80 open
- ✅ Status: `Active`

#### Command: Node Status Check

```bash
#!/bin/bash
echo "🔍 Checking Kubernetes Nodes..."

# Get all nodes
kubectl get nodes

# Get node resources
echo ""
echo "📊 Node Resource Allocation:"
kubectl describe nodes

# Check for node issues
echo ""
echo "⚠️ Node Conditions:"
kubectl get nodes -o custom-columns=NAME:.metadata.name,STATUS:.status.conditions[?(@.type==\"Ready\")].status
```

**Expected Results:**
- ✅ All nodes: `Ready`
- ✅ No `NotReady` nodes
- ✅ Sufficient CPU/Memory available
- ✅ Network healthy

#### Command: Persistent Volumes Check

```bash
#!/bin/bash
echo "🔍 Checking Persistent Volumes..."

# Get PVs and PVCs
kubectl get pv
kubectl get pvc -A

# Check volume health
echo ""
echo "📊 Volume Details:"
kubectl describe pv
kubectl describe pvc -A
```

**Expected Results:**
- ✅ PV status: `Bound` or `Available`
- ✅ PVC status: `Bound`
- ✅ No `Lost` or `Failed` volumes

---

### 1.2 Networking Tests

#### Command: DNS Resolution

```bash
#!/bin/bash
echo "🔍 DNS Resolution Tests..."

# Test DNS for 97v.ru
echo "Testing 97v.ru DNS:"
nslookup 97v.ru
dig 97v.ru

# Test from inside pod
echo ""
echo "Testing DNS from pod:"
kubectl run -it --image=busybox test-dns --restart=Never -- nslookup 97v.ru

# Test DNS propagation globally
echo ""
echo "Testing with different DNS servers:"
nslookup 97v.ru 8.8.8.8         # Google
nslookup 97v.ru 1.1.1.1         # Cloudflare
nslookup 97v.ru 77.88.8.8       # Yandex
```

**Expected Results:**
- ✅ All nslookup resolve to `138.197.254.53`
- ✅ DNS propagation: ~100% globally
- ✅ No DNS failures

#### Command: Network Connectivity

```bash
#!/bin/bash
echo "🔍 Network Connectivity Tests..."

# Ping API
echo "Testing connectivity to 138.197.254.53:"
ping -c 4 138.197.254.53

# Traceroute to API
echo ""
echo "Testing route to API:"
traceroute 138.197.254.53

# Port connectivity
echo ""
echo "Testing port 80/443:"
nc -zv 138.197.254.53 80
nc -zv 138.197.254.53 443

# Internal pod connectivity
echo ""
echo "Testing internal Kubernetes DNS:"
kubectl run -it --image=busybox test-conn --restart=Never -- wget -O- http://api
```

**Expected Results:**
- ✅ ICMP ping successful (< 100ms)
- ✅ Port 80 open
- ✅ Port 443 open (SSL)
- ✅ Route latency acceptable

---

## 🌐 PART 2: API TESTS (97v.ru)

### 2.1 Health Checks

#### Test: API Health Endpoint

```bash
#!/bin/bash
echo "🔍 Testing API Health Endpoint..."

# Test basic health
curl -v http://97v.ru/health

# Expected: 
# HTTP/1.1 200 OK
# {"status": "healthy", "timestamp": "2025-12-08T07:59:00Z"}

# Test HTTPS
curl -v https://97v.ru/health

# Test from pod
kubectl run -it --image=curlimages/curl test-api --restart=Never -- \
  curl http://api:8000/health
```

**Expected Status Code:** `200 OK`

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-08T07:59:00Z",
  "uptime_seconds": 28800,
  "version": "1.0.0"
}
```

#### Test: Readiness Probe

```bash
#!/bin/bash
echo "🔍 Testing Readiness Probe..."

# Check if API is ready for requests
curl -v http://97v.ru/ready

# Expected:
# HTTP/1.1 200 OK
# Dependencies: all healthy
```

**Expected Response:**
```json
{
  "ready": true,
  "dependencies": {
    "database": "connected",
    "redis": "connected",
    "supabase": "connected"
  }
}
```

#### Test: Liveness Probe

```bash
#!/bin/bash
echo "🔍 Testing Liveness Probe..."

# Check if API process is alive
curl -v http://97v.ru/live

# Expected:
# HTTP/1.1 200 OK
# Process alive and responsive
```

### 2.2 REST Endpoint Tests

#### Test: GET /api/v1/analysis/{id}

```bash
#!/bin/bash
echo "🧪 Testing GET /api/v1/analysis/{id}..."

# Test with valid ID
TEST_ID="550e8400-e29b-41d4-a716-446655440000"

curl -X GET \
  "http://97v.ru/api/v1/analysis/$TEST_ID" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"

# Expected:
# HTTP/1.1 200 OK
# {
#   "id": "550e8400...",
#   "file_id": "...",
#   "analysis_result": {...},
#   "status": "completed"
# }

# Test with invalid ID (should return 404)
curl -X GET \
  "http://97v.ru/api/v1/analysis/invalid-id" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Expected:
# HTTP/1.1 404 Not Found
```

#### Test: POST /api/v1/batch-process

```bash
#!/bin/bash
echo "🧪 Testing POST /api/v1/batch-process..."

curl -X POST \
  "http://97v.ru/api/v1/batch-process" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "file_ids": ["id1", "id2", "id3"],
    "priority": "high",
    "notify_on_completion": true
  }'

# Expected:
# HTTP/1.1 202 Accepted
# {
#   "batch_id": "batch-uuid-12345",
#   "file_count": 3,
#   "status": "queued"
# }
```

#### Test: GET /api/v1/metrics

```bash
#!/bin/bash
echo "🧪 Testing GET /api/v1/metrics..."

curl -X GET \
  "http://97v.ru/api/v1/metrics?period=7d" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Expected:
# HTTP/1.1 200 OK
# {
#   "timestamp": "2025-12-08T07:59:00Z",
#   "system": {...},
#   "ai_analysis": {...},
#   "database": {...}
# }
```

### 2.3 WebSocket Tests

#### Test: WebSocket Connection

```bash
#!/bin/bash
echo "🧪 Testing WebSocket /api/v1/live-events..."

# Using wscat (npm install -g wscat)
wscat -c "wss://97v.ru/api/v1/live-events" \
  --header "Authorization: Bearer YOUR_TOKEN"

# Or using websocat (brew install websocat)
websocat "wss://97v.ru/api/v1/live-events" \
  --header "Authorization: Bearer YOUR_TOKEN"

# Expected incoming messages:
# {"type": "analysis_started", "filename": "document.pdf"}
# {"type": "analysis_progress", "progress_percent": 25}
# {"type": "analysis_completed", "analysis_result": {...}}
```

**Expected Behavior:**
- ✅ WebSocket connection established
- ✅ Messages flowing in real-time
- ✅ Connection stable for > 5 minutes

### 2.4 SSL/TLS Tests

#### Test: SSL Certificate

```bash
#!/bin/bash
echo "🔍 Testing SSL Certificate..."

# Check certificate
openssl s_client -connect 97v.ru:443 -showcerts

# Check certificate dates
echo ""
echo "Certificate validity:"
openssl s_client -connect 97v.ru:443 2>/dev/null | \
  openssl x509 -noout -dates

# Check certificate chain
echo ""
echo "Certificate chain:"
openssl s_client -connect 97v.ru:443 2>/dev/null | \
  openssl x509 -noout -issuer -subject

# Test SSL security
echo ""
echo "SSL security test:"
testssl.sh https://97v.ru
```

**Expected Results:**
- ✅ Certificate: Valid
- ✅ Issuer: Let's Encrypt
- ✅ Expiry: > 30 days
- ✅ Chain: Complete
- ✅ No SSL errors

---

## 💾 PART 3: DATABASE TESTS (Supabase)

### 3.1 Connection Tests

#### Test: Connection Pool

```sql
-- Check current connections
SELECT 
  pid, 
  usename, 
  application_name, 
  state, 
  query_start,
  state_change
FROM pg_stat_activity
WHERE datname = 'postgres'
ORDER BY query_start DESC;

-- Expected: 5-20 active connections from FastAPI connection pool
```

#### Test: Connection Parameters

```bash
#!/bin/bash
echo "🔍 Testing Supabase Connection..."

# Test with psql
psql "postgresql://[user]:[password]@[host]:[port]/postgres" \
  -c "SELECT version();"

# Test with Python
python3 << 'EOF'
import psycopg2

try:
    conn = psycopg2.connect(
        host="your-supabase-host.supabase.co",
        database="postgres",
        user="postgres",
        password="your-password"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    print("✅ Database connected:", cursor.fetchone())
    conn.close()
except Exception as e:
    print("❌ Connection failed:", e)
EOF
```

**Expected Results:**
- ✅ Connection successful
- ✅ PostgreSQL version: 15+
- ✅ Response time: < 100ms

### 3.2 Schema Validation Tests

#### Test: Required Tables Exist

```sql
-- Check all required tables
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public'
ORDER BY table_name;

-- Expected tables:
-- - categories
-- - files
-- - events
-- - people
-- - projects
-- - scenarios
-- - agent_memory
-- - connections
-- - test_results (NEW - for testing)
```

#### Test: Table Structure

```sql
-- Check categories table
\d categories

-- Expected columns:
-- id (BIGSERIAL PRIMARY KEY)
-- name (TEXT)
-- color (TEXT)
-- emoji (TEXT)
-- description (TEXT)
-- created_at (TIMESTAMP)

-- Check files table
\d files

-- Expected columns:
-- id (BIGSERIAL PRIMARY KEY)
-- filename (TEXT)
-- file_hash (TEXT)
-- storage_path (TEXT)
-- file_type (TEXT)
-- ai_analysis (JSONB)
-- category_id (BIGINT)
-- people (JSONB)
-- projects (JSONB)
-- custom_fields (JSONB)
-- user_comment (TEXT)
-- uploaded_at (TIMESTAMP)
-- processed_by_agent (TEXT)
```

### 3.3 CRUD Operations Tests

#### Test: CREATE

```sql
-- Insert test category
INSERT INTO categories (name, color, emoji, description, created_at)
VALUES ('Test Category', '#FF0000', '🧪', 'Test entry', NOW())
RETURNING id, name, created_at;

-- Expected: ✅ Returns new record with ID
```

#### Test: READ

```sql
-- Read the test category
SELECT * FROM categories WHERE name = 'Test Category';

-- Expected: ✅ Returns the record just created
```

#### Test: UPDATE

```sql
-- Update test category
UPDATE categories 
SET color = '#00FF00', emoji = '✅'
WHERE name = 'Test Category'
RETURNING *;

-- Expected: ✅ Returns updated record
```

#### Test: DELETE

```sql
-- Delete test category
DELETE FROM categories WHERE name = 'Test Category'
RETURNING *;

-- Expected: ✅ Returns deleted record
```

### 3.4 Transaction Tests

```sql
-- Start transaction
BEGIN;

-- Multiple operations
INSERT INTO categories (name, color, emoji, created_at)
VALUES ('Trans Test 1', '#FF0000', '1️⃣', NOW());

INSERT INTO categories (name, color, emoji, created_at)
VALUES ('Trans Test 2', '#00FF00', '2️⃣', NOW());

-- Rollback to test
ROLLBACK;

-- Verify rolled back
SELECT COUNT(*) FROM categories WHERE name LIKE 'Trans Test%';
-- Expected: 0

-- Test commit
BEGIN;
INSERT INTO categories (name, color, emoji, created_at)
VALUES ('Trans Test Commit', '#0000FF', '✅', NOW());
COMMIT;

-- Verify committed
SELECT * FROM categories WHERE name = 'Trans Test Commit';
-- Expected: ✅ Record exists
```

### 3.5 Replication Tests

```sql
-- Check replication status
SELECT slot_name, slot_type, active, restart_lsn 
FROM pg_replication_slots;

-- Check WAL level
SHOW wal_level;
-- Expected: replica or logical

-- Check max_wal_senders
SHOW max_wal_senders;
-- Expected: >= 5
```

---

## 🤖 PART 4: SERVICE TESTS

### 4.1 N8N Workflow Tests

#### Test: Workflow #1 (Digital Twin Ask)

```bash
#!/bin/bash
echo "🤖 Testing Workflow #1: Digital Twin Ask..."

# Trigger webhook
curl -X POST \
  "https://lavrentev.app.n8n.cloud/webhook/[your-webhook-path]" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is machine learning?"
  }'

# Expected:
# - Webhook received
# - Question sent to Perplexity
# - Answer received
# - Saved to Supabase
# - Response time: < 10 seconds
```

#### Test: Workflow #2 (Daily Intelligence)

```bash
#!/bin/bash
echo "🤖 Testing Workflow #2: Daily Intelligence..."

# Check if workflow has executed today
curl -X GET \
  "https://lavrentev.app.n8n.cloud/api/v1/workflows" \
  -H "Authorization: Bearer YOUR_N8N_TOKEN"

# Check execution logs
curl -X GET \
  "https://lavrentev.app.n8n.cloud/api/v1/executions?workflow=[WORKFLOW_ID]" \
  -H "Authorization: Bearer YOUR_N8N_TOKEN"

# Expected:
# - Workflow executed at 12:00 MSK
# - Status: successful
# - Data in Supabase
# - Telegram message sent
```

#### Test: Workflow #3 (Hourly Reports)

```bash
#!/bin/bash
echo "🤖 Testing Workflow #3: Hourly Reports..."

# Check if hourly execution is working
curl -X GET \
  "https://lavrentev.app.n8n.cloud/api/v1/executions?workflow=[WORKFLOW_ID]" \
  -H "Authorization: Bearer YOUR_N8N_TOKEN" | jq '.data | length'

# Expected: >= 8 (at least 8 executions in last 8+ hours)
```

### 4.2 Perplexity API Tests

```bash
#!/bin/bash
echo "🔧 Testing Perplexity API..."

# Test API connectivity
curl -X POST \
  "https://api.perplexity.ai/chat/completions" \
  -H "Authorization: Bearer $PERPLEXITY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "sonar-reasoning-pro",
    "messages": [
      {
        "role": "user",
        "content": "What is 2+2?"
      }
    ]
  }'

# Expected:
# HTTP/1.1 200 OK
# {
#   "choices": [
#     {
#       "message": {
#         "content": "2+2 equals 4"
#       }
#     }
#   ]
# }
```

### 4.3 Telegram Bot Tests

```bash
#!/bin/bash
echo "🔧 Testing Telegram Bot..."

# Send test message
curl -X POST \
  "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": 123456789,
    "text": "🧪 Test message from testing suite"
  }'

# Expected:
# HTTP/1.1 200 OK
# Message received by user
```

---

## ✅ PART 5: INTEGRATION TESTS

### 5.1 End-to-End Flow Test

```
Scenario: Complete workflow from file upload to analysis result

1️⃣ USER UPLOADS FILE
   └─ Telegram Bot receives file
   
2️⃣ BOT SENDS TO ANALYZER
   └─ N8N Workflow #1 triggered
   
3️⃣ ANALYZER PROCESSES
   └─ Perplexity API analyzes
   
4️⃣ SAVE TO DATABASE
   └─ Supabase stores result
   
5️⃣ BOT RESPONDS
   └─ Telegram shows result
   
6️⃣ API AVAILABLE
   └─ GET /api/v1/analysis/{id} works

✅ Expected: Full flow < 30 seconds
```

### 5.2 Cross-Service Communication

```
Test 1: Telegram → N8N → Perplexity → Supabase → API

curl -X POST \
  "http://97v.ru/api/v1/analysis/test" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"question": "Test question"}'

Expected flow:
1. API received request ✅
2. N8N webhook triggered ✅
3. Perplexity API called ✅
4. Supabase stored result ✅
5. API returns 200 ✅
```

### 5.3 Error Handling Tests

```bash
#!/bin/bash
echo "🧪 Testing Error Handling..."

# Test 1: Invalid API token
echo "Test 1: Invalid token"
curl -X GET \
  "http://97v.ru/api/v1/analysis/test" \
  -H "Authorization: Bearer invalid_token"
# Expected: 401 Unauthorized

# Test 2: Missing required field
echo "Test 2: Missing field"
curl -X POST \
  "http://97v.ru/api/v1/batch-process" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"priority": "high"}'
# Expected: 400 Bad Request

# Test 3: Non-existent resource
echo "Test 3: Not found"
curl -X GET \
  "http://97v.ru/api/v1/analysis/nonexistent" \
  -H "Authorization: Bearer YOUR_TOKEN"
# Expected: 404 Not Found

# Test 4: Server error simulation
echo "Test 4: Database connection error"
# (Stop Supabase temporarily, then restart)
# Expected: 503 Service Unavailable
```

---

## 📈 PART 6: PERFORMANCE TESTS

### 6.1 Response Time Tests

```bash
#!/bin/bash
echo "📈 Performance Testing..."

# Test 1: Health endpoint (should be < 10ms)
time curl -s http://97v.ru/health > /dev/null

# Test 2: Analysis endpoint (should be < 1000ms)
time curl -s -X GET \
  "http://97v.ru/api/v1/analysis/test-id" \
  -H "Authorization: Bearer YOUR_TOKEN" > /dev/null

# Test 3: Metrics endpoint (should be < 500ms)
time curl -s -X GET \
  "http://97v.ru/api/v1/metrics" \
  -H "Authorization: Bearer YOUR_TOKEN" > /dev/null
```

### 6.2 Load Testing

```bash
#!/bin/bash
echo "📈 Load Testing with Apache Bench..."

# Light load: 100 requests, 10 concurrent
ab -n 100 -c 10 http://97v.ru/health

# Medium load: 1000 requests, 50 concurrent
ab -n 1000 -c 50 http://97v.ru/health

# Heavy load: 5000 requests, 100 concurrent
ab -n 5000 -c 100 http://97v.ru/health

# Expected:
# Requests per second: > 1000
# Failed requests: 0
# Average time: < 50ms
```

### 6.3 Database Query Performance

```sql
-- Check slow queries
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Expected: All queries < 100ms
```

---

## 🗂️ PART 7: TEST RESULTS TRACKING (Supabase)

### Create test_results table

```sql
CREATE TABLE IF NOT EXISTS test_results (
  id BIGSERIAL PRIMARY KEY,
  
  -- Test metadata
  test_name TEXT NOT NULL,
  test_category TEXT NOT NULL,
  test_type TEXT NOT NULL,
  
  -- Execution info
  started_at TIMESTAMP NOT NULL DEFAULT NOW(),
  completed_at TIMESTAMP,
  duration_seconds DECIMAL,
  
  -- Results
  status TEXT NOT NULL CHECK (status IN ('passed', 'failed', 'skipped')),
  error_message TEXT,
  
  -- Metrics
  response_time_ms DECIMAL,
  memory_used_mb DECIMAL,
  cpu_used_percent DECIMAL,
  
  -- Environment
  environment TEXT,
  kubernetes_version TEXT,
  supabase_version TEXT,
  api_version TEXT,
  
  -- Additional data
  test_data JSONB,
  assertions_passed INT,
  assertions_total INT,
  
  created_at TIMESTAMP DEFAULT NOW(),
  created_by TEXT
);

-- Create indexes for fast querying
CREATE INDEX idx_test_results_status ON test_results(status);
CREATE INDEX idx_test_results_category ON test_results(test_category);
CREATE INDEX idx_test_results_created_at ON test_results(created_at DESC);
```

### Insert test result

```sql
INSERT INTO test_results (
  test_name,
  test_category,
  test_type,
  started_at,
  completed_at,
  duration_seconds,
  status,
  response_time_ms,
  environment,
  kubernetes_version,
  api_version,
  test_data,
  assertions_passed,
  assertions_total,
  created_by
) VALUES (
  'Health Endpoint Test',
  'API',
  'Integration',
  NOW(),
  NOW() + INTERVAL '5 seconds',
  5,
  'passed',
  8.5,
  'production',
  '1.28',
  '1.0.0',
  '{"endpoint": "/health", "expected_status": 200}',
  3,
  3,
  'testing-suite'
)
RETURNING *;
```

### Query test results

```sql
-- Get latest test results
SELECT 
  test_name,
  test_category,
  status,
  response_time_ms,
  created_at
FROM test_results
ORDER BY created_at DESC
LIMIT 20;

-- Get test statistics
SELECT 
  test_category,
  COUNT(*) as total_tests,
  SUM(CASE WHEN status = 'passed' THEN 1 ELSE 0 END) as passed,
  SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
  ROUND(100.0 * SUM(CASE WHEN status = 'passed' THEN 1 ELSE 0 END) / COUNT(*), 2) as pass_rate
FROM test_results
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY test_category
ORDER BY test_category;

-- Get failed tests
SELECT 
  test_name,
  test_category,
  error_message,
  created_at
FROM test_results
WHERE status = 'failed'
  AND created_at > NOW() - INTERVAL '24 hours'
ORDER BY created_at DESC;
```

---

## 🚀 RUNNING TESTS

### Option 1: Manual Testing (Step by Step)

```bash
# 1. Infrastructure tests
./tests/01-infrastructure-tests.sh

# 2. API tests
./tests/02-api-tests.sh

# 3. Database tests
psql -f ./tests/03-database-tests.sql

# 4. Service tests
./tests/04-service-tests.sh

# 5. Integration tests
./tests/05-integration-tests.sh
```

### Option 2: Automated Testing (Full Suite)

```bash
#!/bin/bash
# Run all tests and store results in Supabase

python3 << 'EOF'
import subprocess
import json
from datetime import datetime
from supabase import create_client

# Initialize Supabase
supabase = create_client(
    "https://xxxxx.supabase.co",
    "your-api-key"
)

test_suites = [
    "infrastructure",
    "api",
    "database",
    "services",
    "integration"
]

for suite in test_suites:
    print(f"🧪 Running {suite} tests...")
    
    try:
        # Run test suite
        result = subprocess.run(
            ["bash", f"tests/{suite}-tests.sh"],
            capture_output=True,
            timeout=300
        )
        
        # Determine status
        status = "passed" if result.returncode == 0 else "failed"
        
        # Store in Supabase
        supabase.table("test_results").insert({
            "test_name": f"{suite.title()} Tests",
            "test_category": suite.upper(),
            "test_type": "Automated",
            "status": status,
            "error_message": result.stderr.decode() if result.returncode != 0 else None,
            "environment": "production",
            "created_by": "automated-testing-suite"
        }).execute()
        
        print(f"✅ {suite}: {status.upper()}")
        
    except subprocess.TimeoutExpired:
        print(f"❌ {suite}: TIMEOUT")
    except Exception as e:
        print(f"❌ {suite}: ERROR - {e}")

print("✅ All test suites completed!")
EOF
```

### Option 3: Continuous Integration (GitHub Actions)

```yaml
# .github/workflows/testing.yml
name: Test Suite

on:
  schedule:
    - cron: '0 */4 * * *'  # Run every 4 hours
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.test.txt
      
      - name: Run infrastructure tests
        run: ./tests/01-infrastructure-tests.sh
      
      - name: Run API tests
        run: ./tests/02-api-tests.sh
      
      - name: Run database tests
        run: psql -f ./tests/03-database-tests.sql
      
      - name: Store results in Supabase
        run: python3 tests/store_results.py
```

---

## 📊 TEST RESULTS DASHBOARD

### Real-time View

```sql
-- Current test status
SELECT 
  test_category,
  status,
  COUNT(*) as count,
  ROUND(AVG(response_time_ms), 2) as avg_response_time_ms
FROM test_results
WHERE created_at > NOW() - INTERVAL '1 hour'
GROUP BY test_category, status
ORDER BY test_category, status;
```

### Health Summary

```sql
-- System health score
SELECT 
  ROUND(
    100.0 * COUNT(CASE WHEN status = 'passed' THEN 1 END) / COUNT(*),
    2
  ) as system_health_percent,
  COUNT(*) as total_tests_24h,
  SUM(CASE WHEN status = 'passed' THEN 1 ELSE 0 END) as passed,
  SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed
FROM test_results
WHERE created_at > NOW() - INTERVAL '24 hours';
```

---

## ⚠️ KNOWN ISSUES & TROUBLESHOOTING

| Issue | Cause | Solution |
|:------|:-----:|:--------:|
| Kubernetes pod CrashLoopBackOff | Memory/CPU limit | Increase pod resources |
| API timeout (> 5000ms) | Database slow query | Check Supabase connections |
| WebSocket connection refused | SSL certificate | Check cert-manager |
| N8N workflow failed | API key expired | Refresh credentials |
| Supabase connection pool exhausted | Too many connections | Increase pool size |

---

## ✅ SIGN-OFF

- [ ] All infrastructure tests passed
- [ ] All API tests passed
- [ ] All database tests passed
- [ ] All service tests passed
- [ ] All integration tests passed
- [ ] Performance metrics acceptable
- [ ] No critical errors in logs
- [ ] Test results stored in Supabase
- [ ] System ready for production

---

**Testing Suite Version:** 1.0.0  
**Last Updated:** Dec 8, 2025, 07:59 AM MSK  
**Next Scheduled Run:** Dec 8, 2025, 12:00 MSK  
**Status:** 🟢 READY TO EXECUTE\n", "sha": ""}