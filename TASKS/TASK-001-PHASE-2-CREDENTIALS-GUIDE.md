# 🔐 CREDENTIALS SETUP GUIDE FOR N8N WORKFLOWS

**Status:** 🔴 BLOCKING - SUB-TASK 4  
**Created:** Dec 8, 2025, 16:00 MSK  
**Priority:** CRITICAL  

---

## 📋 OVERVIEW

This guide provides step-by-step instructions to obtain ALL required credentials for activating 3 N8N workflows:

1. ✅ **Workflow #1:** Digital Twin Ask (Perplexity)
2. ✅ **Workflow #2:** Daily Intelligence Analysis (Perplexity + Supabase + Telegram)
3. ✅ **Workflow #3:** Hourly Report Generator (Supabase + Email + Telegram)

---

## 🎯 CREDENTIALS REQUIRED (PRIORITY ORDER)

| # | Credential | Used In | Difficulty | Time |
|:---|:---|:---|:---:|:---:|
| **1** | Perplexity API Key | WF#1, WF#2 | ⭐ Easy | 5 min |
| **2** | Supabase Postgres | WF#2, WF#3 | ⭐⭐ Medium | 10 min |
| **3** | Telegram Bot Token | WF#2, WF#3 | ⭐ Easy | 5 min |
| **4** | Telegram Chat ID | WF#2, WF#3 | ⭐ Easy | 3 min |
| **5** | Email SMTP | WF#3 | ⭐⭐ Medium | 10 min |
| **6** | SQL Queries | WF#2, WF#3 | ⭐⭐ Medium | 15 min |

**Total Time:** ~45 minutes

---

## 1️⃣ PERPLEXITY API KEY

### **Where to Get It:**

1. Go to: https://www.perplexity.ai/settings/api
2. Log in with your account
3. Click "Create New API Key"
4. Copy the key (format: `pplx-xxxxxxxxxxxxx`)
5. Keep it safe! Don't share!

### **How to Add to N8N:**

**For Workflow #1 (Ask Perplexity):**
```
1. Open workflow in N8N
2. Click "HTTP Request" node (Perplexity)
3. Go to "Headers" section
4. Set: Authorization = Bearer pplx-YOUR-API-KEY
5. Replace pplx-YOUR-API-KEY with your actual key
```

**For Workflow #2 (Daily Analysis):**
```
1. Open workflow in N8N
2. Find "HTTP Request" node (Perplexity API)
3. Same as above - add Authorization header
```

### ✅ How to Verify:
```bash
curl -X POST https://api.perplexity.ai/chat/completions \
  -H "Authorization: Bearer pplx-YOUR-API-KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-3.1-sonar-small-128k-online",
    "messages": [{"role": "user", "content": "Hello"}]
  }'

# Should return JSON with response, NOT error
```

---

## 2️⃣ SUPABASE POSTGRES CREDENTIALS

### **Where to Get It:**

1. Go to: https://supabase.com/dashboard
2. Select your project (super-brain-digital-twin)
3. Go to: **Settings → Database → Connection Info**
4. You'll see:
   - Host: `db.xxxxx.supabase.co`
   - Database: `postgres`
   - User: `postgres`
   - Password: (shown in Settings)
   - Port: `5432`

### **How to Add to N8N:**

**Step 1: Create New Postgres Connection**
```
1. In N8N, click "Credentials"
2. Click "+ Add Credentials"
3. Select "Postgres"
4. Fill in:
   - Hostname: db.xxxxx.supabase.co
   - Database: postgres
   - User: postgres
   - Password: [from Supabase Settings]
   - Port: 5432
   - SSL: "Allow"
5. Click "Test Connection"
6. If green ✅ - save and you're done!
```

**Step 2: Use in Workflows**
```
1. For Workflow #2:
   - Node "Postgres: Execute SQL Query"
   - Select the connection you just created
   - Keep SQL query as is

2. For Workflow #3:
   - Node "HTTP Request (Supabase)"
   - Add Header: apikey = [your-anon-key]
```

### **Where to Get Anon Key (for Workflow #3):**
```
1. Go to Supabase Dashboard
2. Settings → API → Project API Keys
3. Copy "anon" key (public, safe to use)
4. Add to HTTP Request headers in Workflow #3
```

### ✅ How to Verify:
```bash
psql -h db.xxxxx.supabase.co -U postgres -d postgres -c "SELECT NOW();"

# Should return current timestamp, NOT error
```

---

## 3️⃣ TELEGRAM BOT TOKEN

### **Where to Get It:**

