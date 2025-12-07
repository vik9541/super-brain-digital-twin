# ✅ N8N WORKFLOWS - ACTIVATION GUIDE

**Status:** 🟢 READY FOR CONFIGURATION  
**Date:** Dec 8, 2025, 22:30 MSK  
**Time Estimate:** 45 minutes  

---

## 📋 OVERVIEW

Все необходимые credentials получены. Теперь надо настроить N8N для активации всех 3 workflows.

Шаги активации:

| Workflow | Status | Time | Action |
|:---|:---:|:---:|:---:|
| **WF#1: Ask Perplexity** | ✅ Ready | 10 min | Configure + Activate |
| **WF#2: Daily Analysis** | ✅ Ready | 15 min | Configure + Activate |
| **WF#3: Hourly Reports** | ✅ Ready | 15 min | Configure + Activate |
| **Testing** | ✅ Ready | 5 min | Verify all work |

**Total Time:** ~45 minutes

---

## 🔧 CONFIGURATION STEPS

### **STEP 1: PERPLEXITY API KEY (10 minutes)**

Выгдан ключ Perplexity API.

**Add to Workflow #1:**
```
1. Go to N8N dashboard: https://lavrentev.app.n8n.cloud
2. Open Workflow #1 (Ask Perplexity)
3. Find "HTTP Request" node labeled "Perplexity"
4. Click on it
5. Expand "Headers" section
6. Add new header:
   Key: Authorization
   Value: Bearer [YOUR_PERPLEXITY_KEY]
7. Click "Save"
8. Click "Execute" to test
9. Should see response in output node
```

**Add to Workflow #2:**
```
1. Open Workflow #2 (Daily Analysis)
2. Find "HTTP Request" node (Perplexity API analysis)
3. Add same Authorization header
4. Save
```

---

### **STEP 2: SUPABASE POSTGRES CREDENTIALS (15 minutes)**

Эти credentials дали вы.

**Create Postgres Connection in N8N:**

```
1. In N8N, click "Credentials" (left sidebar)
2. Click "+ Create New" or "+ Add Credentials"
3. Search for "Postgres"
4. Select "Postgres"
5. Fill in form:
   
   Hostname: db.lvixtpatqrtuwhygtpjx.supabase.co
   Database: postgres
   User: postgres
   Password: [Ask project owner for this]
   Port: 5432
   SSL: Allow
   
6. Click "Test Connection"
7. Should show: "Connection successful" with green checkmark
8. Click "Save"
9. Name it: "Supabase-PostgreSQL"
```

**Add to Workflow #2:**
```
1. Open Workflow #2
2. Find "Postgres: Execute SQL Query" node
3. In dropdown "Credentials", select "Supabase-PostgreSQL"
4. SQL query already configured
5. Click "Save"
6. Click "Execute" to test
7. Should see data in output
```

**Add Supabase REST API to Workflow #3:**
```
1. Open Workflow #3
2. Find "HTTP Request" node (Supabase REST)
3. Expand "Headers" section
4. Add new header:
   Key: apikey
   Value: [YOUR_SUPABASE_ANON_KEY]
5. Save
```

---

### **STEP 3: TELEGRAM BOT TOKEN (10 minutes)**

Ключ Telegram бота выбран.

**Create Telegram Credentials in N8N:**

```
1. In N8N, click "Credentials"
2. Click "+ Create New"
3. Search for "Telegram"
4. Select "Telegram"
5. Paste your Bot Token
6. Click "Test"
7. Should show green checkmark
8. Click "Save"
9. Name it: "Telegram-Bot"
```

**Add to Workflow #2:**
```
1. Open Workflow #2 (Daily Analysis)
2. Find "Telegram: Send Message" node
3. In "Credentials" dropdown, select "Telegram-Bot"
4. Scroll down to "Chat ID" field
5. Enter your Telegram Chat ID (numeric value)
   [Example: 123456789 - get this from @BotFather]
6. Save
```

**Add to Workflow #3:**
```
1. Open Workflow #3 (Hourly Reports)
2. Find "Telegram: Send Message" node
3. Select same "Telegram-Bot" credentials
4. Set same Chat ID
5. Save
```

---

### **STEP 4: EMAIL SMTP CREDENTIALS (10 minutes)**

Dly Workflow #3 only.

**Setup Gmail:**

```
1. Go to Gmail Security Settings: https://myaccount.google.com/security
2. Enable "2-Step Verification" if not already enabled
3. Go to App Passwords: https://myaccount.google.com/apppasswords
4. Select: Mail, Windows Computer
5. Copy the 16-character password

Create Email Credentials in N8N:

1. In N8N, click "Credentials"
2. Click "+ Create New"
3. Search for "Email"
4. Select "Email"
5. Fill in:
   SMTP Host: smtp.gmail.com
   SMTP Port: 587
   Email: your.gmail@gmail.com
   Password: [16-char App Password]
   From Email: your.gmail@gmail.com
   TLS: Yes (enabled)
6. Click "Test"
7. Should send test email
8. Check your inbox for test email
9. If received, click "Save"
10. Name it: "Gmail-SMTP"
```

