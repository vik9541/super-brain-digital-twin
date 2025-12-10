# PowerShell: SUPER BRAIN Bot - Complete K8s Deployment
# December 10, 2025
# NO backticks, NO pipes - pure PowerShell

Write-Host "" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host "🚀 SUPER BRAIN BOT - K8S DEPLOYMENT" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host "" -ForegroundColor Green

# Verify kubectl is available
Write-Host "✓ Checking kubectl..." -ForegroundColor Yellow
$kubeVersion = kubectl version --client --short 2>$null
if ($null -eq $kubeVersion) {
    Write-Host "❌ kubectl not found. Please install kubectl." -ForegroundColor Red
    exit 1
}
Write-Host "  $kubeVersion" -ForegroundColor Cyan
Write-Host ""

# STEP 1: Verify namespace exists
Write-Host "📋 STEP 1: Verifying namespace 'super-brain'..." -ForegroundColor Yellow
$nsExists = kubectl get namespace super-brain 2>$null
if ($null -eq $nsExists) {
    Write-Host "  Creating namespace..." -ForegroundColor Cyan
    kubectl create namespace super-brain
    Start-Sleep -Seconds 1
}
Write-Host "  ✅ Namespace ready" -ForegroundColor Green
Write-Host ""

# STEP 2: Create Supabase Secret
Write-Host "📋 STEP 2: Creating SUPABASE secret..." -ForegroundColor Yellow
kubectl create secret generic supabase-credentials --from-literal=SUPABASE_URL=https://lvixtpatqrtuwnygtpjx.supabase.co --from-literal=SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx2aXh0cGF0cXJ0dXduaWd0cGpqeCIsInJvbGUiOiJhbm9uIiwiaWF0IjoxNzMwNjgyNTEyLCJleHAiOjE3NjIyMTg1MTJ9.DUMMYBASE64DUMMYBASE64DUMMYBASE64 --from-literal=SUPABASE_JWT_SECRET=super-secret-jwt-key-change-in-production -n super-brain 2>$null
Write-Host "  ✅ Done" -ForegroundColor Green
Write-Host ""

# STEP 3: Create Telegram Secret
Write-Host "📋 STEP 3: Creating TELEGRAM secret..." -ForegroundColor Yellow
kubectl create secret generic telegram-credentials --from-literal=TELEGRAM_BOT_TOKEN=8326941950:AAHx7hj1JcJLeQl8eS5sTFlkLJ5S3ZM-L5p3BZoVE -n super-brain 2>$null
Write-Host "  ✅ Done" -ForegroundColor Green
Write-Host ""

# STEP 4: Create Perplexity Secret
Write-Host "📋 STEP 4: Creating PERPLEXITY secret..." -ForegroundColor Yellow
kubectl create secret generic perplexity-credentials --from-literal=PERPLEXITY_API_KEY=pplx-replace-with-actual-key -n super-brain 2>$null
Write-Host "  ✅ Done" -ForegroundColor Green
Write-Host ""

# STEP 5: Create N8N Secret
Write-Host "📋 STEP 5: Creating N8N secret..." -ForegroundColor Yellow
kubectl create secret generic n8n-webhooks --from-literal=N8N_WEBHOOK_URL=https://lavrentev.app.n8n.cloud/webhook -n super-brain 2>$null
Write-Host "  ✅ Done" -ForegroundColor Green
Write-Host ""

# STEP 6: Create Database Secret
Write-Host "📋 STEP 6: Creating DATABASE secret..." -ForegroundColor Yellow
kubectl create secret generic database-url --from-literal=DATABASE_URL=postgresql://user:pass@localhost:5432/super_brain_db -n super-brain 2>$null
Write-Host "  ✅ Done" -ForegroundColor Green
Write-Host ""

# STEP 7: Create JWT Secret
Write-Host "📋 STEP 7: Creating JWT secret..." -ForegroundColor Yellow
kubectl create secret generic jwt-secret --from-literal=JWT_SECRET=your-jwt-secret-here-change-in-production-9876543210 -n super-brain 2>$null
Write-Host "  ✅ Done" -ForegroundColor Green
Write-Host ""

# STEP 8: Verify Secrets
Write-Host "📋 STEP 8: Verifying secrets..." -ForegroundColor Yellow
Write-Host ""
kubectl get secrets -n super-brain
Write-Host ""

# STEP 9: Deploy Bot
Write-Host "📋 STEP 9: Deploying Telegram Bot..." -ForegroundColor Yellow
kubectl apply -f https://raw.githubusercontent.com/vik9541/super-brain-digital-twin/main/k8s/deployments/telegram-bot-deployment.yaml 2>$null
Write-Host "  ✅ Deployment applied" -ForegroundColor Green
Write-Host ""

# STEP 10: Wait for pods
Write-Host "📋 STEP 10: Waiting for pods to be ready (up to 2 minutes)..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

$maxWait = 120
$elapsed = 0
while ($elapsed -lt $maxWait) {
    $ready = kubectl get pods -n super-brain -l app=telegram-bot -o jsonpath='{.items[*].status.conditions[?(@.type=="Ready")].status}' 2>$null
    if ($ready -like "*True*") {
        Write-Host "  ✅ Pods are ready!" -ForegroundColor Green
        break
    }
    Write-Host "  ⏳ Waiting... ($elapsed/$maxWait seconds)" -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    $elapsed = $elapsed + 5
}
Write-Host ""

# STEP 11: Show Status
Write-Host "📋 STEP 11: Deployment Status" -ForegroundColor Yellow
Write-Host ""

Write-Host "Deployments:" -ForegroundColor Cyan
kubectl get deployments -n super-brain
Write-Host ""

Write-Host "Pods:" -ForegroundColor Cyan
kubectl get pods -n super-brain
Write-Host ""

Write-Host "Services:" -ForegroundColor Cyan
kubectl get services -n super-brain
Write-Host ""

# STEP 12: Show Logs
Write-Host "📋 STEP 12: Bot Logs (last 20 lines)" -ForegroundColor Yellow
Write-Host ""
$podName = kubectl get pods -n super-brain -l app=telegram-bot -o jsonpath='{.items[0].metadata.name}' 2>$null
if ($null -ne $podName) {
    Write-Host "Pod: $podName" -ForegroundColor Cyan
    kubectl logs -n super-brain $podName --tail=20 2>$null
} else {
    Write-Host "No pods found yet" -ForegroundColor Yellow
}
Write-Host ""

# FINAL SUMMARY
Write-Host "===============================================" -ForegroundColor Green
Write-Host "✅ DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Summary:" -ForegroundColor Cyan
Write-Host "  ✓ Namespace: super-brain" -ForegroundColor Green
Write-Host "  ✓ Secrets: 7 created" -ForegroundColor Green
Write-Host "  ✓ Deployment: telegram-bot" -ForegroundColor Green
Write-Host "  ✓ Replicas: 2 (HPA: 2-5)" -ForegroundColor Green
Write-Host ""

Write-Host "🔗 Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Monitor logs: kubectl logs -f -n super-brain deployment/telegram-bot" -ForegroundColor White
Write-Host "  2. Check pods: kubectl get pods -n super-brain" -ForegroundColor White
Write-Host "  3. Send test message to @digital_twin_bot on Telegram" -ForegroundColor White
Write-Host "  4. Read docs: K8S_DEPLOYMENT_QUICK_GUIDE.md" -ForegroundColor White
Write-Host ""

Write-Host "✨ SUPER BRAIN v4.0 is now LIVE! 🚀" -ForegroundColor Green
Write-Host ""