1. Open Telegram
2. Find: **@BotFather** (official Telegram bot for creating bots)
3. Send: `/start`
4. Send: `/newbot`
5. Answer questions:
   - Name: "Digital Twin Bot"
   - Username: "digitaltwin_lavrentev_bot" (must be unique)
6. You'll get a TOKEN: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`
7. **SAVE THIS!** You can always get it back from @BotFather with `/mybots`

### **How to Add to N8N:**

**For Workflow #2 (Daily Analysis):**
```
1. Open workflow
2. Find "Telegram: Send Message" node
3. Click "Credentials" dropdown
4. Click "+ Add Credentials"
5. Select "Telegram"
6. Paste Bot Token from @BotFather
7. Click "Test Connection"
8. If green ✅ - save!
```

**For Workflow #3 (Hourly Reports):**
```
Same process - select same Telegram credentials
```

### ✅ How to Verify:
```bash
curl -X POST https://api.telegram.org/bot123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11/getMe

# Should return JSON with bot info, NOT error
```

---

## 4️⃣ TELEGRAM CHAT ID

### **Where to Get It:**

**Option A: Manual (Easiest)**
```
1. Open your bot: https://t.me/digitaltwin_lavrentev_bot
2. Send: /start
3. Go to: https://api.telegram.org/bot123456:ABC.../getUpdates
   (Replace with your actual bot token)
4. Look for "chat": {"id": 123456789}
5. Copy that number (your Chat ID)
```

**Option B: Using Python**
```python
import requests

token = "YOUR_BOT_TOKEN"
url = f"https://api.telegram.org/bot{token}/getUpdates"
response = requests.get(url).json()

for update in response['result']:
    chat_id = update['message']['chat']['id']
    print(f"Your Chat ID: {chat_id}")
```

### **How to Add to N8N:**

**For Workflow #2 (Daily Analysis):**
```
1. Open workflow
2. Find "Telegram: Send Message" node
3. Set "Chat ID" field to: 123456789 (your actual ID)
4. Test the workflow
```

**For Workflow #3 (Hourly Reports):**
```
Same field - use same Chat ID
```

### ✅ How to Verify:
```bash
curl -X POST https://api.telegram.org/bot123456:ABC.../sendMessage \
  -d "chat_id=123456789&text=Test%20message"

# Should receive message in Telegram, NOT error
```

---

## 5️⃣ EMAIL SMTP CREDENTIALS (For Workflow #3)

### **Option A: Gmail (Recommended)**

**Step 1: Enable 2FA**
```
1. Go to: https://myaccount.google.com/security
2. Enable "2-Step Verification"
```

**Step 2: Create App Password**
```
1. Go to: https://myaccount.google.com/apppasswords
2. Select: Mail → Windows Computer
3. Google will generate 16-character password
4. Copy it (format: xxxx xxxx xxxx xxxx)
```

**Step 3: Add to N8N**
```
SMTP Settings:
  Host: smtp.gmail.com
  Port: 587
  Username: your.email@gmail.com
  Password: [16-char password from Step 2]
  From: your.email@gmail.com
```

### **Option B: Custom Email Provider**

Find SMTP settings from your provider:
- Gmail: smtp.gmail.com:587
- Outlook: smtp.office365.com:587
- Yandex: smtp.yandex.com:465
- Check your provider's documentation

### **How to Add to N8N:**

```
1. Open Workflow #3
2. Find "Send Email" node
3. Click "Credentials"
4. Click "+ Add Credentials"
5. Select "Email"
6. Fill in SMTP settings above
7. Test with test email
8. Save!
```

### ✅ How to Verify:

Use Test button in N8N Send Email node. Should receive test email in 1-2 seconds.

---

## 6️⃣ SQL QUERIES FOR WORKFLOWS

### **Workflow #2: Daily Analysis SQL**

```sql
-- Get yesterday's message statistics
SELECT 
  COUNT(*) as total_messages,
  COUNT(DISTINCT user_id) as unique_users,
  AVG(EXTRACT(EPOCH FROM (updated_at - created_at))) as avg_response_time_sec,
  MAX(created_at) as last_activity,
  DATE(created_at) as activity_date
FROM telegram_interactions
WHERE DATE(created_at) = CURRENT_DATE - INTERVAL '1 day'
  AND type IN ('question', 'analysis_request')
GROUP BY DATE(created_at);
```

**How to Add:**
```
1. Open Workflow #2
2. Find "Postgres: Execute SQL Query" node
3. Paste the SQL above
4. Click Save
```

### **Workflow #3: Hourly Report SQL**

```sql
-- Get last hour's messages
SELECT 
  id,
  user_id,
  text,
  type,
  created_at,
  response_time_ms
FROM telegram_interactions
WHERE created_at >= NOW() - INTERVAL '1 hour'
ORDER BY created_at DESC
LIMIT 100;
```

