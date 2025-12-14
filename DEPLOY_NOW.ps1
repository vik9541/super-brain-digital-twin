# ============================================================
#  Victor Bot v2.0 - ONE-COMMAND DEPLOY
# ============================================================

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   🚀 VICTOR BOT v2.0 - QUICK DEPLOY" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Проверка переменной окружения для registry
if (-not $env:DO_REGISTRY) {
    Write-Host "❌ Переменная DO_REGISTRY не установлена!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Установи ее:" -ForegroundColor Yellow
    Write-Host '   $env:DO_REGISTRY = "registry.digitalocean.com/YOUR_REGISTRY"' -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Или запусти с параметром:" -ForegroundColor Yellow
    Write-Host '   .\deploy_victor_production.ps1 -Registry "registry.digitalocean.com/YOUR_REGISTRY"' -ForegroundColor Cyan
    Write-Host ""
    exit 1
}

$REGISTRY = $env:DO_REGISTRY

Write-Host "📋 Configuration:" -ForegroundColor Yellow
Write-Host "   Registry: $REGISTRY" -ForegroundColor White
Write-Host "   Version: 2.0.0" -ForegroundColor White
Write-Host "   Domain: victor.97v.ru" -ForegroundColor White
Write-Host ""

# Спросить подтверждение
$confirm = Read-Host "Продолжить деплой? (y/n)"
if ($confirm -ne "y") {
    Write-Host "❌ Деплой отменен" -ForegroundColor Red
    exit 0
}

Write-Host ""

# Запустить полный деплой
.\deploy_victor_production.ps1 -Registry $REGISTRY -Version "2.0.0"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "   ✅ ДЕПЛОЙ ЗАВЕРШЕН!" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Следующие шаги:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Проверь API:" -ForegroundColor White
    Write-Host "   curl https://victor.97v.ru/health" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "2. Настрой Telegram webhook:" -ForegroundColor White
    Write-Host '   .\setup_telegram_webhook.ps1 -NgrokUrl "https://victor.97v.ru"' -ForegroundColor Cyan
    Write-Host ""
    Write-Host "3. Отправь сообщение боту и смотри логи:" -ForegroundColor White
    Write-Host "   kubectl logs -f -l app=victor-bot-v2" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Red
    Write-Host "   ❌ ДЕПЛОЙ ЗАВЕРШИЛСЯ С ОШИБКОЙ" -ForegroundColor Red
    Write-Host "============================================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Проверь логи выше для деталей" -ForegroundColor Yellow
    Write-Host ""
}
