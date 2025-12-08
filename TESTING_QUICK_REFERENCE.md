# 🧪 TESTING QUICK REFERENCE CARD

**Print this! Tape to monitor!**

---

## 🚀 ONE-LINER START

```bash
export SUPABASE_URL="https://hbdrmgtcvlwjcecptfxd.supabase.co" && \
export SUPABASE_KEY="your-key" && \
python3 run_tests.py --all
```

---

## 📈 5-SECOND STATUS CHECK

```bash
# API healthy?
curl http://97v.ru/health

# Kubernetes OK?
kubectl get pods

# Database connected?
psql -c "SELECT 1"

# Tests running?
SELECT COUNT(*) FROM test_results WHERE created_at > NOW() - INTERVAL '1 hour';
```

---

## 📊 4 FILES YOU NEED

| File | Purpose | Size |
|:-----|:--------|:-----|
| **TESTING.md** | Full test guide (40+ tests) | 26 KB |
| **SUPABASE_TESTING_SCHEMA.sql** | DB schema (5 tables) | 16 KB |
| **run_tests.py** | Auto test runner | 18 KB |
| **TEST_EXECUTION_GUIDE.md** | Step-by-step | 10 KB |

---

## 💾 SUPABASE TABLES AT A GLANCE

```sql
-- Test results (primary)
SELECT test_name, status, response_time_ms 
FROM test_results ORDER BY created_at DESC LIMIT 10;

-- Health check
SELECT * FROM v_health_dashboard;

-- Failed tests only
SELECT * FROM v_failed_tests LIMIT 5;

-- Performance trends (7 days)
SELECT * FROM v_performance_trends;
```

---

## 🔧 TEST CATEGORIES (Run Separately)

```bash
python3 run_tests.py --infrastructure  # Kubernetes, DNS, Network
python3 run_tests.py --api             # 97v.ru endpoints
python3 run_tests.py --database        # Supabase health
```

---

## 📁 EXPECTED OUTPUT

```
✅ Kubernetes Pod Status: passed (123.45ms)
✅ API Health Check: passed (8.32ms)
✅ DNS Resolution (97v.ru): passed (45.67ms)
✅ Database Connection: passed (89.01ms)
✅ GET /api/v1/metrics: passed (234.56ms)

======================================================================
📈 TEST EXECUTION SUMMARY
======================================================================
Total Tests: 5
✅ Passed: 5
❌ Failed: 0
Pass Rate: 100.0%
Avg Response Time: 100.20ms
======================================================================
```

---

## ❌ QUICK TROUBLESHOOTING

| Problem | Command |
|:--------|:--------|
| **API not responding** | `curl -v http://97v.ru/health` |
| **DNS broken** | `nslookup 97v.ru 8.8.8.8` |
| **Pods down** | `kubectl get pods -A` |
| **DB disconnected** | `psql -c "SELECT 1"` |
| **Supabase key wrong** | Check `.env` or `$SUPABASE_KEY` |
| **Tests not logging** | Check RLS in Supabase |

---

## 📈 TODAY'S CHECKLIST

- [ ] Set SUPABASE_URL env var
- [ ] Set SUPABASE_KEY env var
- [ ] Set API_URL = http://97v.ru
- [ ] Run: `pip install requests supabase`
- [ ] Create schema: `psql -f SUPABASE_TESTING_SCHEMA.sql`
- [ ] Execute: `python3 run_tests.py --all`
- [ ] View results in Supabase console
- [ ] Check health: `SELECT * FROM v_health_dashboard;`

---

## 🌟 BEST TIMES TO TEST

- **Daily:** 6 AM MSK (automated)
- **Before deployment:** Manual run
- **After changes:** Within 5 minutes
- **Performance check:** Every 4 hours (automated)

---

## 📄 READING TEST RESULTS

```
status = 'passed'        ✅ Everything good
status = 'failed'        ❌ Something broken
status = 'error'         ⚠️ Connection/setup issue
status = 'skipped'       ⏳ Not needed this run

response_time_ms < 100   🚀 Very fast
response_time_ms < 500   ✅ Acceptable
response_time_ms > 1000  🛑 Slow alert!
```

---

## 🗒️ ENV VARIABLES

