# 🚀 TASK-001 PHASE 2: N8N WORKFLOWS SETUP
## GitHub Issue-based Task Tracking

**Task ID:** TASK-001-PHASE-2  
**Status:** 🔵 READY TO START  
**Assignee:** @vik9541  
**Sprint:** Week 1 (Dec 8-9)  
**Deadline:** 9 Dec 2025, 17:00 MSK  
**Estimated Time:** 5 hours  
**Priority:** 🔴 **CRITICAL**

---

## 📋 OVERVIEW

**Objective:** Create 3 N8N workflows for Astra VIK bot automation

**Deliverables:**
- ✅ digital-twin-ask-perplexity (Webhook trigger)
- ✅ daily-intelligence-analysis (Cron trigger)
- ✅ hourly-report-generator (Cron trigger)
- ✅ All workflows ACTIVE in production
- ✅ Webhook URLs documented
- ✅ Test cases passed

---

## 🎯 SUB-TASKS

### **SUB-TASK 1: Setup Workflow #1 - Ask Perplexity**
**Time:** 2 hours | **Status:** ⏳ TODO

**Checklist:**
- [ ] Open N8N dashboard (https://n8n.io/account/lavrentev)
- [ ] Create new workflow: `digital-twin-ask-perplexity`
- [ ] Add NODE 1: Webhook (POST trigger)
  - [ ] Method: POST
  - [ ] Path: `/webhook/digital-twin-ask`
  - [ ] Save webhook URL
- [ ] Add NODE 2: Function (parse JSON)
  - [ ] Extract: question, user_id, timestamp
- [ ] Add NODE 3: HTTP Request (Perplexity API)
  - [ ] URL: `https://api.perplexity.ai/openai/v1/chat/completions`
  - [ ] Method: POST
  - [ ] Auth: Bearer token
  - [ ] Model: sonar
  - [ ] Max tokens: 2000
- [ ] Add NODE 4: Postgres (Supabase)
  - [ ] INSERT into `telegram_interactions`
  - [ ] Save: user_id, question, answer, source, created_at
- [ ] Add NODE 5: Respond to Webhook
  - [ ] Status: 200
  - [ ] Body: {success, answer, user_id, timestamp}
- [ ] Test workflow with sample data
- [ ] Fix any errors
- [ ] Activate workflow
- [ ] Document webhook URL

**Acceptance Criteria:**
```
✅ Workflow is ACTIVE (green toggle)
✅ Test execution successful
✅ Data saved to Supabase
✅ Webhook URL working
✅ Response time < 5 seconds
```

**Comments/Notes:**
- Perplexity API Key: [SET IN ENVIRONMENT]
- Supabase connection: [VERIFY CREDENTIALS]
- Webhook URL: [TO BE DOCUMENTED]

---

### **SUB-TASK 2: Setup Workflow #2 - Daily Analysis**
**Time:** 1.5 hours | **Status:** ⏳ TODO

**Checklist:**
- [ ] Create new workflow: `daily-intelligence-analysis`
- [ ] Add NODE 1: Cron trigger
  - [ ] Schedule: `0 9 * * *` (9 AM UTC)
- [ ] Add NODE 2: Postgres (Query yesterday data)
  - [ ] SELECT COUNT(*) FROM telegram_interactions
  - [ ] WHERE DATE(created_at) = YESTERDAY
- [ ] Add NODE 3: Function (aggregate stats)
  - [ ] Count queries
  - [ ] Average response time
  - [ ] Top topics
- [ ] Add NODE 4: HTTP Request (Perplexity analysis)
  - [ ] Analyze aggregated data
  - [ ] Generate insights
- [ ] Add NODE 5: Postgres (Save report)
  - [ ] INSERT into `analysis_reports`
- [ ] Add NODE 6: Telegram (notify user)
  - [ ] Send summary to admin
- [ ] Test with Cron simulation
- [ ] Activate workflow

**Acceptance Criteria:**
```
✅ Workflow is ACTIVE
✅ Schedule correct (9 AM UTC)
✅ Data aggregation working
✅ Report saved to database
✅ Telegram notification sent
```

---

### **SUB-TASK 3: Setup Workflow #3 - Hourly Reports**
**Time:** 1.5 hours | **Status:** ⏳ TODO

**Checklist:**
- [ ] Create new workflow: `hourly-report-generator`
- [ ] Add NODE 1: Cron trigger
  - [ ] Schedule: `0 * * * *` (every hour)
- [ ] Add NODE 2: Postgres (Get last 100 messages)
  - [ ] SELECT * FROM telegram_interactions
  - [ ] ORDER BY created_at DESC LIMIT 100
- [ ] Add NODE 3: Function (Generate report)
  - [ ] Format as JSON or CSV
  - [ ] Include metadata
- [ ] Add NODE 4: Upload to Supabase Storage
  - [ ] Bucket: `reports`
  - [ ] Path: `hourly/{date}/{hour}.json`
- [ ] Add NODE 5: Email (send to admin)
  - [ ] Include download link
- [ ] Add NODE 6: Telegram (notify)
  - [ ] Send notification
- [ ] Test workflow
- [ ] Activate workflow

**Acceptance Criteria:**
```
✅ Workflow is ACTIVE
✅ Schedule correct (every hour)
✅ Report file generated
✅ File uploaded to storage
✅ Email sent successfully
✅ Telegram notification received
```

---

### **SUB-TASK 4: Testing & Validation**
**Time:** 30 minutes | **Status:** ⏳ TODO

**Checklist:**
- [ ] All 3 workflows visible in N8N dashboard
- [ ] All 3 workflows are ACTIVE (green toggles)
- [ ] Test Workflow #1:
  - [ ] Send webhook request
  - [ ] Verify Perplexity response
  - [ ] Check Supabase insertion
- [ ] Test Workflow #2:
  - [ ] Trigger manually (test execution)
  - [ ] Verify analysis report
  - [ ] Check database entry
- [ ] Test Workflow #3:
  - [ ] Trigger manually
  - [ ] Verify file upload
  - [ ] Check email/Telegram
- [ ] Check N8N logs for errors
- [ ] Document all webhook URLs
- [ ] Create summary report

**Acceptance Criteria:**
```
✅ All workflows execute successfully
✅ No errors in N8N logs
✅ All integrations working
✅ Data flowing correctly
✅ Ready for Phase 3
```

---

## 📊 PROGRESS TRACKING

### **Timeline**

**Day 1: Dec 8 (Sunday)**
```
09:00-11:00 | SUB-TASK 1 | ⏳ TODO
11:00-12:30 | SUB-TASK 2 | ⏳ TODO
12:30-14:00 | LUNCH      | 🍽️
14:00-15:30 | SUB-TASK 3 | ⏳ TODO
15:30-16:30 | Testing    | ⏳ TODO
16:30-17:00 | Docs       | ⏳ TODO
```

**Day 2: Dec 9 (Monday)**
```
09:00-10:00 | Bug fixes  | ⏳ TODO
10:00-12:00 | Final test | ⏳ TODO
12:00-13:00 | Deploy     | ⏳ TODO
```

### **Status Updates** (to be filled daily)

**Dec 8, 09:00** - Task started
- [ ] Workflow #1 started

**Dec 8, 11:00** - Update
- [ ] Workflow #1 completed
- [ ] Workflow #2 started

**Dec 8, 12:30** - Lunch

**Dec 8, 14:00** - Workflow #2 done
- [ ] Workflow #2 completed
- [ ] Workflow #3 started

**Dec 8, 15:30** - Testing phase
- [ ] Workflow #3 completed
- [ ] All workflows testing

**Dec 8, 17:00** - EOD Report
- [ ] Day 1 summary
- [ ] Blockers identified

**Dec 9, 12:00** - Final deployment
- [ ] All workflows LIVE
- [ ] Production verified
- [ ] Task COMPLETE

---

## 🔗 DEPENDENCIES

**Must be completed BEFORE this task:**
- ✅ TASK-001-PHASE-1 (Bot created, TOKEN secured)
- ✅ K8s secret configured with TOKEN
- ✅ Perplexity API key available
- ✅ Supabase credentials configured

**Blocks the following tasks:**
- 🔵 TASK-001-PHASE-3 (Bot Development)
- 🔵 TASK-001-PHASE-4 (Testing)
- 🔵 TASK-001-PHASE-5 (Production Deploy)

---

## 📚 RESOURCES

### **Documentation**
- [N8N-Integration-Guide.md](../DOCUMENTATION/N8N-Integration-Guide.md) - Full guide
- [N8N-Quick-Reference.md](../DOCUMENTATION/N8N-Quick-Reference.md) - Quick start
- [DECISIONS/STRATEGIC-DECISION-DEC7.md](../DECISIONS/STRATEGIC-DECISION-DEC7.md) - Architecture
- [SUMMARY-DEC7-EXECUTION-PLAN.md](../SUMMARY-DEC7-EXECUTION-PLAN.md) - Full plan

### **External Links**
- N8N Dashboard: https://n8n.io/account/lavrentev
- N8N Docs: https://docs.n8n.io
- Perplexity API: https://docs.perplexity.ai
- Supabase: https://supabase.com/docs

---

## 🚨 RISKS & MITIGATIONS

| Risk | Probability | Impact | Mitigation |
|:---|:---:|:---:|:---:|
| Perplexity API rate limit | Medium | High | Implement queue, retry logic |
| Supabase connection timeout | Low | Medium | Use connection pooling |
| N8N webhook URL instability | Low | High | Document & test multiple times |
| Webhook auth issues | Medium | Medium | Use API key from start |
| Cron timing sync issues | Low | Low | Test with manual triggers first |

---

## 🎉 SUCCESS CRITERIA (Overall)

```
✅ 3 N8N workflows created
✅ All workflows ACTIVE in production
✅ Webhook URLs documented & working
✅ All integrations tested
✅ No errors in production logs
✅ Ready for Phase 3: Bot Development
✅ Estimated time: 5 hours (within budget)
```

---

## 📝 COMPLETION NOTES

**This task is complete when:**

1. All 3 workflows are ACTIVE in N8N dashboard
2. Each workflow has been tested successfully
3. All URLs and credentials are documented
4. GitHub issue is marked CLOSED
5. Team has verified in production
6. Next phase (PHASE-3) can begin

---

**Task Created:** 7 Dec 2025, 21:35 MSK  
**Assigned To:** @vik9541  
**Sprint:** Week 1 (8-14 Dec)  
**Labels:** `task`, `n8n`, `workflows`, `critical`, `phase-2`

**Related Issues:**
- TASK-001-PHASE-1 ✅ COMPLETE
- TASK-001-PHASE-2 (THIS)
- TASK-001-PHASE-3 (⏳ waiting)
- TASK-001-PHASE-4 (⏳ waiting)
- TASK-001-PHASE-5 (⏳ waiting)