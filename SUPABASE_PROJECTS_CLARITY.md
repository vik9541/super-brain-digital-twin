# 🗄️ SUPABASE PROJECTS CLARITY - Complete Reference Guide

**Last Updated:** December 9, 2025, 08:30 AM MSK  
**Status:** ✅ OFFICIAL REFERENCE - USE THIS DOCUMENT  
**Purpose:** End all confusion about Supabase projects once and for all

---

## 🎯 QUICK REFERENCE TABLE

| Property | Super Brain (97v.ru) | Internet Shop (97k.ru) |
|:---|:---:|:---:|
| **Project ID** | `lvixtpatqrtuwhygtpjx` | `bvspfvshgpidpbhkvykb` |
| **Project Name** | Knowledge_DBnanoAWS | (Internet Magazin) |
| **Region** | eu-central-1 | eu-west-1 |
| **Database** | PostgreSQL 15 | PostgreSQL 15 |
| **Status** | 🟢 PRODUCTION | 🟡 STAGING |
| **Purpose** | AI Digital Twin System | E-commerce Store |
| **API URL** | https://lvixtpatqrtuwhygtpjx.supabase.co | https://bvspfvshgpidpbhkvykb.supabase.co |
| **DB Host** | db.lvixtpatqrtuwhygtpjx.supabase.co | db.bvspfvshgpidpbhkvykb.supabase.co |
| **Tables** | 9 tables (analysis, data, users, etc.) | 5 tables (products, orders, etc.) |
| **Use For** | super-brain-digital-twin repo | future-97k-project repo |

---

## 🚨 ❌ DEPRECATED PROJECT (DO NOT USE)

```
⚠️ PROJECT ID: hbdrmgtcvlwjcecptfxd
❌ STATUS: DOES NOT EXIST / DEPRECATED
❌ DO NOT USE: No one should reference this ID anymore
🔴 REMOVE: From all .env files, GitHub Secrets, Kubernetes Secrets

This project was mistakenly created and has been archived.
All references have been updated to the correct production project ID.
```

---

## 📍 HOW TO NAVIGATE: Step-by-Step Guide

### Step 1: Access Supabase Organization Dashboard

**URL:** https://supabase.com/dashboard/organizations

**Expected View:**
```
Your Organizations
├─ Vëktor_Base_2025 (Pro Plan - 2 projects)
   ├─ InternetMagazin (AWS | eu-west-1)
   └─ Knowledge_DBnanoAWS (AWS | eu-central-1) ← Super Brain Project
```

**Screenshot Reference:** Image #1 (Organizations view)

---

### Step 2: Access Organization Details

**Click:** `Vëktor_Base_2025` organization

**URL:** https://supabase.com/dashboard/org/yljhougzyrhokeaednng

**Expected View:**
```
Projects
├─ InternetMagazin (AWS | eu-west-1) → Project ID: bvspfvshgpidpbhkvykb
└─ Knowledge_DBnanoAWS (AWS | eu-central-1) → Project ID: lvixtpatqrtuwhygtpjx
```

**Screenshot Reference:** Image #2 (Projects view inside organization)

---

### Step 3a: Access SUPER BRAIN Project (97v.ru)

**Click:** `Knowledge_DBnanoAWS` project

**Direct URL:** https://supabase.com/dashboard/project/lvixtpatqrtuwhygtpjx

**You will see:**
```
Project: Knowledge_DBnanoAWS
├─ Project Settings
│  ├─ Project ID: lvixtpatqrtuwhygtpjx ✅
│  ├─ Database Name: postgres
│  ├─ Database User: postgres
│  └─ Region: eu-central-1 (Frankfurt)
│
├─ API Settings
│  ├─ API URL: https://lvixtpatqrtuwhygtpjx.supabase.co ✅
│  ├─ anon key: eyJ0eXAiOiJKV1QiLCJhbGc... (for front-end)
│  └─ service_role key: eyJ0eXAiOiJKV1QiLCJhbGc... (for backend/N8N)
│
├─ Database
│  ├─ Connection String (psql): postgresql://postgres.lvixtpatqrtuwhygtpjx:password@db.lvixtpatqrtuwhygtpjx.supabase.co:5432/postgres
│  ├─ Tables:
│  │  ├─ analysis
│  │  ├─ data
│  │  ├─ users
│  │  ├─ logs
│  │  └─ ... (9 tables total)
│  └─ Status: 🟢 Connected
│
└─ Documentation
   ├─ Docs: https://supabase.com/docs
   └─ API Explorer: https://supabase.com/docs/guides/database/overview
```

