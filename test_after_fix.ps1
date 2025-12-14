#!/usr/bin/env pwsh
# Final test after DB pool fix

$token = "8457627946:AAEKY9QoV4yI8A9D5u6lJflralz480uazp8"

Write-Host "`n" -NoNewline
Write-Host "===============================================" -ForegroundColor Green
Write-Host " ФИНАЛЬНЫЙ ТЕСТ WEBHOOK (после фикса DB pool)" -ForegroundColor White
Write-Host "===============================================`n" -ForegroundColor Green

# 1. Check pod
Write-Host "[1] Статус пода:" -ForegroundColor Yellow
kubectl get pods -l app=victor-bot-v2 -o custom-columns=NAME:.metadata.name,STATUS:.status.phase,RESTARTS:.status.containerStatuses[0].restartCount,AGE:.metadata.creationTimestamp --no-headers

# 2. Check logs for "Database pool created"
Write-Host "`n[2] Проверка создания DB pool:" -ForegroundColor Yellow
$poolLog = kubectl logs deployment/victor-bot-v2 --tail=200 | Select-String "Database pool created"
if ($poolLog) {
    Write-Host "   ✅ DB pool создан!" -ForegroundColor Green
    Write-Host "   $poolLog" -ForegroundColor Gray
} else {
    Write-Host "   ⚠️ DB pool log не найден (может быть еще не создан)" -ForegroundColor Yellow
}

# 3. Test POST request
Write-Host "`n[3] Отправка тестового POST:" -ForegroundColor Yellow
$payload = '{"update_id":999999998,"message":{"message_id":999,"from":{"id":1743141472,"first_name":"Test"},"chat":{"id":1743141472,"type":"private"},"date":1734200400,"text":"TEST_AFTER_FIX"}}'

$response = curl.exe -X POST https://victor.97v.ru/api/telegram/webhook `
    -H "Content-Type: application/json" `
    -d $payload `
    -w "`nHTTP_CODE:%{http_code}" `
    -s

if ($response -match "HTTP_CODE:200") {
    Write-Host "   ✅ POST успешен! Код: 200" -ForegroundColor Green
} elseif ($response -match "HTTP_CODE:500") {
    Write-Host "   ❌ Ошибка 500 (DB pool не работает)" -ForegroundColor Red
} else {
    Write-Host "   ⚠️ Неожиданный ответ:" -ForegroundColor Yellow
    Write-Host "   $response" -ForegroundColor Gray
}

# 4. Check logs for POST
Write-Host "`n[4] Проверка логов после POST:" -ForegroundColor Yellow
Start-Sleep -Seconds 1
$postLog = kubectl logs deployment/victor-bot-v2 --tail=10 | Select-String "POST.*webhook"
if ($postLog) {
    Write-Host "   ✅ POST запрос обработан:" -ForegroundColor Green
    $postLog | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }
} else {
    Write-Host "   ⚠️ POST не найден в логах" -ForegroundColor Yellow
}

# 5. Final message
Write-Host "`n===============================================" -ForegroundColor Green
Write-Host "`n💡 СЛЕДУЮЩИЙ ШАГ:" -ForegroundColor Cyan
Write-Host "   Отправьте сообщение боту: @astra_VIK_bot" -ForegroundColor White
Write-Host "   Например: /start" -ForegroundColor White
Write-Host "`n   Затем проверьте:" -ForegroundColor Gray
Write-Host "   kubectl logs deployment/victor-bot-v2 --tail=20" -ForegroundColor Gray
Write-Host "`n===============================================`n" -ForegroundColor Green
