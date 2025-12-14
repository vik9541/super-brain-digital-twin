# ============================================================
#  Victor Bot v2.0 - Production Deployment Script
# ============================================================
# Полный деплой Victor Bot на 97v.ru Kubernetes кластер

param(
    [Parameter(Mandatory=$false)]
    [string]$Registry = "registry.digitalocean.com/YOUR_REGISTRY",
    
    [Parameter(Mandatory=$false)]
    [string]$Version = "2.0.0",
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipBuild,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipPush
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   🚀 VICTOR BOT v2.0 - PRODUCTION DEPLOYMENT" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# ============================================================
# STEP 1: Build Docker Image
# ============================================================
if (-not $SkipBuild) {
    Write-Host "📦 STEP 1/5: Building Docker image..." -ForegroundColor Yellow
    Write-Host ""
    
    $imageName = "victor-bot:$Version"
    
    docker build -t $imageName -f Dockerfile.victor-bot .
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Docker build failed!" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ Image built: $imageName" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "⏭️  STEP 1/5: Skipped (--SkipBuild)" -ForegroundColor Gray
    Write-Host ""
}

# ============================================================
# STEP 2: Tag and Push to Registry
# ============================================================
if (-not $SkipPush) {
    Write-Host "🏷️  STEP 2/5: Tagging and pushing to registry..." -ForegroundColor Yellow
    Write-Host ""
    
    $fullImageName = "$Registry/victor-bot:$Version"
    
    Write-Host "   Tagging: $fullImageName" -ForegroundColor White
    docker tag "victor-bot:$Version" $fullImageName
    
    Write-Host "   Pushing to registry..." -ForegroundColor White
    docker push $fullImageName
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Docker push failed!" -ForegroundColor Red
        Write-Host "   Make sure you're logged in: doctl registry login" -ForegroundColor Yellow
        exit 1
    }
    
    Write-Host "✅ Image pushed: $fullImageName" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "⏭️  STEP 2/5: Skipped (--SkipPush)" -ForegroundColor Gray
    Write-Host ""
}

# ============================================================
# STEP 3: Update K8s manifests with image name
# ============================================================
Write-Host "📝 STEP 3/5: Updating Kubernetes manifests..." -ForegroundColor Yellow
Write-Host ""

$deploymentFile = "k8s\victor-bot\03-deployment.yaml"
$fullImageName = "$Registry/victor-bot:$Version"

# Читаем файл
$content = Get-Content $deploymentFile -Raw

# Заменяем placeholder на реальное имя образа
$updatedContent = $content -replace 'image: registry\.digitalocean\.com/YOUR_REGISTRY/victor-bot:.*', "image: $fullImageName"

# Сохраняем
Set-Content $deploymentFile -Value $updatedContent

Write-Host "✅ Deployment manifest updated" -ForegroundColor Green
Write-Host ""

# ============================================================
# STEP 4: Apply Kubernetes manifests
# ============================================================
Write-Host "☸️  STEP 4/5: Deploying to Kubernetes..." -ForegroundColor Yellow
Write-Host ""

# Проверяем подключение к кластеру
Write-Host "   Checking cluster connection..." -ForegroundColor White
kubectl cluster-info | Select-Object -First 1

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Cannot connect to Kubernetes cluster!" -ForegroundColor Red
    Write-Host "   Run: doctl kubernetes cluster kubeconfig save <cluster-name>" -ForegroundColor Yellow
    exit 1
}

# Применяем манифесты по порядку
$manifests = @(
    "k8s\victor-bot\01-secrets.yaml",
    "k8s\victor-bot\02-configmap.yaml",
    "k8s\victor-bot\03-deployment.yaml",
    "k8s\victor-bot\04-service.yaml",
    "k8s\victor-bot\05-ingress.yaml"
)

foreach ($manifest in $manifests) {
    Write-Host "   Applying: $manifest" -ForegroundColor White
    kubectl apply -f $manifest
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to apply: $manifest" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "✅ All manifests applied" -ForegroundColor Green
Write-Host ""

# ============================================================
# STEP 5: Wait for rollout and check status
# ============================================================
Write-Host "⏳ STEP 5/5: Waiting for deployment..." -ForegroundColor Yellow
Write-Host ""

kubectl rollout status deployment/victor-bot-v2 --timeout=300s

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Deployment failed or timeout!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Check logs:" -ForegroundColor Yellow
    Write-Host "   kubectl logs -l app=victor-bot-v2 --tail=50" -ForegroundColor Cyan
    exit 1
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   ✅ DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Показываем статус
Write-Host "📊 Deployment Status:" -ForegroundColor Cyan
Write-Host ""

Write-Host "Pods:" -ForegroundColor Yellow
kubectl get pods -l app=victor-bot-v2

Write-Host ""
Write-Host "Service:" -ForegroundColor Yellow
kubectl get service victor-bot-service

Write-Host ""
Write-Host "Ingress:" -ForegroundColor Yellow
kubectl get ingress victor-bot-ingress

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   🎯 NEXT STEPS" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Check if DNS is configured:" -ForegroundColor Yellow
Write-Host "   nslookup victor.97v.ru" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Test the API:" -ForegroundColor Yellow
Write-Host "   curl https://victor.97v.ru/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Set Telegram webhook:" -ForegroundColor Yellow
Write-Host "   .\setup_telegram_webhook.ps1 -NgrokUrl `"https://victor.97v.ru`"" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. View logs:" -ForegroundColor Yellow
Write-Host "   kubectl logs -f -l app=victor-bot-v2" -ForegroundColor Cyan
Write-Host ""