**How to Add:**
```
1. Open Workflow #3
2. Find "HTTP Request" node (Supabase REST)
3. This uses REST API, not direct SQL
4. URL: https://[project].supabase.co/rest/v1/telegram_interactions?order=created_at.desc&limit=100
```

---

## 🔧 CREATING REQUIRED TABLES

### **If Tables Don't Exist:**

**Create daily_reports table (for Workflow #2):**
```sql
CREATE TABLE IF NOT EXISTS daily_reports (
  id BIGSERIAL PRIMARY KEY,
  report_date DATE NOT NULL,
  total_messages INTEGER,
  unique_users INTEGER,
  avg_response_time DECIMAL,
  analysis TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(report_date)
);

CREATE INDEX idx_daily_reports_date ON daily_reports(report_date);
```

**Create hourly_reports table (for Workflow #3):**
```sql
CREATE TABLE IF NOT EXISTS hourly_reports (
  id BIGSERIAL PRIMARY KEY,
  report_hour TIMESTAMP NOT NULL,
  total_messages INTEGER,
  unique_users INTEGER,
  report_data JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(report_hour)
);

CREATE INDEX idx_hourly_reports_hour ON hourly_reports(report_hour);
```

**Run in Supabase SQL Editor:**
1. Go to Supabase Dashboard
2. SQL Editor → New Query
3. Paste the SQL above
4. Click "Run"
5. Should see: "Success. No rows returned"

---

## ✅ VERIFICATION CHECKLIST

Before marking SUB-TASK 4 as COMPLETE, verify:

- [ ] **Perplexity API Key**
  - [ ] Key obtained from https://perplexity.ai/settings/api
  - [ ] Added to WF#1 (HTTP Request headers)
  - [ ] Added to WF#2 (HTTP Request headers)
  - [ ] Test: Can make API call (see section 1️⃣)

- [ ] **Supabase Postgres**
  - [ ] Connection details obtained
  - [ ] Connection added to N8N credentials
  - [ ] Test connection: Green ✅
  - [ ] Anon key obtained for REST API
  - [ ] Tables created (daily_reports, hourly_reports)

- [ ] **Telegram Bot**
  - [ ] Bot token obtained from @BotFather
  - [ ] Bot credentials added to N8N
  - [ ] Test connection: Green ✅
  - [ ] Chat ID obtained
  - [ ] Chat ID added to WF#2 and WF#3
  - [ ] Test message sent successfully

- [ ] **Email SMTP (for WF#3)**
  - [ ] SMTP credentials obtained
  - [ ] Email credentials added to N8N
  - [ ] Test email sent successfully

- [ ] **SQL Queries**
  - [ ] WF#2 SQL query added to Postgres node
  - [ ] WF#3 Supabase REST API configured
  - [ ] Both tested with test data

---

## 🚀 NEXT STEPS

Once ALL credentials are collected:

1. **Activate Workflows:**
   ```
   WF#1: Open → Toggle "Active" → ON ✅
   WF#2: Open → Toggle "Active" → ON ✅
   WF#3: Open → Toggle "Active" → ON ✅
   ```

2. **Test Each Workflow:**
   - Click "Execute" button
   - Verify output in each node
   - Check logs for errors

3. **Monitor First Run:**
   - WF#1: Test via webhook immediately
   - WF#2: Wait until next 09:00 UTC
   - WF#3: Wait until next hour boundary

4. **Document Results:**
   - Update GitHub Issue #5
   - Mark SUB-TASK 4 as COMPLETE
   - Move to Phase 3 (Bot Development)

---

## 📞 TROUBLESHOOTING

### **"Unauthorized" error from Perplexity**
- Check API key is correct
- Check key is in format: `pplx-xxxxx`
- Verify Authorization header is: `Bearer pplx-xxxxx`

### **"Connection refused" from Supabase**
- Check hostname: should be `db.xxxxx.supabase.co`
- Check port: should be 5432
- Check SSL: should be "Allow"
- Verify IP whitelist in Supabase Settings

### **"Chat not found" from Telegram**
- Check Chat ID is numeric (not string)
- Check bot can access that chat
- Verify bot token is correct

### **"SMTP auth failed" from Email**
- Check Gmail App Password (not regular password)
- Check port is 587 (not 465)
- Check credentials are correct

---

**Time Estimate:** 45 minutes to complete all

**Difficulty:** Medium (mostly copy-paste)

**Due:** Dec 8, 2025 by 17:30 MSK

---

**Created by:** AI Assistant  
**Status:** 🟢 READY TO USE  
**Last Updated:** Dec 8, 2025, 16:00 MSK
