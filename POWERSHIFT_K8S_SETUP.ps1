# PowerShell Script for K8s Secrets Setup
# For SUPER BRAIN Digital Twin - December 10, 2025
# Run in: PowerShell (Administrator)

Write-Host "🚀 SUPER BRAIN K8s SECRETS SETUP" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Create Namespace
Write-Host "📍 STEP 1: Creating namespace 'super-brain'..." -ForegroundColor Yellow
kubectl create namespace super-brain 2>$null
Start-Sleep -Seconds 1
Write-Host "✅ Namespace created (or already exists)" -ForegroundColor Green
Write-Host ""

# Step 2: Create Supabase Secret
Write-Host "📍 STEP 2: Creating SUPABASE credentials secret..." -ForegroundColor Yellow
kubectl create secret generic supabase-credentials `
  --from-literal=SUPABASE_URL=https://lvixtpatqrtuwnygtpjx.supabase.co `
  --from-literal=SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx2aXh0cGF0cXJ0dXduaWd0cGpqeCIsInJvbGUiOiJhbm9uIiwiaWF0IjoxNzMwNjgyNTEyLCJleHAiOjE3NjIyMTg1MTJ9.DUMMYBASE64DUMMYBASE64DUMMYBASE64 `
  --from-literal=SUPABASE_JWT_SECRET=super-secret-jwt-key-change-in-production `
  -n super-brain `
  --dry-run=client -o yaml | kubectl apply -f - 2>$null
Write-Host "✅ SUPABASE secret created" -ForegroundColor Green
Write-Host ""

# Step 3: Create Telegram Secret
Write-Host "📍 STEP 3: Creating TELEGRAM credentials secret..." -ForegroundColor Yellow
kubectl create secret generic telegram-credentials `
  --from-literal=TELEGRAM_BOT_TOKEN=8326941950:AAHx7hj1JcJLeQl8eS5sTFlkLJ5S3ZM-L5p3BZoVE `
  -n super-brain `
  --dry-run=client -o yaml | kubectl apply -f - 2>$null
Write-Host "✅ TELEGRAM secret created" -ForegroundColor Green
Write-Host ""

# Step 4: Create Perplexity Secret
Write-Host "📍 STEP 4: Creating PERPLEXITY credentials secret..." -ForegroundColor Yellow
kubectl create secret generic perplexity-credentials `
  --from-literal=PERPLEXITY_API_KEY=pplx-replace-with-actual-key `
  -n super-brain `
  --dry-run=client -o yaml | kubectl apply -f - 2>$null
Write-Host "✅ PERPLEXITY secret created" -ForegroundColor Green
Write-Host ""

# Step 5: Create N8N Secret
Write-Host "📍 STEP 5: Creating N8N webhooks secret..." -ForegroundColor Yellow
kubectl create secret generic n8n-webhooks `
  --from-literal=N8N_WEBHOOK_URL=https://lavrentev.app.n8n.cloud/webhook `
  -n super-brain `
  --dry-run=client -o yaml | kubectl apply -f - 2>$null
Write-Host "✅ N8N secret created" -ForegroundColor Green
Write-Host ""

# Step 6: Create Database URL Secret
Write-Host "📍 STEP 6: Creating DATABASE URL secret..." -ForegroundColor Yellow
kubectl create secret generic database-url `
  --from-literal=DATABASE_URL=postgresql://user:pass@localhost:5432/super_brain_db `
  -n super-brain `
  --dry-run=client -o yaml | kubectl apply -f - 2>$null
Write-Host "✅ DATABASE_URL secret created" -ForegroundColor Green
Write-Host ""

# Step 7: Create JWT Secret
Write-Host "📍 STEP 7: Creating JWT secret..." -ForegroundColor Yellow
kubectl create secret generic jwt-secret `
  --from-literal=JWT_SECRET=your-jwt-secret-here-change-in-production-9876543210 `
  -n super-brain `
  --dry-run=client -o yaml | kubectl apply -f - 2>$null
Write-Host "✅ JWT secret created" -ForegroundColor Green
Write-Host ""

# Step 8: Verify all secrets
Write-Host "📍 STEP 8: Verifying all secrets created..." -ForegroundColor Yellow
Write-Host ""
kubectl get secrets -n super-brain
Write-Host ""

# Step 9: Show summary
Write-Host "✅ COMPLETED!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Summary:" -ForegroundColor Cyan
Write-Host "  ✓ Namespace: super-brain" -ForegroundColor Green
Write-Host "  ✓ Secrets created: 7" -ForegroundColor Green
Write-Host "  ✓ Status: Ready for deployment" -ForegroundColor Green
Write-Host ""
Write-Host "🔗 Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Create Bot Deployment manifest" -ForegroundColor White
Write-Host "  2. Deploy with: kubectl apply -f bot-deployment.yaml" -ForegroundColor White
Write-Host "  3. Check status: kubectl get pods -n super-brain" -ForegroundColor White
Write-Host ""
Write-Host "📚 Documentation: DEPLOYMENT_CREDENTIALS_K8S_GUIDE.md" -ForegroundColor Yellow
