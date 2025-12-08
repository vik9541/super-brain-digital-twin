# 📋 OPERATIONAL PROCEDURES & INCIDENT RESPONSE PLAYBOOKS

**Date:** Dec 8, 2025, 08:32 AM MSK  
**Version:** 1.0.0  
**Purpose:** Standardized procedures to eliminate manual reminders  
**Maintenance:** Update as procedures evolve  

---

## 🗣️ WHY THIS EXISTS

**Problem:** Manual reminders get forgotten
**Solution:** Automated GitHub Issues with checklists
**Result:** Never need to ask twice ✅

---

## 💡 PRINCIPLE: Automate Everything

When you need to:
1. **Remember something** → Create GitHub Issue
2. **Track progress** → Use Issue checklist
3. **Report results** → Add comment to Issue
4. **Close task** → Mark Issue as completed

---

## 📋 STANDARD ISSUE TEMPLATE FOR TASKS

### When Creating Any Repeating Task:

```markdown
# TASK-XXX: [Task Name]

**Status:** 🟡 IN PROGRESS
**Timeline:** [duration]
**Checklist:** [sub-tasks]

## 📈 Reporting
- [ ] Step 1 completed
- [ ] Step 2 completed
- [ ] Results logged
```

**Examples:**
- TASK-001: Phase 2 Workflows (completed)
- TASK-002: DNS Propagation Monitoring (current)
- TASK-003: Full Test Suite Execution
- TASK-004: Results Verification

---

## 🌟 INCIDENT RESPONSE PLAYBOOK

### When You Discover an Issue:

**STEP 1: Create Incident Report Issue** (5 min)
```bash
# GitHub Issue with:
# - Title: INC-YYYY-MM-DD-XXX: [Problem]
# - Severity: 🔴 CRITICAL / 🟡 HIGH / 🟢 LOW
# - Root cause analysis
# - Immediate actions
```

**STEP 2: Create Task Issue for Each Action** (2 min)
```bash
# GitHub Issue with:
# - Title: TASK-XXX: [Specific action]
# - Parent: Link to incident
# - Checklist: Detailed steps
# - Assign to: @yourself
```

**STEP 3: Execute Task** (time varies)
```bash
# Follow checklist
# Report results in Issue comment
# Update checklist items as completed
```

**STEP 4: Verify Completion** (5 min)
```bash
# Confirm all checklist items done
# Check results in Supabase/logs
# Close issue when complete
```

---

## 🚨 INCIDENT INC-2025-12-08-001: Full Workflow Example

### What Happened:
1. **08:00** - Testing started
2. **08:10** - API health check failed (Empty reply)
3. **08:15** - Root cause identified (DNS mismatch)
4. **08:30** - INCIDENT_REPORT_DEC8_2025.md created
5. **08:32** - TASK-002 created with detailed checklist

### Why This Way Works:

✅ **No manual reminders needed**
```
Instead of: "Remember to check DNS in 5 minutes"
We use: GitHub Issue TASK-002 with automatic checklist
```

✅ **Progress is tracked**
```
Instead of: "Did you test API yet?"
We use: Issue checklist showing: [x] API tested
```

✅ **Results are documented**
```
Instead of: "What were the results?"
We use: Issue comment with detailed results
```
✅ **Timeline is recorded**
```
Instead of: "When did we fix it?"
We use: GitHub Issue timestamps
```

---

## 📋 REPEATING TASKS SCHEDULE

### Daily Tests (Auto via CronJob)
```bash
# 6 AM MSK: Automated health check
# Runs: kubectl, DNS, API health, Database
# Reports to: Supabase test_results table
# Alert if: Any failures
```

### Weekly Reviews (Manual via Issue)
```bash
# Every Monday: TASK-XXX: Weekly Test Report
# Check: Performance trends, failed tests, SLA compliance
# Create: Weekly summary comment
```

### On Any API Changes
```bash
# Create: TASK-XXX: Post-Deployment Testing
# Tasks:
#   - Run full test suite
#   - Verify DNS
#   - Check logs
#   - Update documentation
```

---

## 📋 ISSUE LABELS FOR ORGANIZATION

### Status Labels
```
🟡 in-progress    - Currently being worked on
⏳ pending        - Waiting for something
✅ completed      - Done
🔴 critical      - Urgent, needs immediate action
```

### Category Labels
```
🚀 infrastructure - Kubernetes, DNS, networking
🌐 api           - API endpoints, health checks
💾 database      - Supabase, SQL, storage
🧪 testing      - Test suite, automation
📊 monitoring   - Metrics, alerting, logs
```

---

## 📈 GITHUB ISSUE NAMING CONVENTION

### For Incidents:
```
INC-YYYY-MM-DD-XXX: [Short description]
Example: INC-2025-12-08-001: API Accessibility Issue
```

### For Tasks:
```
TASK-XXX: [Action to complete]
Example: TASK-002: Monitor DNS Propagation & Verify API Connectivity
```

### For Features:
```
FEAT-XXX: [Feature name]
Example: FEAT-003: Add WebSocket real-time updates
```

### For Bug Reports:
```
BUG-XXX: [Problem description]
Example: BUG-001: API returns 502 on high load
```

