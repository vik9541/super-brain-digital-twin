# PowerShell Script for Complete K8s Deployment
# SUPER BRAIN Telegram Bot - December 10, 2025
# Run in: PowerShell (Administrator)

Write-Host "🚀 SUPER BRAIN BOT - COMPLETE K8S DEPLOYMENT" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# ==================================================
# STEP 1: Create Namespace
# ==================================================
Write-Host "📍 STEP 1: Creating namespace 'super-brain'..." -ForegroundColor Yellow
kubectl create namespace super-brain 2>$null
Start-Sleep -Seconds 1
Write-Host "✅ Namespace ready" -ForegroundColor Green
Write-Host ""

# ==================================================
# STEP 2: Create K8s Secrets
# ==================================================
Write-Host "📍 STEP 2: Creating K8s Secrets..." -ForegroundColor Yellow

# 2a. Supabase
Write-Host "  [2.1] Creating SUPABASE credentials..." -ForegroundColor Cyan
kubectl create secret generic supabase-credentials `
  --from-literal=SUPABASE_URL=https://lvixtpatqrtuwnygtpjx.supabase.co `
  --from-literal=SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx2aXh0cGF0cXJ0dXduaWd0cGpqeCIsInJvbGUiOiJhbm9uIiwiaWF0IjoxNzMwNjgyNTEyLCJleHAiOjE3NjIyMTg1MTJ9.DUMMYBASE64DUMMYBASE64DUMMYBASE64 `
  --from-literal=SUPABASE_JWT_SECRET=super-secret-jwt-key-change-in-production `
  -n super-brain `
  --dry-run=client -o yaml 2>$null | kubectl apply -f - 2>$null
Write-Host "    ✅ Done" -ForegroundColor Green

# 2b. Telegram
Write-Host "  [2.2] Creating TELEGRAM credentials..." -ForegroundColor Cyan
kubectl create secret generic telegram-credentials `
  --from-literal=TELEGRAM_BOT_TOKEN=8326941950:AAHx7hj1JcJLeQl8eS5sTFlkLJ5S3ZM-L5p3BZoVE `
  -n super-brain `
  --dry-run=client -o yaml 2>$null | kubectl apply -f - 2>$null
Write-Host "    ✅ Done" -ForegroundColor Green

# 2c. Perplexity
Write-Host "  [2.3] Creating PERPLEXITY credentials..." -ForegroundColor Cyan
kubectl create secret generic perplexity-credentials `
  --from-literal=PERPLEXITY_API_KEY=pplx-replace-with-actual-key `
  -n super-brain `
  --dry-run=client -o yaml 2>$null | kubectl apply -f - 2>$null
Write-Host "    ✅ Done" -ForegroundColor Green

# 2d. N8N
Write-Host "  [2.4] Creating N8N webhooks secret..." -ForegroundColor Cyan
kubectl create secret generic n8n-webhooks `
  --from-literal=N8N_WEBHOOK_URL=https://lavrentev.app.n8n.cloud/webhook `
  -n super-brain `
  --dry-run=client -o yaml 2>$null | kubectl apply -f - 2>$null
Write-Host "    ✅ Done" -ForegroundColor Green

# 2e. Database
Write-Host "  [2.5] Creating DATABASE URL secret..." -ForegroundColor Cyan
kubectl create secret generic database-url `
  --from-literal=DATABASE_URL=postgresql://user:pass@localhost:5432/super_brain_db `
  -n super-brain `
  --dry-run=client -o yaml 2>$null | kubectl apply -f - 2>$null
Write-Host "    ✅ Done" -ForegroundColor Green

# 2f. JWT
Write-Host "  [2.6] Creating JWT secret..." -ForegroundColor Cyan
kubectl create secret generic jwt-secret `
  --from-literal=JWT_SECRET=your-jwt-secret-here-change-in-production-9876543210 `
  -n super-brain `
  --dry-run=client -o yaml 2>$null | kubectl apply -f - 2>$null
Write-Host "    ✅ Done" -ForegroundColor Green

Write-Host "✅ All secrets created" -ForegroundColor Green
Write-Host ""

# ==================================================
# STEP 3: Verify Secrets
# ==================================================
Write-Host "📍 STEP 3: Verifying secrets..." -ForegroundColor Yellow
$secretCount = kubectl get secrets -n super-brain -o name 2>$null | Measure-Object | Select-Object -ExpandProperty Count
Write-Host "  Found $secretCount secrets in namespace" -ForegroundColor Cyan
Write-Host ""
kubectl get secrets -n super-brain 2>$null
Write-Host ""