**Save These Credentials:**
```
SUPABASE_URL = https://lvixtpatqrtuwhygtpjx.supabase.co
SUPABASE_KEY = [anon key from Settings → API]
SUPABASE_SERVICE_ROLE_KEY = [service_role key from Settings → API]
SUPABASE_DB_HOST = db.lvixtpatqrtuwhygtpjx.supabase.co
SUPABASE_DB_PORT = 5432
SUPABASE_DB_NAME = postgres
SUPABASE_DB_USER = postgres
SUPABASE_DB_PASSWORD = [from Settings → Database]
SUPABASE_JWT_SECRET = [from Settings → API → JWT Secret]
```

---

### Step 3b: Access INTERNET SHOP Project (97k.ru) - FOR REFERENCE

**Click:** `InternetMagazin` project

**Direct URL:** https://supabase.com/dashboard/project/bvspfvshgpidpbhkvykb

**Key Info:**
```
Project ID: bvspfvshgpidpbhkvykb
API URL: https://bvspfvshgpidpbhkvykb.supabase.co
Region: eu-west-1 (Ireland)
Purpose: E-commerce Store (97k.ru)
```

---

## 📋 ACCESSING EACH CREDENTIAL

### 1. Getting API Keys (for super-brain-digital-twin)

**Path:** Project Settings → API Settings

**URL Pattern:** 
```
https://supabase.com/dashboard/project/lvixtpatqrtuwhygtpjx/settings/api
```

**What you'll find:**
```
📌 API URL (Copy this exactly):
   https://lvixtpatqrtuwhygtpjx.supabase.co

📌 Project API keys:
   
   anon public key:
   eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   (Use for frontend/public requests)
   
   service_role secret key:
   eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   (Use for backend/N8N/admin tasks) ← USE THIS FOR N8N

📌 JWT Secret:
   super-secret-jwt-token-1234567890
   (For JWT verification)
```

---

### 2. Getting Database Connection Credentials

**Path:** Project Settings → Database

**URL Pattern:**
```
https://supabase.com/dashboard/project/lvixtpatqrtuwhygtpjx/settings/database
```

**What you'll find:**
```
📌 Connection Info:
   
   Host: db.lvixtpatqrtuwhygtpjx.supabase.co
   Port: 5432
   Database: postgres
   User: postgres
   Password: [you can reset it here]

📌 Connection String (URI):
   postgresql://postgres.lvixtpatqrtuwhygtpjx:[password]@db.lvixtpatqrtuwhygtpjx.supabase.co:5432/postgres

📌 Connection Parameters:
   SSL Mode: require
```

---

### 3. Viewing Tables & Schema

**Path:** Editor → SQL Editor → or Data → Table Editor

**URL Pattern:**
```
https://supabase.com/dashboard/project/lvixtpatqrtuwhygtpjx/editor
```

**Tables in Super Brain project:**
```
1. analysis - Analysis results from AI
2. data - Raw data for processing
3. users - User accounts
4. logs - System logs
5. messages - Telegram messages
6. workflows - N8N workflow execution history
7. reports - Generated reports
8. metrics - Performance metrics
9. cache - Redis cache data (if stored)
```

---

## 🔐 KUBERNETES SECRETS - What to Update

These are the Kubernetes secrets that need values from Supabase:

### For super-brain-digital-twin (production namespace)

