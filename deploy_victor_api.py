#!/usr/bin/env python3
"""
🚀 Victor Bot v2.0 - Деплой через Supabase REST API

Использует supabase-py клиент для выполнения SQL через PostgREST
"""

from pathlib import Path

from supabase import Client, create_client

# Конфигурация
SUPABASE_URL = "https://lvixtpatqrtuwhygtpjx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx2aXh0cGF0cXJ0dXdoeWd0cGp4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzM3NjQxMzQsImV4cCI6MjA0OTM0MDEzNH0.OxCRxYfIkqAzHd_Q-tLTXTI-n3Yls6MrLfJ6-RZdqrk"


def deploy_schema():
    """Развернуть schema через Supabase client"""

    print("=" * 60)
    print("   🚀 VICTOR BOT v2.0 - SCHEMA DEPLOYMENT (REST API)")
    print("=" * 60)
    print()

    # Создать Supabase клиент
    print("📡 Connecting to Supabase...")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Connected!")
    print()

    # Читаем SQL файл
    sql_file = Path(__file__).parent / "database" / "victor_bot_v2_schema.sql"
    with open(sql_file, "r", encoding="utf-8") as f:
        sql_content = f.read()

    print(f"📄 SQL File: {sql_file.name}")
    print(f"📊 Size: {len(sql_content)} bytes")
    print()

    # Выполняем через RPC (если есть функция execute_sql)
    # или создаем таблицы напрямую

    print("⚠️  ВНИМАНИЕ:")
    print("   Supabase REST API (PostgREST) НЕ поддерживает произвольный SQL!")
    print("   Нужно использовать SQL Editor вручную или Database REST API.")
    print()
    print("=" * 60)
    print("   ИНСТРУКЦИЯ ДЛЯ РУЧНОГО ДЕПЛОЯ")
    print("=" * 60)
    print()
    print("1. Открой: https://app.supabase.com/project/lvixtpatqrtuwhygtpjx/sql/new")
    print()
    print(f"2. Скопируй ВЕСЬ файл: {sql_file}")
    print()
    print("3. Вставь в SQL Editor")
    print()
    print("4. Нажми RUN (F5)")
    print()
    print("5. Должно появиться: ✅ 'Success. No rows returned'")
    print()
    print("=" * 60)
    print()
    print("После этого проверь:")
    print("  python test_victor_db_connection.py")
    print()


if __name__ == "__main__":
    deploy_schema()