**Add to Workflow #3:**
```
1. Open Workflow #3
2. Find "Send Email" node
3. In "Credentials" dropdown, select "Gmail-SMTP"
4. Set recipient email in "To" field
5. Save
```

---

### **STEP 5: CREATE REQUIRED DATABASE TABLES (Optional - if needed)**

```
1. Go to Supabase Dashboard
2. Click "SQL Editor"
3. Click "New Query"
4. Copy-paste this SQL:

CREATE TABLE IF NOT EXISTS daily_reports (
  id BIGSERIAL PRIMARY KEY,
  report_date DATE NOT NULL,
  total_messages INTEGER,
  unique_users INTEGER,
  analysis TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(report_date)
);

CREATE TABLE IF NOT EXISTS hourly_reports (
  id BIGSERIAL PRIMARY KEY,
  report_hour TIMESTAMP NOT NULL,
  total_messages INTEGER,
  unique_users INTEGER,
  report_data JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(report_hour)
);

5. Click "Run"
6. Should see: "Success. No rows returned."
```

---

## ✅ ACTIVATION CHECKLIST

### **Workflow #1: Ask Perplexity**
- [ ] Perplexity API Key added to HTTP Request node
- [ ] Execute test: Shows response in output
- [ ] Toggle "Active" button to ON (green)
- [ ] Webhook URL noted (for API calls)

### **Workflow #2: Daily Intelligence Analysis**
- [ ] Perplexity API Key configured
- [ ] Supabase Postgres credentials selected
- [ ] Telegram credentials selected
- [ ] Chat ID entered
- [ ] Execute test: All nodes show data
- [ ] Toggle "Active" button to ON (green)
- [ ] Verify schedule: 09:00 UTC / 12:00 MSK daily

### **Workflow #3: Hourly Report Generator**
- [ ] Supabase Anon Key added to HTTP Request
- [ ] Telegram credentials selected
- [ ] Chat ID entered
- [ ] Email credentials configured
- [ ] Execute test: Email sent successfully
- [ ] Toggle "Active" button to ON (green)
- [ ] Verify schedule: Every hour

---

## 🚀 FINAL ACTIVATION STEPS

**Once all credentials are configured:**

```
Workflow #1:
  N8N Dashboard → WF#1 → Toggle "Active" → ON ✅
  
 Workflow #2:
  N8N Dashboard → WF#2 → Toggle "Active" → ON ✅
  Schedule shows: "Every day, 09:00 UTC"
  
 Workflow #3:
  N8N Dashboard → WF#3 → Toggle "Active" → ON ✅
  Schedule shows: "Every hour"
```

---

## 🚛 TESTING

**Test Workflow #1 (Ask Perplexity):**
```bash
curl -X POST [WEBHOOK_URL] \
  -H "Content-Type: application/json" \
  -d '{"question": "What is AI?", "user_id": 123}'

Should return JSON with answer
```

**Test Workflow #2 (Daily Analysis):**
```
1. Open workflow
2. Click "Execute"
3. Watch as each node executes
4. Check Telegram for message
```

**Test Workflow #3 (Hourly Reports):**
```
1. Open workflow
2. Click "Execute"
3. Check:
   - Email received
   - Telegram message received
   - Data in Supabase (new row in hourly_reports)
```

---

## ⏰ TIMELINE TO COMPLETION

```
22:30 MSK - Credentials provided
22:35-22:45 (10 min) - Configure Perplexity
22:45-23:00 (15 min) - Configure Supabase
23:00-23:10 (10 min) - Configure Telegram
23:10-23:25 (15 min) - Configure Email
23:25-23:35 (10 min) - Test all workflows

✅ 23:35 MSK - ALL WORKFLOWS LIVE! 🚀
```

---

## 📞 QUICK REFERENCE

**N8N Credentials Types Needed:**
- Postgres (for Supabase)
- Telegram Bot
- Email (Gmail SMTP)

**Credential Storage:**
- All stored securely in N8N
- NOT in GitHub
- NOT in config files
- Encrypted by N8N

**Workflows Auto-Execute:**
- WF#2: Daily at 12:00 MSK
- WF#3: Every hour
- WF#1: On webhook call

---

## 📌 NOTES

- Credentials provided by project owner
- Use them ONLY in N8N secure storage
- Never commit to GitHub
- Never share publicly
- Rotate keys periodically

---

**Everything is ready!**

**All 3 workflows can be activated TODAY!** 🌟

**Phase 2 Complete: Today at 23:35 MSK** ⏰
