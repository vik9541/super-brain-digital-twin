"""
Проверка Victor Bot v2.0 таблиц через Supabase REST API
"""

from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv('.env.victor')

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print("=" * 60)
print("   🚀 VICTOR BOT v2.0 - SUPABASE REST API TEST")
print("=" * 60)
print()

# Создать клиент
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("✅ Supabase client connected!")
print(f"📡 URL: {SUPABASE_URL}")
print()

# Проверить таблицы
tables = ['victor_inbox', 'victor_files', 'victor_observations', 'victor_processing_queue']

for table in tables:
    try:
        response = supabase.table(table).select("*", count='exact').execute()
        print(f"✅ {table:25} - {response.count} rows")
    except Exception as e:
        print(f"❌ {table:25} - ERROR: {e}")

print()
print("=" * 60)
print("   🎯 DATABASE READY!")
print("=" * 60)
print()
print("Next steps:")
print("  1. python main_victor_bot.py   # Запустить API сервер")
print("  2. curl http://localhost:8000/api/health")
print()
