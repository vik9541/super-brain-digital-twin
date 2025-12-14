"""
Тест подключения к Supabase БД для Victor Bot v2.0
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

# Загрузить .env
load_dotenv('.env.victor')

DATABASE_URL = os.getenv("DATABASE_URL")

async def test_database_connection():
    """Тест подключения к БД и проверка таблиц"""
    
    print("🔍 Проверка подключения к Supabase...")
    print(f"📡 DATABASE_URL: {DATABASE_URL[:50]}...")
    
    if not DATABASE_URL:
        print("❌ ERROR: DATABASE_URL не найден в .env")
        return False
    
    try:
        # Подключиться к БД
        print("\n⏳ Подключаюсь к базе данных...")
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Подключение установлено!")
        
        # Проверить существование таблиц Victor Bot
        print("\n🔍 Проверяю таблицы Victor Bot v2.0...")
        
        tables_query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'victor_%'
            ORDER BY table_name;
        """
        
        tables = await conn.fetch(tables_query)
        
        if not tables:
            print("❌ Таблицы Victor Bot НЕ найдены!")
            print("\n⚠️  НЕОБХОДИМО:")
            print("   1. Открыть https://app.supabase.com/project/lvixtpatqrtuwhygtpjx/sql/new")
            print("   2. Скопировать содержимое database/victor_bot_v2_schema.sql")
            print("   3. Вставить в SQL Editor и нажать RUN")
            await conn.close()
            return False
        
        print(f"✅ Найдено {len(tables)} таблиц Victor Bot:\n")
        
        expected_tables = [
            'victor_files',
            'victor_inbox', 
            'victor_observations',
            'victor_processing_queue'
        ]
        
        found_tables = [row['table_name'] for row in tables]
        
        for table_name in expected_tables:
            if table_name in found_tables:
                # Подсчитать строки
                count = await conn.fetchval(f"SELECT COUNT(*) FROM {table_name}")
                print(f"   ✅ {table_name:30} ({count} строк)")
            else:
                print(f"   ❌ {table_name:30} НЕ НАЙДЕНА")
        
        # Проверить views
        print("\n🔍 Проверяю views...")
        
        views_query = """
            SELECT table_name 
            FROM information_schema.views 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'victor_%'
            ORDER BY table_name;
        """
        
        views = await conn.fetch(views_query)
        
        if views:
            print(f"✅ Найдено {len(views)} views:\n")
            for view in views:
                print(f"   ✅ {view['table_name']}")
        
        # Тест записи
        print("\n🔍 Тестирую запись в victor_inbox...")
        
        test_id = await conn.fetchval("""
            INSERT INTO victor_inbox (
                content_type, content, processing_status,
                telegram_message_id, telegram_chat_id
            ) VALUES ($1, $2, $3, $4, $5)
            RETURNING id
        """, 'text', 'Test message from connection test', 'raw', 999999999, 1743141472)
        
        print(f"✅ Тестовая запись создана: {test_id}")
        
        # Удалить тестовую запись
        await conn.execute("DELETE FROM victor_inbox WHERE id = $1", test_id)
        print(f"✅ Тестовая запись удалена")
        
        # Закрыть соединение
        await conn.close()
        print("\n✅ Все проверки пройдены!")
        print("\n🚀 Готово к запуску: python main_victor_bot.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        print(f"\nДетали: {type(e).__name__}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("   VICTOR BOT v2.0 - DATABASE CONNECTION TEST")
    print("="*60)
    
    result = asyncio.run(test_database_connection())
    
    print("\n" + "="*60)
    
    if result:
        print("   ✅ STATUS: READY")
    else:
        print("   ❌ STATUS: NOT READY")
    
    print("="*60)
