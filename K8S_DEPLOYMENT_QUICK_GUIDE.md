# 🚀 K8s Deployment Quick Guide

**Date:** December 10, 2025  
**Status:** ✅ READY FOR DEPLOYMENT  
**Related Issue:** #38 (TASK-PRD-04)  

---

## 📋 QUICKSTART (3 COMMANDS)

```powershell
# 1. Run the deployment script
.\DEPLOY_BOT_K8S.ps1

# 2. Check status
kubectl get pods -n super-brain

# 3. View logs
kubectl logs -f -n super-brain deployment/telegram-bot
```

---

## 🎯 What Gets Deployed

✅ **Namespace:** `super-brain`  
✅ **Deployment:** `telegram-bot` (2 replicas)  
✅ **Service:** `telegram-bot` (ClusterIP on port 8000)  
✅ **ServiceAccount:** `telegram-bot`  
✅ **RBAC:** Role + RoleBinding  
✅ **HPA:** Horizontal Pod Autoscaler (2-5 replicas)  
✅ **K8s Secrets:** 7 secrets (Supabase, Telegram, Perplexity, N8N, Database, JWT)  

---

## 📦 Prerequisites

- ✅ PowerShell 7+ or Windows PowerShell
- ✅ kubectl installed and configured
- ✅ Access to DigitalOcean DOKS cluster
- ✅ Bot image available: `vik9541/super-brain-bot:latest`

---

## 🚀 Step-by-Step Deployment

### Option A: Automated (RECOMMENDED)

**Run the PowerShell script:**

```powershell
cd C:\Users\9541\Documents\super-brain-digital-twin
.\DEPLOY_BOT_K8S.ps1
```

This will:
1. Create namespace
2. Create 7 K8s secrets
3. Deploy bot
4. Wait for pods to be ready
5. Show status and logs

**⏱️ Time:** ~2 minutes

---

### Option B: Manual (Step-by-Step)

#### Step 1: Create Namespace

```powershell
kubectl create namespace super-brain
```

#### Step 2: Create Secrets

```powershell
# Supabase
kubectl create secret generic supabase-credentials `
  --from-literal=SUPABASE_URL=https://lvixtpatqrtuwnygtpjx.supabase.co `
  --from-literal=SUPABASE_KEY=YOUR_KEY_HERE `
  --from-literal=SUPABASE_JWT_SECRET=YOUR_JWT_SECRET `
  -n super-brain

# Telegram
kubectl create secret generic telegram-credentials `
  --from-literal=TELEGRAM_BOT_TOKEN=YOUR_TOKEN_HERE `
  -n super-brain

# Perplexity
kubectl create secret generic perplexity-credentials `
  --from-literal=PERPLEXITY_API_KEY=YOUR_KEY_HERE `
  -n super-brain

# N8N
kubectl create secret generic n8n-webhooks `
  --from-literal=N8N_WEBHOOK_URL=https://lavrentev.app.n8n.cloud/webhook `
  -n super-brain

# Database
kubectl create secret generic database-url `
  --from-literal=DATABASE_URL=postgresql://user:pass@host:5432/db `
  -n super-brain

# JWT
kubectl create secret generic jwt-secret `
  --from-literal=JWT_SECRET=YOUR_JWT_SECRET `
  -n super-brain
```

#### Step 3: Deploy Bot

```powershell
kubectl apply -f k8s/deployments/telegram-bot-deployment.yaml -n super-brain
```

#### Step 4: Wait for Pods

```powershell
kubectl wait --for=condition=ready pod -l app=telegram-bot -n super-brain --timeout=120s
```

---

## ✅ Verification

### Check Namespace

```powershell
kubectl get namespace super-brain
```

**Expected:**
```
NAME          STATUS   AGE
super-brain   Active   X minutes
```

### Check Secrets

```powershell
kubectl get secrets -n super-brain
```

**Expected:**
```
NAME                       TYPE     DATA   AGE
supabase-credentials       Opaque   3      X
telegram-credentials       Opaque   1      X
perplexity-credentials     Opaque   1      X
n8n-webhooks              Opaque   1      X
database-url              Opaque   1      X
jwt-secret                Opaque   1      X
```

### Check Deployment

```powershell
kubectl get deployment -n super-brain
```

**Expected:**
```
NAME            READY   UP-TO-DATE   AVAILABLE   AGE
telegram-bot    2/2     2            2           X
```

### Check Pods

```powershell
kubectl get pods -n super-brain
```

**Expected:**
```
NAME                             READY   STATUS    RESTARTS   AGE
telegram-bot-xxxxx-xxxxx        1/1     Running   0          X
telegram-bot-xxxxx-yyyyy        1/1     Running   0          X
```

### Check Service

```powershell
kubectl get service -n super-brain
```

**Expected:**
```
NAME            TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)
telegram-bot    ClusterIP   10.xx.xx.xx     <none>        8000/TCP
```

---

## 🔍 Monitoring

### View Logs (Real-time)

```powershell
kubectl logs -f -n super-brain deployment/telegram-bot
```

### View Logs (Last N lines)

```powershell
kubectl logs -n super-brain deployment/telegram-bot --tail=50
```

### View Logs (Specific Pod)

```powershell
$podName = kubectl get pods -n super-brain -l app=telegram-bot -o jsonpath='{.items[0].metadata.name}'
kubectl logs -n super-brain $podName
```

### View Pod Events

```powershell
kubectl describe pod -n super-brain deployment/telegram-bot
```

### View Pod Details

```powershell
kubectl get pods -n super-brain -o yaml
```

---

## 📊 Scaling & Performance

### Manual Scaling

```powershell
# Scale to 3 replicas
kubectl scale deployment telegram-bot -n super-brain --replicas=3