---

## 🗣️ COMMUNICATION PROTOCOL

### When Something Needs Attention:

**DON'T:** Slack, email, or ask in person  
**DO:** Create GitHub Issue

```
❌ Bad: "Hey, remember to test the API later"
✅ Good: Create Issue TASK-002 with checklist

❌ Bad: "Did you fix the DNS issue?"
✅ Good: Check Issue #5 and TASK-002 status

❌ Bad: "What's the test result?"
✅ Good: Check Issue #7 comments and Supabase results
```

### Why This Works:
- ✅ Everything is documented
- ✅ Nothing gets lost
- ✅ Progress is visible
- ✅ Results are traceable
- ✅ No manual reminders needed

---

## 📋 TASK EXECUTION TEMPLATE

**Always use this structure when executing tasks:**

```markdown
# TASK-XXX: [Task Name]

## 📈 Execution Plan
1. [ ] Step 1 - Description
2. [ ] Step 2 - Description
3. [ ] Step 3 - Description

## 📚 Reporting Template
- Started at: [time]
- Completed at: [time]
- Duration: [time]
- Status: PASSED / FAILED / PARTIAL
- Results: [details]
- Issues encountered: [if any]
- Next action: [if needed]

## 📌 Evidence
- Logs: [link or summary]
- Supabase records: [link or summary]
- Screenshots: [if applicable]
```

---

## 🛁 CURRENT TASK: TASK-002

**Issue:** #7  
**Title:** Monitor DNS Propagation & Verify API Connectivity  
**Status:** 🟡 IN PROGRESS  
**Timeline:** ~60 minutes  

### What This Means:
1. No need to remind about checking DNS
2. GitHub Issue has auto-checklist
3. Update checklist as you complete steps
4. Post results in issue comment
5. Close issue when done

**That's it!** No manual tracking needed ✅

---

## 💡 AUTOMATION RULES (Never ask again)

### Rule 1: Testing Reminders
```
Before: "Remember to test API in 5 minutes"
After: GitHub Issue TASK-XXX with auto-checklist

Benefit: 🔴 No reminders needed
```

### Rule 2: Progress Tracking
```
Before: "What's the status?"
After: Check GitHub Issue checklist

Benefit: 🔴 Status always visible
```

### Rule 3: Result Reporting
```
Before: "What were the results?"
After: Check Issue comment with detailed report

Benefit: 🔴 Results permanently documented
```

### Rule 4: Timeline Recording
```
Before: "When did we fix it?"
After: Check GitHub Issue timestamps

Benefit: 🔴 Timeline automatically recorded
```

---

## 📌 SUPABASE TEST RESULTS TRACKING

### Automatic Storage
All test results automatically stored in:
```sql
Table: test_results
View: v_health_dashboard
View: v_failed_tests
View: v_performance_trends
```

### Query Results
```bash
# Instead of: "What were the test results?"
# Query:
SELECT * FROM test_results 
WHERE created_at > NOW() - INTERVAL '1 hour'
ORDER BY created_at DESC;
```

---

## 📚 REFERENCE: Related Documents

| Document | Purpose |
|:---------|:--------|
| **INCIDENT_REPORT_DEC8_2025.md** | Root cause analysis |
| **FIX_API_ACCESSIBILITY.md** | Step-by-step solutions |
| **TESTING.md** | Complete test procedures |
| **TESTING_WITH_DIGITALOCEAN_CONSOLE.md** | How to use console |
| **OPERATIONAL_PROCEDURES.md** | THIS FILE - Never ask again |

---

## 📊 SUCCESS METRICS

```
✅ If you ever ask: "Remember to..."
   ➡️ Create GitHub Issue instead

✅ If you ever ask: "What's the status?"
   ➡️ Check GitHub Issue checklist

✅ If you ever ask: "What were the results?"
   ➡️ Check Issue comment or Supabase

✅ If you ever ask: "When was this fixed?"
   ➡️ Check GitHub Issue timestamp
```

**Goal: Never manually remind again** 🌟

---

## 📝 QUICK REFERENCE CHECKLIST

When executing any task:

```
✅ Create GitHub Issue with:
   - Clear title (TASK-XXX or INC-XXX)
   - Status label (🟡 in-progress)
   - Category labels (🚀 infrastructure, etc)
   - Detailed sub-tasks with checkboxes
   - Assign to yourself

✅ Execute by:
   - Following checklist steps
   - Checking off items as completed
   - Recording times and results

✅ Report by:
   - Adding comment with results
   - Noting any issues or blockers
   - Including evidence (logs, screenshots)

✅ Close by:
   - Verifying all checklist items done
   - Confirming results are acceptable
   - Changing status to ✅ completed
   - Closing the issue
```

---

## 🌟 FINAL RULE

**If you need to remind someone about something more than once:**

➡️ **Automate it with a GitHub Issue**

Then you'll never need to remind again. 🚀

---

**Status:** 🟢 **ACTIVE PROCEDURE**  
**Last Updated:** Dec 8, 2025, 08:32 AM MSK  
**Revision:** 1.0  

**Remember:** Follow this procedure and you'll never need manual reminders again! 👍