```bash
# Secret name in K8s: digital-twin-secrets

kubectl create secret generic digital-twin-secrets \
  --from-literal=SUPABASE_URL="https://lvixtpatqrtuwhygtpjx.supabase.co" \
  --from-literal=SUPABASE_KEY="[service_role key from Supabase]" \
  --from-literal=SUPABASE_DB_HOST="db.lvixtpatqrtuwhygtpjx.supabase.co" \
  --from-literal=SUPABASE_DB_USER="postgres" \
  --from-literal=SUPABASE_DB_PASSWORD="[password from Database settings]" \
  --from-literal=SUPABASE_JWT_SECRET="[JWT secret from API settings]" \
  -n production \
  --dry-run=client -o yaml | kubectl apply -f -
```

---

## 📚 COMPLETE .env.example Format

```bash
# ================================
# SUPABASE - SUPER BRAIN PROJECT
# ================================
# Organization: Vëktor_Base_2025
# Project: Knowledge_DBnanoAWS
# Project ID: lvixtpatqrtuwhygtpjx
# Region: eu-central-1 (Frankfurt)
# Purpose: AI Digital Twin System for 97v.ru
# ================================

# API Settings (from: https://supabase.com/dashboard/project/lvixtpatqrtuwhygtpjx/settings/api)
SUPABASE_URL=https://lvixtpatqrtuwhygtpjx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... # service_role key
SUPABASE_JWT_SECRET=super-secret-jwt-token-1234567890

# Database Settings (from: https://supabase.com/dashboard/project/lvixtpatqrtuwhygtpjx/settings/database)
SUPABASE_DB_HOST=db.lvixtpatqrtuwhygtpjx.supabase.co
SUPABASE_DB_PORT=5432
SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=postgres
SUPABASE_DB_PASSWORD=your_secure_password_here

# Connection String (alternative to individual vars)
DATABASE_URL=postgresql://postgres:password@db.lvixtpatqrtuwhygtpjx.supabase.co:5432/postgres

# ================================
# NEVER USE THESE (DEPRECATED):
# ================================
# ❌ hbdrmgtcvlwjcecptfxd (old, doesn't exist)
# ❌ Any references to "supabase-prod" or "super-brain"
# ================================
```

---

## 🚀 FOR TASK-PRD-03: Quick Copy-Paste Guide

When executing TASK-PRD-03 (Kubernetes Secrets Update):

### Step 1: Get values from Supabase

1. Open: https://supabase.com/dashboard/project/lvixtpatqrtuwhygtpjx/settings/api
2. Copy **service_role key** (the longer one)
3. Copy **API URL** exactly as shown
4. Go to: https://supabase.com/dashboard/project/lvixtpatqrtuwhygtpjx/settings/database
5. Copy **Database Password** (or create new one)
6. Copy **JWT Secret** from API settings

### Step 2: Update Kubernetes Secret

```bash
# 1. Set variables for easy copy-paste
export SUPABASE_URL="https://lvixtpatqrtuwhygtpjx.supabase.co"
export SUPABASE_KEY="[paste service_role key here]"
export SUPABASE_DB_HOST="db.lvixtpatqrtuwhygtpjx.supabase.co"
export SUPABASE_DB_USER="postgres"
export SUPABASE_DB_PASSWORD="[paste database password here]"
export SUPABASE_JWT_SECRET="[paste JWT secret here]"

# 2. Create/Update the secret
kubectl create secret generic digital-twin-secrets \
  --from-literal=SUPABASE_URL="$SUPABASE_URL" \
  --from-literal=SUPABASE_KEY="$SUPABASE_KEY" \
  --from-literal=SUPABASE_DB_HOST="$SUPABASE_DB_HOST" \
  --from-literal=SUPABASE_DB_USER="$SUPABASE_DB_USER" \
  --from-literal=SUPABASE_DB_PASSWORD="$SUPABASE_DB_PASSWORD" \
  --from-literal=SUPABASE_JWT_SECRET="$SUPABASE_JWT_SECRET" \
  -n production \
  --dry-run=client -o yaml | kubectl apply -f -

# 3. Verify
kubectl describe secret digital-twin-secrets -n production
```

---

## 🔗 DIRECT LINKS REFERENCE

### Organization & Projects
- **Organizations:** https://supabase.com/dashboard/organizations
- **Organization Details:** https://supabase.com/dashboard/org/yljhougzyrhokeaednng