# Check scaling
kubectl get deployment telegram-bot -n super-brain
```

### Check HPA Status

```powershell
kubectl get hpa -n super-brain

# Detailed HPA info
kubectl describe hpa telegram-bot -n super-brain
```

### View Metrics (if Prometheus installed)

```powershell
kubectl top pod -n super-brain
kubectl top node
```

---

## 🔧 Troubleshooting

### Pods Not Starting?

```powershell
# Check pod status
kubectl describe pod -n super-brain (pod_name)

# Check events
kubectl get events -n super-brain --sort-by='.lastTimestamp'

# Check logs
kubectl logs -n super-brain (pod_name)
```

### Secret Not Found?

```powershell
# Verify secret exists
kubectl get secret (secret_name) -n super-brain

# Verify secret content
kubectl describe secret (secret_name) -n super-brain
```

### Image Pull Error?

```powershell
# Check image
kubectl describe pod -n super-brain (pod_name) | grep -A 5 "Events"

# Verify image exists
docker pull vik9541/super-brain-bot:latest
```

### Port Forwarding Issue?

```powershell
# Forward port locally
kubectl port-forward -n super-brain svc/telegram-bot 8000:8000

# Test connection
Invoke-WebRequest -Uri http://localhost:8000/health
```

---

## 🔄 Update & Rollback

### Update Deployment

```powershell
# Update image
kubectl set image deployment/telegram-bot telegram-bot=vik9541/super-brain-bot:v4.1 -n super-brain

# Check rollout status
kubectl rollout status deployment/telegram-bot -n super-brain
```

### Rollback to Previous Version

```powershell
# View rollout history
kubectl rollout history deployment/telegram-bot -n super-brain

# Rollback
kubectl rollout undo deployment/telegram-bot -n super-brain
```

---

## ⚠️ Common Issues & Solutions

| Issue | Solution |
|:---|:---|
| **Pod stuck in Pending** | Check resource limits: `kubectl describe node` |
| **CrashLoopBackOff** | Check logs: `kubectl logs -n super-brain (pod_name)` |
| **ImagePullBackOff** | Verify image exists: `docker pull vik9541/super-brain-bot:latest` |
| **Connection refused** | Check service: `kubectl get svc -n super-brain` |
| **Secret not injected** | Restart pods: `kubectl rollout restart deployment/telegram-bot -n super-brain` |
| **Out of memory** | Increase limits in deployment manifest |
| **High CPU usage** | Check HPA metrics: `kubectl describe hpa -n super-brain` |

---

## 📌 Files Reference

| File | Purpose |
|:---|:---|
| `DEPLOY_BOT_K8S.ps1` | Automated deployment script |
| `k8s/deployments/telegram-bot-deployment.yaml` | Kubernetes manifest |
| `DEPLOYMENT_CREDENTIALS_K8S_GUIDE.md` | Detailed credentials guide |
| `K8S_DEPLOYMENT_QUICK_GUIDE.md` | This file |
| `api/bot_handler.py` | Bot implementation |

---

## 🎯 Next Steps

1. ✅ Run deployment script
2. ✅ Verify all pods are running
3. ✅ Check logs for errors
4. ✅ Send test message to bot
5. ✅ Monitor for 24 hours
6. ✅ Document any issues
7. ✅ Update CHECKLIST.md with completion

---

## 📞 Support

**Documentation:** [DEPLOYMENT_CREDENTIALS_K8S_GUIDE.md](./DEPLOYMENT_CREDENTIALS_K8S_GUIDE.md)  
**GitHub Issue:** [#38 - TASK-PRD-04](https://github.com/vik9541/super-brain-digital-twin/issues/38)  
**Contact:** @vik9541 (Project Lead)  

---

**Last Updated:** December 10, 2025, 17:23 MSK  
**Status:** ✅ READY FOR DEPLOYMENT  
**Version:** 1.0
