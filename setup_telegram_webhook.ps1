# ============================================================
#  Victor Bot v2.0 - Быстрая настройка Telegram Webhook
# ============================================================

param(
    [Parameter(Mandatory=$true)]
    [string]$NgrokUrl  # например: https://abc123.ngrok.io
)

$BOT_TOKEN = "8457627946:AAEKY9QoV4yI8A9D5u6lJflralz480uazp8"
$WEBHOOK_PATH = "/api/telegram/webhook"
$FULL_URL = "$NgrokUrl$WEBHOOK_PATH"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   🤖 VICTOR BOT v2.0 - WEBHOOK SETUP" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Удалить старый webhook
Write-Host "🗑️  Удаляем старый webhook..." -ForegroundColor Yellow
try {
    $deleteResult = Invoke-RestMethod "https://api.telegram.org/bot$BOT_TOKEN/deleteWebhook"
    if ($deleteResult.ok) {
        Write-Host "✅ Старый webhook удален" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  Ошибка при удалении: $_" -ForegroundColor Yellow
}

Write-Host ""

# 2. Установить новый webhook
Write-Host "🔗 Устанавливаем webhook на: $FULL_URL" -ForegroundColor Yellow
try {
    $setResult = Invoke-RestMethod "https://api.telegram.org/bot$BOT_TOKEN/setWebhook?url=$FULL_URL"
    
    if ($setResult.ok) {
        Write-Host "✅ Webhook установлен успешно!" -ForegroundColor Green
    } else {
        Write-Host "❌ ОШИБКА: $($setResult.description)" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ ОШИБКА: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# 3. Проверить webhook
Write-Host "🔍 Проверяем webhook..." -ForegroundColor Yellow
Start-Sleep -Seconds 1

try {
    $info = Invoke-RestMethod "https://api.telegram.org/bot$BOT_TOKEN/getWebhookInfo"
    
    Write-Host ""
    Write-Host "📊 WEBHOOK INFO:" -ForegroundColor Cyan
    Write-Host "   URL: $($info.result.url)" -ForegroundColor White
    Write-Host "   Has Custom Certificate: $($info.result.has_custom_certificate)" -ForegroundColor White
    Write-Host "   Pending Update Count: $($info.result.pending_update_count)" -ForegroundColor White
    
    if ($info.result.last_error_date) {
        Write-Host "   ⚠️  Last Error: $($info.result.last_error_message)" -ForegroundColor Yellow
        Write-Host "   Error Date: $(Get-Date -UnixTimeSeconds $info.result.last_error_date)" -ForegroundColor Yellow
    } else {
        Write-Host "   ✅ No errors" -ForegroundColor Green
    }
    
} catch {
    Write-Host "❌ Не удалось получить информацию: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   🎉 ГОТОВО!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Теперь отправь сообщение боту в Telegram:" -ForegroundColor Yellow
Write-Host "   @YourBotName" -ForegroundColor Cyan
Write-Host ""
Write-Host "Смотри логи в терминале с запущенным сервером!" -ForegroundColor Yellow
Write-Host ""
