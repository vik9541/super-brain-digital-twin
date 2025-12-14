#!/usr/bin/env python3
"""
🚀 Victor Bot v2.0 - Автоматический деплой через Supabase Management API

Использует официальный Management API для выполнения SQL
Требуется Service Role Key (не anon key!)
"""

import httpx
from pathlib import Path

# ВАЖНО: Нужен SERVICE_ROLE_KEY, не anon key!
# Получить его можно здесь: https://app.supabase.com/project/lvixtpatqrtuwhygtpjx/settings/api
SUPABASE_URL = "https://lvixtpatqrtuwhygtpjx.supabase.co"
SERVICE_ROLE_KEY = "REPLACE_WITH_SERVICE_ROLE_KEY"  # ⚠️ НЕ КОММИТИТЬ!

def deploy_schema_via_api():
    """Развернуть schema через Management API"""
    
    print("=" * 60)
    print("   🚀 VICTOR BOT v2.0 - SCHEMA DEPLOYMENT (API)")
    print("=" * 60)
    print()
    
    if SERVICE_ROLE_KEY == "REPLACE_WITH_SERVICE_ROLE_KEY":
        print("❌ ERROR: SERVICE_ROLE_KEY не настроен!")
        print()
        print("Получите Service Role Key:")
        print("1. Открой: https://app.supabase.com/project/lvixtpatqrtuwhygtpjx/settings/api")
        print("2. Скопируй 'service_role' secret key")
        print("3. Установи в этот скрипт или переменную окружения SUPABASE_SERVICE_KEY")
        print()
        return False
    
    # Читаем SQL
    sql_file = Path(__file__).parent / "database" / "victor_bot_v2_schema.sql"
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    print(f"📄 SQL File: {sql_file.name}")
    print(f"📊 Size: {len(sql_content)} bytes")
    print()
    
    # Supabase Management API endpoint для SQL
    url = f"{SUPABASE_URL}/rest/v1/rpc/execute_sql"
    
    headers = {
        "apikey": SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "sql": sql_content
    }
    
    print("⏳ Executing SQL via Management API...")
    
    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                print("✅ SQL executed successfully!")
                print()
                print("Response:", response.json())
                return True
            else:
                print(f"❌ ERROR: HTTP {response.status_code}")
                print(response.text)
                return False
                
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return False

if __name__ == "__main__":
    success = deploy_schema_via_api()
    
    if not success:
        print()
        print("=" * 60)
        print("   ⚠️  ИСПОЛЬЗУЙТЕ РУЧНОЙ МЕТОД")
        print("=" * 60)
        print()
        print("1. Открой: https://app.supabase.com/project/lvixtpatqrtuwhygtpjx/sql/new")
        print("2. Скопируй database/victor_bot_v2_schema.sql")
        print("3. Вставь и нажми RUN")
        print()