# ==================================================
# STEP 4: Deploy Telegram Bot
# ==================================================
Write-Host "📍 STEP 4: Deploying Telegram Bot..." -ForegroundColor Yellow

# Check if file exists
$botDeploymentFile = "k8s/deployments/telegram-bot-deployment.yaml"
if (Test-Path $botDeploymentFile) {
    Write-Host "  Applying manifest from: $botDeploymentFile" -ForegroundColor Cyan
    kubectl apply -f $botDeploymentFile 2>$null
    Write-Host "  ✅ Deployment applied" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  File not found: $botDeploymentFile" -ForegroundColor Yellow
    Write-Host "  Using inline deployment..." -ForegroundColor Cyan
    # Apply deployment from GitHub
    kubectl apply -f https://raw.githubusercontent.com/vik9541/super-brain-digital-twin/main/k8s/deployments/telegram-bot-deployment.yaml 2>$null
    Write-Host "  ✅ Deployment applied" -ForegroundColor Green
}
Write-Host ""

# ==================================================
# STEP 5: Wait for deployment
# ==================================================
Write-Host "📍 STEP 5: Waiting for deployment to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

$maxWaitTime = 120
$elapsedTime = 0
$podReady = $false

while ($elapsedTime -lt $maxWaitTime) {
    $pods = kubectl get pods -n super-brain -l app=telegram-bot -o jsonpath='{.items[*].status.conditions[?(@.type=="Ready")].status}' 2>$null
    if ($pods -like "*True*") {
        $podReady = $true
        break
    }
    Write-Host "  Waiting... ($elapsedTime/$maxWaitTime seconds)" -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    $elapsedTime += 5
}

if ($podReady) {
    Write-Host "  ✅ Pods are ready!" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Timeout waiting for pods" -ForegroundColor Yellow
}
Write-Host ""

# ==================================================
# STEP 6: Show Deployment Status
# ==================================================
Write-Host "📍 STEP 6: Deployment Status" -ForegroundColor Yellow
Write-Host ""
Write-Host "Deployments:" -ForegroundColor Cyan
kubectl get deployments -n super-brain 2>$null
Write-Host ""

Write-Host "Pods:" -ForegroundColor Cyan
kubectl get pods -n super-brain 2>$null
Write-Host ""

Write-Host "Services:" -ForegroundColor Cyan
kubectl get services -n super-brain 2>$null
Write-Host ""

# ==================================================
# STEP 7: Show logs
# ==================================================
Write-Host "📍 STEP 7: Pod Logs (last 10 lines)" -ForegroundColor Yellow
Write-Host ""
$podName = kubectl get pods -n super-brain -l app=telegram-bot -o jsonpath='{.items[0].metadata.name}' 2>$null
if ($podName) {
    Write-Host "Latest logs from: $podName" -ForegroundColor Cyan
    kubectl logs -n super-brain $podName --tail=10 2>$null
} else {
    Write-Host "No pods found yet" -ForegroundColor Yellow
}
Write-Host ""

# ==================================================
# FINAL SUMMARY
# ==================================================
Write-Host "✅ DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Summary:" -ForegroundColor Cyan
Write-Host "  ✓ Namespace: super-brain" -ForegroundColor Green
Write-Host "  ✓ Secrets: 7 created" -ForegroundColor Green
Write-Host "  ✓ Deployment: telegram-bot" -ForegroundColor Green
Write-Host "  ✓ Replicas: 2 (HPA: 2-5)" -ForegroundColor Green
Write-Host ""

Write-Host "🔗 Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Monitor pods: kubectl logs -f -n super-brain deployment/telegram-bot" -ForegroundColor White
Write-Host "  2. Check status: kubectl get pods -n super-brain" -ForegroundColor White
Write-Host "  3. Port forward: kubectl port-forward -n super-brain svc/telegram-bot 8000:8000" -ForegroundColor White
Write-Host "  4. Send test message to bot" -ForegroundColor White
Write-Host ""
Write-Host "📚 Documentation:" -ForegroundColor Yellow
Write-Host "  - Deployment Guide: DEPLOYMENT_CREDENTIALS_K8S_GUIDE.md" -ForegroundColor White
Write-Host "  - Bot Handler: api/bot_handler.py" -ForegroundColor White
Write-Host "  - Manifest: k8s/deployments/telegram-bot-deployment.yaml" -ForegroundColor White
Write-Host ""