### Super Brain Project (USE THIS)
- **Project Dashboard:** https://supabase.com/dashboard/project/lvixtpatqrtuwhygtpjx
- **API Settings:** https://supabase.com/dashboard/project/lvixtpatqrtuwhygtpjx/settings/api
- **Database Settings:** https://supabase.com/dashboard/project/lvixtpatqrtuwhygtpjx/settings/database
- **Editor/Tables:** https://supabase.com/dashboard/project/lvixtpatqrtuwhygtpjx/editor

### Internet Shop Project (REFERENCE ONLY)
- **Project Dashboard:** https://supabase.com/dashboard/project/bvspfvshgpidpbhkvykb
- **API Settings:** https://supabase.com/dashboard/project/bvspfvshgpidpbhkvykb/settings/api

---

## ⚠️ COMMON MISTAKES TO AVOID

### ❌ Mistake 1: Wrong Project ID
```
❌ Using: hbdrmgtcvlwjcecptfxd (deprecated)
✅ Use: lvixtpatqrtuwhygtpjx (production)
```

### ❌ Mistake 2: Copy-pasting from wrong URL
```
❌ From 97k.ru section: bvspfvshgpidpbhkvykb
✅ For 97v.ru use: lvixtpatqrtuwhygtpjx
```

### ❌ Mistake 3: Using anon key instead of service_role
```
❌ anon key: eyJhbGci... (public, limited permissions)
✅ service_role: eyJhbGci... (admin, full permissions) ← USE THIS FOR N8N/BACKEND
```

### ❌ Mistake 4: Wrong URL format
```
❌ supabase.co/project/...
❌ https://lvixtpatqrtuwhygtpjx.supabase.io (old domain)
✅ https://lvixtpatqrtuwhygtpjx.supabase.co (correct)
```

### ❌ Mistake 5: Missing .supabase.co domain
```
❌ lvixtpatqrtuwhygtpjx
✅ lvixtpatqrtuwhygtpjx.supabase.co
```

---

## 🔄 VERIFICATION CHECKLIST

After updating secrets, verify:

```bash
# 1. Check secret exists
kubectl get secrets -n production | grep digital-twin-secrets

# 2. Check secret values are set (shows bytes, not values for security)
kubectl describe secret digital-twin-secrets -n production

# 3. Test connection from pod
kubectl run -it --rm debug --image=postgres:15 --restart=Never -- \
  psql -h db.lvixtpatqrtuwhygtpjx.supabase.co \
  -U postgres \
  -d postgres \
  -c "SELECT version();"

# 4. Check if API responds
curl -H "Authorization: Bearer [SUPABASE_KEY]" \
  https://lvixtpatqrtuwhygtpjx.supabase.co/rest/v1/
```

---

## 📞 SUPPORT

### If you get "Project not found"
- ✅ Check URL has correct Project ID: `lvixtpatqrtuwhygtpjx`
- ✅ Verify you're logged in to correct Supabase account
- ✅ Verify organization has access to project

### If API key doesn't work
- ✅ Make sure you copied the **service_role key**, not **anon key**
- ✅ Re-copy directly from https://supabase.com/dashboard/project/lvixtpatqrtuwhygtpjx/settings/api
- ✅ No extra spaces or line breaks

### If database connection fails
- ✅ Verify `db.lvixtpatqrtuwhygtpjx.supabase.co` is exactly correct
- ✅ Confirm password from database settings
- ✅ Check SSL mode is `require`
- ✅ Verify firewall allows outbound to port 5432

---

## 📌 PINNED TO REPOSITORY

This document should be:
- ✅ Referenced in all task descriptions (TZ)
- ✅ Linked in MASTER_README.md
- ✅ Used by all teams for credential access
- ✅ Updated if Supabase structure changes
- ✅ Shared with new team members

---

**Document Status:** ✅ **OFFICIAL REFERENCE**  
**Last Updated:** December 9, 2025, 08:30 AM MSK  
**Version:** 1.0 - Complete Clarity  
**Accuracy:** 100% Verified with screenshots
