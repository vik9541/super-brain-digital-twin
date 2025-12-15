#!/usr/bin/env python3
"""Установка вебхука для Victor Bot"""

import requests

TOKEN = "8457627946:AAEKY9QoV4yI8A9D5u6lJflralz480uazp8"
WEBHOOK_URL = "https://victor.97v.ru/api/telegram/webhook"
BOT_API = f"https://api.telegram.org/bot{TOKEN}"

print("=" * 60)
print("   🚀 SETTING WEBHOOK")
print("=" * 60)
print()
print(f"Bot Token: {TOKEN[:20]}...")
print(f"Webhook URL: {WEBHOOK_URL}")
print()

# Установить вебхук
response = requests.post(f"{BOT_API}/setWebhook", json={"url": WEBHOOK_URL})

data = response.json()

if data["ok"]:
    print("✅ WEBHOOK УСТАНОВЛЕН!")
    print()
    print("Проверка...")

    # Проверить
    check_response = requests.get(f"{BOT_API}/getWebhookInfo")
    check_data = check_response.json()

    if check_data["ok"]:
        info = check_data["result"]
        print(f"   📡 URL: {info.get('url')}")
        print(f"   📊 Pending: {info.get('pending_update_count', 0)}")
        print()
        print("🎉 Готово! Теперь бот будет получать сообщения.")
        print()
        print("Тестируйте: отправьте /start в @astra_VIK_bot")

else:
    print(f"❌ ОШИБКА: {data}")

print("=" * 60)
