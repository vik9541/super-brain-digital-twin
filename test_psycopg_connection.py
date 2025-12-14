#!/usr/bin/env python3
"""
🧪 Тест подключения psycopg3 к Supabase Pooler

Проверяет совместимость psycopg3 + Supabase PgBouncer
"""

import asyncio
import os
import sys

import psycopg
from dotenv import load_dotenv
from psycopg_pool import AsyncConnectionPool

# Windows fix для psycopg3
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def test_connection():
    """Тест базового подключения"""
    load_dotenv(".env.victor")

    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ DATABASE_URL не найден")
        return False

    print("=" * 60)
    print("   🧪 ТЕСТ PSYCOPG3 ПОДКЛЮЧЕНИЯ К SUPABASE")
    print("=" * 60)
    print()

    try:
        print("📡 Подключение к БД...")
        conn = await psycopg.AsyncConnection.connect(DATABASE_URL)

        print("✅ Подключение установлено!")
        print()

        # Простой запрос
        print("🔍 Выполнение тестового запроса...")
        async with conn.cursor() as cur:
            await cur.execute("SELECT version();")
            version = await cur.fetchone()
            print(f"✅ PostgreSQL версия: {version[0][:50]}...")

        print()

        # Проверка таблиц
        print("🔍 Проверка существующих таблиц...")
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE 'victor_%'
                ORDER BY table_name;
            """
            )
            tables = await cur.fetchall()

            if tables:
                print(f"✅ Найдено {len(tables)} Victor таблиц:")
                for table in tables:
                    print(f"   • {table[0]}")
            else:
                print("⚠️  Victor таблицы не найдены")

        await conn.close()
        print()
        print("✅ Тест завершен успешно!")
        return True

    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_connection_pool():
    """Тест connection pool"""
    load_dotenv(".env.victor")

    DATABASE_URL = os.getenv("DATABASE_URL")

    print()
    print("=" * 60)
    print("   🧪 ТЕСТ CONNECTION POOL")
    print("=" * 60)
    print()

    try:
        print("📡 Создание connection pool...")
        pool = AsyncConnectionPool(
            DATABASE_URL,
            min_size=1,
            max_size=5,
            kwargs={"options": "-c jit=off"},  # PgBouncer compatibility
        )

        await pool.open()
        print("✅ Pool создан!")

        # Получить соединение
        print("🔍 Тест получения соединения из pool...")
        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT current_database(), current_user;")
                result = await cur.fetchone()
                print(f"✅ База данных: {result[0]}")
                print(f"✅ Пользователь: {result[1]}")

        await pool.close()
        print()
        print("✅ Connection pool работает корректно!")
        return True

    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Запуск всех тестов"""
    success1 = await test_connection()
    success2 = await test_connection_pool()

    print()
    print("=" * 60)
    if success1 and success2:
        print("   ✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print("   🎉 psycopg3 совместим с Supabase Pooler!")
    else:
        print("   ❌ ТЕСТЫ НЕ ПРОЙДЕНЫ")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