```bash
# Set these before running:
export SUPABASE_URL="https://hbdrmgtcvlwjcecptfxd.supabase.co"
export SUPABASE_KEY="your-supabase-api-key"
export API_URL="http://97v.ru"
export API_TOKEN="optional-bearer-token"

# Verify:
echo $SUPABASE_URL
echo $SUPABASE_KEY
```

---

## 📚 SQL QUERIES (Copy-Paste Ready)

```sql
-- Last 20 test results
SELECT test_name, status, response_time_ms, created_at 
FROM test_results ORDER BY created_at DESC LIMIT 20;

-- Today's pass rate
SELECT 
  ROUND(100.0 * COUNT(CASE WHEN status='passed' THEN 1 END) / COUNT(*), 2) as pass_rate
FROM test_results WHERE DATE(created_at) = CURRENT_DATE;

-- Failed tests in last 24h
SELECT test_name, error_message, created_at 
FROM test_results 
WHERE status='failed' AND created_at > NOW() - INTERVAL '24 hours';

-- Performance by category
SELECT test_category, AVG(response_time_ms) as avg_ms, MAX(response_time_ms) as max_ms
FROM test_results 
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY test_category;
```

---

## 🔗 DIRECT LINKS

- **Supabase Console:** https://app.supabase.com/project/[id]/editor/test_results
- **API Health:** http://97v.ru/health
- **GitHub Issue #5:** https://github.com/vik9541/super-brain-digital-twin/issues/5
- **This Repo:** https://github.com/vik9541/super-brain-digital-twin

---

## 🌟 PERFORMANCE TARGETS

```
✅ API Response:      < 500ms
✅ DNS Resolution:   < 100ms  
✅ Database Query:   < 50ms
✅ Pass Rate:        > 95%
✅ Infrastructure:   100% healthy
✅ Uptime:           99.9%
```

---

## 📈 WHAT TO DO IF TESTS FAIL

### Immediate Actions
1. Check error message in Supabase
2. Run manual verification: `curl http://97v.ru/health`
3. Check pod status: `kubectl get pods`
4. Check logs: `kubectl logs deployment/api`

### Common Fixes
```bash
# Restart API pod
kubectl rollout restart deployment/api

# Check connectivity
ping 97v.ru
nslookup 97v.ru

# Verify database
psql -c "SELECT 1 FROM test_results LIMIT 1;"

# Clear cache
sudo systemctl restart systemd-resolved  # Linux
dscacheutil -flushcache                  # macOS
```

### Escalation
- If > 3 consecutive failures → Check GitHub Issue #5
- If infrastructure issue → Check Kubernetes events
- If database issue → Check Supabase status
- If API issue → Check deployment logs

---

## 📝 LOGGING TEMPLATE

```bash
# When you run tests, log it:
echo "Test run started: $(date)" >> test_log.txt
python3 run_tests.py --all
echo "Test run ended: $(date)" >> test_log.txt

# Query how it went:
SELECT COUNT(*), status FROM test_results 
WHERE created_at > NOW() - INTERVAL '1 hour'
GROUP BY status;
```

---

## 📁 CREATED FOR YOU TODAY

| File | What It Does | Key Section |
|:-----|:-------------|:-------------|
| **TESTING.md** | 26 KB complete guide | 40+ test cases, troubleshooting |
| **SUPABASE_TESTING_SCHEMA.sql** | DB setup | 5 tables, 4 views, 3 functions |
| **run_tests.py** | Auto runner | Just execute: `python3 run_tests.py --all` |
| **TEST_EXECUTION_GUIDE.md** | Step-by-step | 5-min quick start |
| **TEST_SUMMARY.md** | Overview | Coverage, timeline, results |
| **TESTING_QUICK_REFERENCE.md** | THIS FILE | You are here! 😀 |

---

## 🎆 YOU'RE ALL SET!

### Next 5 minutes:
1. Set env variables ✅
2. Install pip packages ✅
3. Create schema in Supabase ✅
4. Run: `python3 run_tests.py --all` ✅
5. View results ✅

### Questions?
Check [TESTING.md](TESTING.md) or [TEST_EXECUTION_GUIDE.md](TEST_EXECUTION_GUIDE.md)

---

**Status:** 🟢 READY NOW  
**Time to first test:** 5 minutes  
**Complete suite runtime:** 45 minutes  
**Files:** 6 (70 KB total)  
**Test cases:** 25+  

🚀 **You're ready to test everything!**
