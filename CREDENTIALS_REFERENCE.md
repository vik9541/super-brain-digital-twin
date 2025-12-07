# 🔐 CREDENTIALS REFERENCE — Super Brain Digital Twin

**📅 Дата:** 7 декабря 2025, 17:30 MSK  
**🟢 Статус:** VERIFIED & ACTIVE  
**🌟 Версия:** 1.0

---

# ✅ K8s SECRET: `digital-twin-secrets`

## Нахождение

**Namespace:** `production`  
**Type:** Opaque  
**Status:** 🟢 ACTIVE & VERIFIED  
**Created:** ~5 days ago

---

## 🔐 CREDENTIALS INVENTORY

| Key | Size | Purpose | Status |
|:---|:---:|:---|:---:|
| **SUPABASE_URL** | 40 bytes | Database connection URL | ✅ Ready |
| **SUPABASE_KEY** | 219 bytes | Database API key | ✅ Ready |
| **TELEGRAM_BOT_TOKEN** | 46 bytes | Telegram bot authentication | ✅ Ready |
| **PERPLEXITY_API_KEY** | 53 bytes | AI/ML API access | ✅ Ready |

---

## 📄 HOW TO VERIFY CREDENTIALS

### Command 1: List Secret
```bash
kubectl get secrets -n production | grep digital-twin
```

**Expected Output:**
```
digital-twin-secrets          Opaque       4      5d
```

### Command 2: Describe Secret
```bash
kubectl describe secret digital-twin-secrets -n production
```

**Expected Output:**
```
Name:         digital-twin-secrets
Namespace:    production
Type:         Opaque

Data
====
SUPABASE_URL:       40 bytes
SUPABASE_KEY:       219 bytes
TELEGRAM_BOT_TOKEN: 46 bytes
PERPLEXITY_API_KEY: 53 bytes
```

### Command 3: View Secret Values (Use with caution!)
```bash
# View SUPABASE_URL
kubectl get secret digital-twin-secrets -n production -o jsonpath='{.data.SUPABASE_URL}' | base64 --decode

# View TELEGRAM_BOT_TOKEN
kubectl get secret digital-twin-secrets -n production -o jsonpath='{.data.TELEGRAM_BOT_TOKEN}' | base64 --decode

# View all secrets (careful - outputs all values!)
kubectl get secret digital-twin-secrets -n production -o yaml
```

---

## 🔗 HOW CREDENTIALS ARE USED

### In K8s CronJobs

**File:** `k8s/batch-analyzer-cronjob.yaml`

```yaml
env:
- name: SUPABASE_URL
  valueFrom:
    secretKeyRef:
      name: digital-twin-secrets
      key: SUPABASE_URL

- name: SUPABASE_KEY
  valueFrom:
    secretKeyRef:
      name: digital-twin-secrets
      key: SUPABASE_KEY

- name: TELEGRAM_BOT_TOKEN
  valueFrom:
    secretKeyRef:
      name: digital-twin-secrets
      key: TELEGRAM_BOT_TOKEN

- name: PERPLEXITY_API_KEY
  valueFrom:
    secretKeyRef:
      name: digital-twin-secrets
      key: PERPLEXITY_API_KEY
```

### In Python Code

**File:** `batch_analyzer.py`

```python
import os

# Credentials automatically injected by K8s
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
```

---

## 📌 TASKS USING THESE CREDENTIALS

### ✅ TASK-002: Batch Analyzer
**Status:** 🟢 READY  
**Uses:** SUPABASE_URL, SUPABASE_KEY, TELEGRAM_BOT_TOKEN, PERPLEXITY_API_KEY  
**File:** https://github.com/vik9541/super-brain-digital-twin/blob/main/batch_analyzer.py

### ✅ TASK-003: Reports Generator
**Status:** 🟢 READY  
**Uses:** SUPABASE_URL, SUPABASE_KEY, TELEGRAM_BOT_TOKEN  
**File:** https://github.com/vik9541/super-brain-digital-twin/blob/main/reports_generator.py

### ✅ TASK-004: Grafana Dashboard
**Status:** 🟢 READY  
**Uses:** None (uses Prometheus metrics)  

### ✅ TASK-005: API Extensions
**Status:** 🟢 READY  
**Uses:** SUPABASE_URL, SUPABASE_KEY  
**File:** https://github.com/vik9541/super-brain-digital-twin/blob/main/api/main.py

---

## ⚠️ SECURITY BEST PRACTICES

✅ **DO:**
- ✅ Store all secrets in K8s Secrets
- ✅ Use secret names in K8s manifests
- ✅ Never commit credentials to Git
- ✅ Rotate credentials regularly
- ✅ Audit secret access logs
- ✅ Use RBAC to limit secret access

❌ **DON'T:**
- ❌ Pass credentials as environment variables in manifests
- ❌ Print credentials in logs
- ❌ Share credentials in Slack/email
- ❌ Store credentials in .env files
- ❌ Commit secrets.yaml to Git

---

## 🔄 IF YOU NEED TO UPDATE CREDENTIALS

### Option 1: Delete and Recreate
```bash
# Delete old secret
kubectl delete secret digital-twin-secrets -n production

# Create new secret with updated values
kubectl create secret generic digital-twin-secrets \
  --from-literal=SUPABASE_URL="new-url" \
  --from-literal=SUPABASE_KEY="new-key" \
  --from-literal=TELEGRAM_BOT_TOKEN="new-token" \
  --from-literal=PERPLEXITY_API_KEY="new-api-key" \
  -n production

# Restart pods to pick up new secrets
kubectl rollout restart deployment/batch-analyzer -n production
kubectl rollout restart cronjob/batch-analyzer -n production
```

### Option 2: Patch Existing Secret
```bash
# Patch a single key
kubectl patch secret digital-twin-secrets -n production \
  -p '{"data": {"SUPABASE_URL": "'$(echo -n 'new-url' | base64)'"}}'
```

### Option 3: Using External Secret Management
Consider using:
- 💫 HashiCorp Vault
- 💫 AWS Secrets Manager
- 💫 Azure Key Vault
- 💫 Google Secret Manager

---

## 📊 AUDIT TRAIL

**Created:** ~5 days ago (DigitalOcean DOKS initialization)  
**Last Verified:** 7 Dec 2025, 17:30 MSK  
**Status:** 🟢 ACTIVE & WORKING  
**Access Method:** kubectl (K8s API)  

---

## 👤 RESPONSIBLE PARTIES

**Credentials Owner:** @vik9541 (Project Lead)  
**Infrastructure:** @Pavel T. (INFRA Lead)  
**Security:** @Alexander Z. (Security Lead)  

---

## 🔗 RELATED DOCUMENTATION

| Document | Purpose | Link |
|:---|:---|:---:|
| TASK-002 Checklist | Deployment guide | [Link](./TASKS/TASK-002-INFRA-CHECKLIST.md) |
| Batch Analyzer Code | Python implementation | [Link](./batch_analyzer.py) |
| K8s Manifests | CronJob + RBAC | [Link](./k8s/) |
| Security Guide | Secrets best practices | [Link](https://kubernetes.io/docs/concepts/configuration/secret/) |

---

**🟢 Status:** ALL CREDENTIALS VERIFIED & READY TO USE  
**⚠️ Sensitive Data:** This file references secret keys but does NOT contain actual values
