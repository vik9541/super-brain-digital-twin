#!/usr/bin/env python3
"""Проверка вебхука Victor Bot - текущее состояние"""

import requests

TOKEN = "8457627946:AAEKY9QoV4yI8A9D5u6lJflralz480uazp8"
BOT_API = f"https://api.telegram.org/bot{TOKEN}"

print("=" * 60)
print("   🔍 WEBHOOK STATUS CHECK")
print("=" * 60)

# Получить информацию о вебхуке
response = requests.get(f"{BOT_API}/getWebhookInfo")
data = response.json()

if data["ok"]:
    info = data["result"]
    print()
    print(f"📡 URL: {info.get('url', 'NOT SET')}")
    print(f"📊 Pending Updates: {info.get('pending_update_count', 0)}")
    print(f"❌ Last Error: {info.get('last_error_message', 'None')}")
    
    if info.get('last_error_message'):
        print()
        print("🔴 ПРОБЛЕМА С ВЕБХУКОМ!")
        if "500" in info['last_error_message']:
            print("   → Ожидается после деплоя `6452507` (REST API fallback fix)")
            print("   → GitHub Actions должен задеплоить исправление")
        print()
    else:
        print()
        print("✅ Вебхук работает без ошибок!")
        print()
else:
    print(f"❌ ERROR: {data}")

print("=" * 60)
print("Проверьте GitHub Actions:")
print("https://github.com/vik9541/super-brain-digital-twin/actions")
print("=" * 60)
