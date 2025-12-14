#!/usr/bin/env python3
"""
🚀 Victor Bot v2.0 - Автоматический деплой SQL схемы в Supabase

Этот скрипт автоматически загружает database/victor_bot_v2_schema.sql
напрямую в Supabase PostgreSQL через asyncpg.

Usage:
    python deploy_victor_schema.py
"""

import asyncio
import asyncpg
import os
from pathlib import Path
from dotenv import load_dotenv


async def deploy_schema():
    """Развернуть Victor Bot v2.0 schema в Supabase"""
    
    # Загрузить переменные окружения
    load_dotenv('.env.victor')
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ ERROR: DATABASE_URL not found in .env")
        return False
    
    # Путь к SQL файлу
    sql_file = Path(__file__).parent / "database" / "victor_bot_v2_schema.sql"
    
    if not sql_file.exists():
        print(f"❌ ERROR: SQL file not found: {sql_file}")
        return False
    
    print("=" * 60)
    print("   🚀 VICTOR BOT v2.0 - SCHEMA DEPLOYMENT")
    print("=" * 60)
    print()
    print(f"📄 SQL File: {sql_file.name}")
    print(f"📡 Database: {DATABASE_URL.split('@')[1].split('/')[0] if '@' in DATABASE_URL else 'unknown'}")
    print()
    
    # Прочитать SQL
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    print(f"📊 SQL Size: {len(sql_content)} bytes")
    print()
    
    try:
        print("⏳ Connecting to database...")
        conn = await asyncpg.connect(DATABASE_URL)
        
        print("✅ Connected successfully!")
        print()
        
        # Разделить на отдельные команды (по точке с запятой)
        # и выполнить последовательно
        statements = [s.strip() for s in sql_content.split(';') if s.strip()]
        
        print(f"🔧 Executing {len(statements)} SQL statements...")
        print()
        
        success_count = 0
        error_count = 0
        
        for i, statement in enumerate(statements, 1):
            try:
                # Пропустить комментарии
                if statement.startswith('--'):
                    continue
                
                # Показать первые 50 символов
                preview = statement[:50].replace('\n', ' ')
                if len(statement) > 50:
                    preview += "..."
                
                print(f"  [{i}/{len(statements)}] {preview}")
                
                await conn.execute(statement)
                success_count += 1
                
            except Exception as e:
                error_count += 1
                error_msg = str(e)
                
                # Игнорировать ошибки "уже существует"
                if "already exists" in error_msg.lower() or "duplicate" in error_msg.lower():
                    print(f"      ⚠️  Already exists (skipped)")
                    success_count += 1  # Считаем успешным
                else:
                    print(f"      ❌ ERROR: {error_msg[:100]}")
        
        await conn.close()
        
        print()
        print("=" * 60)
        print(f"   ✅ DEPLOYMENT COMPLETE")
        print("=" * 60)
        print(f"✅ Success: {success_count}/{len(statements)}")
        if error_count > 0:
            print(f"⚠️  Errors: {error_count} (may be duplicates)")
        print()
        
        # Проверить созданные таблицы
        print("🔍 Verifying tables...")
        conn = await asyncpg.connect(DATABASE_URL)
        
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'victor_%'
            ORDER BY table_name;
        """)
        
        if tables:
            print()
            print("📊 Victor Bot v2.0 Tables:")
            for row in tables:
                print(f"   ✅ {row['table_name']}")
            print()
        else:
            print("   ⚠️  No Victor tables found!")
            print()
        
        await conn.close()
        
        return True
        
    except asyncpg.InvalidPasswordError:
        print()
        print("❌ AUTHENTICATION FAILED")
        print("   Check your DATABASE_URL password")
        return False
        
    except asyncpg.PostgresError as e:
        print()
        print(f"❌ DATABASE ERROR: {e}")
        return False
        
    except Exception as e:
        print()
        print(f"❌ UNEXPECTED ERROR: {type(e).__name__}: {e}")
        return False


async def main():
    """Main entry point"""
    success = await deploy_schema()
    
    if success:
        print("=" * 60)
        print("   🎉 READY TO START!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("  1. Test connection: python test_victor_db_connection.py")
        print("  2. Start API server: python main_victor_bot.py")
        print("  3. Test endpoint: curl http://localhost:8000/api/health")
        print()
        exit(0)
    else:
        print("=" * 60)
        print("   ❌ DEPLOYMENT FAILED")
        print("=" * 60)
        print()
        print("Please check:")
        print("  1. DATABASE_URL in .env is correct")
        print("  2. You have internet connection")
        print("  3. Supabase project is active")
        print()
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
