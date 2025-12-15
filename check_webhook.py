#!/usr/bin/env python3
"""Проверка настроек вебхука Victor Bot"""

import requests

TOKEN = "8457627946:AAEKY9QoV4yI8A9D5u6lJflralz480uazp8"
BOT_API = f"https://api.telegram.org/bot{TOKEN}"

print("=" * 60)
print("   🔍 WEBHOOK INFO CHECK")
print("=" * 60)

# Получить информацию о вебхуке
response = requests.get(f"{BOT_API}/getWebhookInfo")
data = response.json()

if data["ok"]:
    info = data["result"]
    print()
    print(f"📡 URL: {info.get('url', 'NOT SET')}")
    print(f"✅ Has Custom Certificate: {info.get('has_custom_certificate', False)}")
    print(f"📊 Pending Updates: {info.get('pending_update_count', 0)}")
    print(f"⏰ Last Error Date: {info.get('last_error_date', 'None')}")
    print(f"❌ Last Error: {info.get('last_error_message', 'None')}")
    print(f"🔢 Max Connections: {info.get('max_connections', 40)}")
    print()
    
    if not info.get('url'):
        print("⚠️  WEBHOOK NOT SET!")
        print()
        print("Нужно установить:")
        print(f"  {BOT_API}/setWebhook?url=https://victor.97v.ru/api/telegram/webhook")
        print()
    elif "victor.97v.ru" not in info.get('url', ''):
        print(f"⚠️  WRONG URL: {info['url']}")
        print()
        print("Должен быть: https://victor.97v.ru/api/telegram/webhook")
        print()
    else:
        print("✅ Webhook URL correct!")
        print()
        
        if info.get('last_error_message'):
            print("⚠️  Есть ошибки при доставке:")
            print(f"   {info['last_error_message']}")
            print()
else:
    print(f"❌ ERROR: {data}")
