# 🔧 N8N CLOUD INTEGRATION GUIDE
## Super Brain Digital Twin - Automation Hub

**Дата:** 7 декабря 2025, 20:50 MSK  
**Аккаунт:** lavrentev (DigitalOcean)  
**Тариф:** Pro  
**Статус:** 🟢 READY FOR INTEGRATION

---

## 📋 N8N ACCOUNT DETAILS

### Account Information
```
Account: lavrentev
Plan: Pro
Price: 60 €/month
Billing: Monthly
Status: Active ✅
```

### Pro Plan Specifications
| Feature | Limit |
|:---|:---:|
| **Workflow Executions** | 10,000/month |
| **Workflow Steps** | Unlimited |
| **Concurrent Executions** | 20 |
| **Shared Projects** | 3 |
| **AI Credits** | 150/month |
| **Workflow History** | 5 days |
| **Insights Duration** | 7 days |
| **Roles** | Admin |
| **Global Variables** | ✅ Yes |
| **Execution Search** | ✅ Yes |

---

## 🎯 USE CASES FOR SUPER BRAIN

### **USE CASE 1: Question Answering Pipeline** ⭐ PRIORITY 1

**Workflow Name:** `digital-twin-ask-perplexity`

**Flow:**
```
Trigger: Telegram Bot /ask command
    ↓
Node 1: Parse question from Telegram
    Input: user_id, question, timestamp
    ↓
Node 2: Call Perplexity API
    Model: sonar
    Max tokens: 2000
    Temperature: 0.7
    ↓
Node 3: Enrich response
    Add metadata (source, timestamp)
    ↓
Node 4: Save to Supabase
    Table: telegram_interactions
    Fields: user_id, question, answer, created_at
    ↓
Node 5: Return to Telegram Bot
    Format: markdown
    Split if > 4096 chars
```

**Execution Cost:**
- Per execution: ~0.1 executions (cheap!)
- Monthly budget: 10,000 executions
- Expected usage: 500 questions/month = 5% of quota ✅

---

### **USE CASE 2: Daily Batch Analysis** ⭐ PRIORITY 2

**Workflow Name:** `daily-intelligence-analysis`

**Schedule:** Every day at 09:00 UTC

**Flow:**
```
Trigger: Cron (0 9 * * *)
    ↓
Node 1: Fetch yesterday's data
    Table: telegram_interactions
    Filter: created_at > yesterday
    ↓
Node 2: Aggregate statistics
    Count messages
    Extract topics
    Calculate sentiment
    ↓
Node 3: Send to Perplexity for insights
    Prompt: "Analyze this data and provide 3 key insights"
    ↓
Node 4: Generate report
    Format: Markdown or PDF
    ↓
Node 5: Save to Supabase
    Table: analysis_reports
    ↓
Node 6: Send Telegram alert
    To: @digital_twin_bot
    Message: "Daily report ready: [summary]"
```

---

### **USE CASE 3: Report Generation** ⭐ PRIORITY 3

**Workflow Name:** `hourly-report-generator`

**Schedule:** Every hour (on the hour)

**Flow:**
```
Trigger: Cron (0 * * * *)
    ↓
Node 1: Get last 100 messages
    From: telegram_interactions
    Order: DESC by created_at
    ↓
Node 2: Summarize with AI
    Use: Perplexity + AI credits
    ↓
Node 3: Generate Excel
    Columns: timestamp, user, question, summary
    ↓
Node 4: Upload to S3 or Supabase
    Filename: report_{{ $now.toISOString() }}
    ↓
Node 5: Email report
    To: vik9541@bk.ru
    Attachment: Excel file
    ↓
Node 6: Log to Supabase
    Table: generated_reports
```

---

## 📊 EXECUTION BUDGET

### Monthly Quota: 10,000 executions

| Use Case | Frequency | Monthly | % of Quota |
|:---|:---:|:---:|:---:|
| **Ask/Perplexity** | ~500 calls | 500 | 5% |
| **Daily Analysis** | 1/day | 30 | 0.3% |
| **Hourly Reports** | 24/day | 720 | 7.2% |
| **Error Handler** | As needed | ~100 | 1% |
| **Testing/Dev** | Variable | 500 | 5% |
| **Buffer** | Reserved | 7,150 | 71.5% |
| **TOTAL** | | **9,000** | **90%** |

**Status:** ✅ Comfortable margin (10% buffer)

---

## 🔐 SECURITY SETUP

### Environment Variables in N8N

```yaml
Credentials:
  PERPLEXITY_API_KEY: "ppl-xxx..."
  SUPABASE_URL: "https://xxx.supabase.co"
  SUPABASE_KEY: "eyJxxx..."
  TELEGRAM_BOT_TOKEN: "123456:ABC..."
  TELEGRAM_CHAT_ID: "xxxxxxx"
  SMTP_PASSWORD: "app-specific-pwd"
```

### Webhook Authentication

```python
# In N8N webhook
Authorization: "Bearer {{ $env.WEBHOOK_SECRET }}"
# Secret stored in N8N credentials, not in code
```

---

## 📝 IMPLEMENTATION ROADMAP

### WEEK 1 (8-14 Dec)
- [ ] Create N8N account connection
- [ ] Set up Perplexity API node
- [ ] Set up Supabase PostgreSQL node
- [ ] Build "ask-perplexity" workflow
- [ ] Test locally with polling

### WEEK 2 (15-21 Dec)
- [ ] Deploy "ask-perplexity" to production
- [ ] Set Telegram webhook
- [ ] Monitor execution logs
- [ ] Build "daily-analysis" workflow
- [ ] Set up error handling

### WEEK 3 (22-28 Dec)
- [ ] Build "hourly-reports" workflow
- [ ] Set up email notifications
- [ ] Performance optimization
- [ ] Load testing
- [ ] Documentation

### WEEK 4 (29-31 Dec)
- [ ] Production hardening
- [ ] Security audit
- [ ] Final testing
- [ ] v1.0.0 release ready

---

## 🎯 SUCCESS CRITERIA

✅ **Ask Workflow**
- Response time < 5 seconds
- Success rate > 99%
- Proper error handling

✅ **Analysis Workflow**
- Runs every day at 09:00 UTC
- Completes within 2 minutes
- Report saved to Supabase

✅ **Report Workflow**
- Runs every hour
- PDF/Excel generated
- Email sent successfully

---

## 📞 USEFUL LINKS

- **N8N Docs:** https://docs.n8n.io
- **Perplexity API:** https://docs.perplexity.ai
- **Supabase Docs:** https://supabase.com/docs
- **Telegram Bot API:** https://core.telegram.org/bots/api
- **Your N8N Instance:** https://n8n.io/account/lavrentev

---

**Document created:** 7 Dec 2025, 20:50 MSK  
**Status:** ✅ READY FOR IMPLEMENTATION  
**Priority:** ⭐⭐⭐ HIGH