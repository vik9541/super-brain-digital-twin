# 🚀 DEPLOY: Simple PowerShell Commands (NO PIPES)

**Copy & Paste these commands ONE BY ONE**

---

## STEP 1: Create Namespace

```powershell
kubectl create namespace super-brain
```

**Wait for result, then check:**

```powershell
kubectl get namespaces
```

You should see `super-brain` in the list.

---

## STEP 2: Create Supabase Secret

```powershell
kubectl create secret generic supabase-credentials --from-literal=SUPABASE_URL=https://lvixtpatqrtuwnygtpjx.supabase.co --from-literal=SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx2aXh0cGF0cXJ0dXduaWd0cGpqeCIsInJvbGUiOiJhbm9uIiwiaWF0IjoxNzMwNjgyNTEyLCJleHAiOjE3NjIyMTg1MTJ9.DUMMYBASE64DUMMYBASE64DUMMYBASE64 --from-literal=SUPABASE_JWT_SECRET=super-secret-jwt-key-change-in-production -n super-brain
```

---

## STEP 3: Create Telegram Secret

```powershell
kubectl create secret generic telegram-credentials --from-literal=TELEGRAM_BOT_TOKEN=8326941950:AAHx7hj1JcJLeQl8eS5sTFlkLJ5S3ZM-L5p3BZoVE -n super-brain
```

---

## STEP 4: Create Perplexity Secret

```powershell
kubectl create secret generic perplexity-credentials --from-literal=PERPLEXITY_API_KEY=pplx-replace-with-actual-key -n super-brain
```

---

## STEP 5: Create N8N Secret

```powershell
kubectl create secret generic n8n-webhooks --from-literal=N8N_WEBHOOK_URL=https://lavrentev.app.n8n.cloud/webhook -n super-brain
```

---

## STEP 6: Create Database Secret

```powershell
kubectl create secret generic database-url --from-literal=DATABASE_URL=postgresql://user:pass@localhost:5432/super_brain_db -n super-brain
```

---

## STEP 7: Create JWT Secret

```powershell
kubectl create secret generic jwt-secret --from-literal=JWT_SECRET=your-jwt-secret-here-change-in-production-9876543210 -n super-brain
```

---

## STEP 8: Verify All Secrets

```powershell
kubectl get secrets -n super-brain
```

You should see 7 secrets listed.

---

## STEP 9: Deploy Bot

```powershell
kubectl apply -f https://raw.githubusercontent.com/vik9541/super-brain-digital-twin/main/k8s/deployments/telegram-bot-deployment.yaml
```

---

## STEP 10: Check Deployment Status

```powershell
kubectl get deployments -n super-brain
```

```powershell
kubectl get pods -n super-brain
```

---

## STEP 11: View Bot Logs

```powershell
kubectl logs -f deployment/telegram-bot -n super-brain
```

(Press CTRL+C to stop)

---

## ✅ DONE!

Your bot should now be running.
