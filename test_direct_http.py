"""
Простой тест доступа через HTTP к Supabase REST API
"""
import httpx
from dotenv import load_dotenv
import os

load_dotenv('.env.victor')

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print("=" * 60)
print("   🧪 DIRECT HTTP TEST")
print("=" * 60)
print()

# Прямой HTTP запрос к REST API
url = f"{SUPABASE_URL}/rest/v1/victor_inbox?select=*&limit=5"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
}

print(f"📡 URL: {url}")
print(f"🔑 Key: {SUPABASE_KEY[:50]}...")
print()

try:
    response = httpx.get(url, headers=headers, timeout=10.0)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ SUCCESS! Found {len(data)} rows")
        for row in data:
            print(f"  - {row.get('content_type')}: {row.get('content', '')[:50]}")
    else:
        print(f"\n❌ ERROR: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ EXCEPTION: {e}")

print()
print("💡 Если ошибка 401 - обнови RLS политики в SQL Editor")
print("💡 Если ошибка 404 - проверь что таблицы созданы")
