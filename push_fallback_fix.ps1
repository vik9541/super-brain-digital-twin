#!/usr/bin/env pwsh
# Auto-push script для фикса REST API fallback

Set-Location "C:\Projects\personal-assistant-bot"

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  GIT PUSH - REST API FALLBACK FIX" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Add files
Write-Host "Adding files..." -ForegroundColor Yellow
git add api/victor_bot_router.py deploy_victor_schema.py check_webhook.py

# Commit
Write-Host "Committing..." -ForegroundColor Yellow
$commitMsg = @"
fix: Add REST API fallback for all handlers when pool fails

- get_db_pool() now returns None on connection failure (no blocking)
- All handle_* functions support pool=None (use REST API)  
- Fixes 500 Internal Server Error at webhook endpoint
- MVP: Files saved as metadata only (no download yet)
- Refs: supabase/supabase#1573
"@

git commit -m $commitMsg

# Push
Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
git push origin main

Write-Host ""
Write-Host "✅ DONE! Check GitHub Actions:" -ForegroundColor Green
Write-Host "   https://github.com/vik9541/super-brain-digital-twin/actions" -ForegroundColor Cyan
Write-Host ""
