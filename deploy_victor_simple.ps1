# Victor Bot v2.0 - Production Deployment Script
# Simple version without emojis for PowerShell compatibility

param(
    [Parameter(Mandatory=$false)]
    [string]$Registry = "registry.digitalocean.com/digital-twin-registry",
    
    [Parameter(Mandatory=$false)]
    [string]$Version = "2.0.0",
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipBuild,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipPush
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host " VICTOR BOT v2.0 - PRODUCTION DEPLOYMENT" -ForegroundColor Cyan
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host ""

# ============================================================
# STEP 1: Build Docker Image
# ============================================================
if (-not $SkipBuild) {
    Write-Host "[1/5] Building Docker image..." -ForegroundColor Yellow
    Write-Host ""
    
    $imageName = "victor-bot:$Version"
    
    docker build -t $imageName -f Dockerfile.victor-bot .
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Docker build failed!" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "SUCCESS: Image built: $imageName" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "[1/5] Skipped (--SkipBuild)" -ForegroundColor Gray
    Write-Host ""
}

# ============================================================
# STEP 2: Tag and Push to Registry
# ============================================================
if (-not $SkipPush) {
    Write-Host "[2/5] Tagging and pushing to registry..." -ForegroundColor Yellow
    Write-Host ""
    
    $fullImageName = "$Registry/victor-bot:$Version"
    $latestImageName = "$Registry/victor-bot:latest"
    
    # Tag with version
    docker tag "victor-bot:$Version" $fullImageName
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Docker tag failed!" -ForegroundColor Red
        exit 1
    }
    
    # Tag as latest
    docker tag "victor-bot:$Version" $latestImageName
    
    Write-Host "Pushing $fullImageName ..." -ForegroundColor Cyan
    docker push $fullImageName
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Docker push failed!" -ForegroundColor Red
        Write-Host "Make sure you're logged in: doctl registry login" -ForegroundColor Yellow
        exit 1
    }
    
    Write-Host "Pushing $latestImageName ..." -ForegroundColor Cyan
    docker push $latestImageName
    
    Write-Host "SUCCESS: Images pushed to registry" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "[2/5] Skipped (--SkipPush)" -ForegroundColor Gray
    Write-Host ""
}

# ============================================================
# STEP 3: Update Kubernetes Manifests
# ============================================================
Write-Host "[3/5] Updating Kubernetes manifests..." -ForegroundColor Yellow
Write-Host ""

$deploymentFile = "k8s\victor-bot\03-deployment.yaml"
$fullImageName = "$Registry/victor-bot:$Version"

# Read and update deployment file
$content = Get-Content $deploymentFile -Raw
$content = $content -replace 'image: registry\.digitalocean\.com/[^/]+/victor-bot:[^\s]+', "image: $fullImageName"
$content | Set-Content $deploymentFile -NoNewline

Write-Host "Updated $deploymentFile with image: $fullImageName" -ForegroundColor Cyan
Write-Host ""

# ============================================================
# STEP 4: Deploy to Kubernetes
# ============================================================
Write-Host "[4/5] Deploying to Kubernetes..." -ForegroundColor Yellow
Write-Host ""

# Check kubectl connection
kubectl cluster-info | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Not connected to Kubernetes cluster!" -ForegroundColor Red
    Write-Host "Run: doctl kubernetes cluster kubeconfig save <cluster-name>" -ForegroundColor Yellow
    exit 1
}

# Apply manifests in order
$manifests = @(
    "k8s\victor-bot\01-secrets.yaml",
    "k8s\victor-bot\02-configmap.yaml",
    "k8s\victor-bot\03-deployment.yaml",
    "k8s\victor-bot\04-service.yaml",
    "k8s\victor-bot\05-ingress.yaml"
)

foreach ($manifest in $manifests) {
    Write-Host "Applying $manifest ..." -ForegroundColor Cyan
    kubectl apply -f $manifest
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to apply $manifest" -ForegroundColor Red
        exit 1
    }
}

Write-Host "SUCCESS: All manifests applied" -ForegroundColor Green
Write-Host ""

# ============================================================
# STEP 5: Wait for Rollout
# ============================================================
Write-Host "[5/5] Waiting for rollout to complete..." -ForegroundColor Yellow
Write-Host ""

kubectl rollout status deployment/victor-bot-v2 --timeout=300s
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: Rollout did not complete in time" -ForegroundColor Yellow
    Write-Host "Check status with: kubectl get pods -l app=victor-bot-v2" -ForegroundColor Cyan
} else {
    Write-Host "SUCCESS: Deployment rolled out successfully!" -ForegroundColor Green
}

Write-Host ""

# ============================================================
# Show Status
# ============================================================
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host " DEPLOYMENT STATUS" -ForegroundColor Cyan
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Pods:" -ForegroundColor Yellow
kubectl get pods -l app=victor-bot-v2

Write-Host ""
Write-Host "Service:" -ForegroundColor Yellow
kubectl get svc victor-bot-service

Write-Host ""
Write-Host "Ingress:" -ForegroundColor Yellow
kubectl get ingress victor-bot-ingress

Write-Host ""
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host " NEXT STEPS" -ForegroundColor Cyan
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Check logs:" -ForegroundColor White
Write-Host "   kubectl logs -f -l app=victor-bot-v2" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Test API:" -ForegroundColor White
Write-Host "   curl https://victor.97v.ru/health" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Setup webhook:" -ForegroundColor White
Write-Host "   .\setup_telegram_webhook.ps1 -NgrokUrl 'https://victor.97v.ru'" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Monitor SSL certificate:" -ForegroundColor White
Write-Host "   kubectl get certificate victor-bot-tls" -ForegroundColor Gray
Write-Host ""
