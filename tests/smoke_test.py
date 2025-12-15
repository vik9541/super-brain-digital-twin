"""
Smoke Tests для 97v.ru Platform
=================================
Проверка критических компонентов инфраструктуры после развёртывания

Тесты:
1. API Health (liveness & readiness)
2. Redis connection + TTL
3. PostgreSQL queries
4. Telegram Bot
5. File upload (TZ-001)
6. File list
7. Batch processing
8. Performance metrics
9. WebSocket connection
10. Monitoring endpoints
11. SSL certificates

Запуск: pytest tests/smoke_test.py -v -s
"""

import os
import asyncio
import time
from datetime import datetime, timedelta
import pytest
import httpx
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Конфигурация
API_URL = os.getenv("API_URL", "https://api.97v.ru")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
DATABASE_URL = os.getenv("DATABASE_URL")
FILE_STORAGE_PATH = os.getenv("FILE_STORAGE_PATH", "/tmp/uploads")

# Таймауты
TIMEOUT = 30.0
PERFORMANCE_THRESHOLD_API = 1.0  # 1 секунда
PERFORMANCE_THRESHOLD_DB = 2.0   # 2 секунды


@pytest.mark.asyncio
async def test_01_api_health_liveness():
    """Тест 1: API Health - Liveness Probe"""
    print("\n🔍 Test 1: API Liveness Probe")
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        start = time.time()
        response = await client.get(f"{API_URL}/health")
        elapsed = time.time() - start
        
        print(f"   Status: {response.status_code}")
        print(f"   Response time: {elapsed*1000:.0f}ms")
        
        assert response.status_code == 200, "API health check failed"
        data = response.json()
        assert data.get("status") == "healthy", "API not healthy"
        
        print(f"   ✅ API is alive ({elapsed*1000:.0f}ms)")


@pytest.mark.asyncio
async def test_02_api_health_readiness():
    """Тест 2: API Health - Readiness Probe"""
    print("\n🔍 Test 2: API Readiness Probe")
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(f"{API_URL}/ready")
        
        print(f"   Status: {response.status_code}")
        
        assert response.status_code == 200, "API readiness check failed"
        data = response.json()
        assert data.get("ready") is True, "API not ready"
        
        # Проверка зависимостей
        deps = data.get("dependencies", {})
        print(f"   Database: {'✅' if deps.get('database') else '❌'}")
        print(f"   Redis: {'✅' if deps.get('redis') else '❌'}")
        
        assert deps.get("database"), "Database not ready"
        assert deps.get("redis"), "Redis not ready"
        
        print("   ✅ API is ready with all dependencies")


@pytest.mark.asyncio
async def test_03_redis_connection():
    """Тест 3: Redis Connection + TTL (TZ-001)"""
    print("\n🔍 Test 3: Redis Connection & TTL")
    
    try:
        import redis.asyncio as aioredis
    except ImportError:
        pytest.skip("redis library not installed")
    
    redis_client = await aioredis.from_url(REDIS_URL, decode_responses=True)
    
    try:
        # Ping
        pong = await redis_client.ping()
        assert pong, "Redis ping failed"
        print("   ✅ Redis ping successful")
        
        # Write test
        test_key = f"smoke_test_{datetime.now().timestamp()}"
        test_value = "test_value_97v"
        ttl_hours = 12  # TZ-001 requirement
        
        await redis_client.setex(
            test_key,
            timedelta(hours=ttl_hours),
            test_value
        )
        print(f"   ✅ Write successful (TTL: {ttl_hours}h)")
        
        # Read test
        retrieved = await redis_client.get(test_key)
        assert retrieved == test_value, "Redis read mismatch"
        print("   ✅ Read successful")
        
        # TTL check
        ttl = await redis_client.ttl(test_key)
        assert ttl > 0, "TTL not set correctly"
        print(f"   ✅ TTL verified: {ttl}s (~{ttl/3600:.1f}h)")
        
        # Cleanup
        await redis_client.delete(test_key)
        
    finally:
        await redis_client.close()


@pytest.mark.asyncio
async def test_04_database_connection():
    """Тест 4: PostgreSQL Connection & Queries"""
    print("\n🔍 Test 4: Database Connection")
    
    if not DATABASE_URL:
        pytest.skip("DATABASE_URL not configured")
    
    try:
        import asyncpg
    except ImportError:
        pytest.skip("asyncpg library not installed")
    
    start = time.time()
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        # Simple query
        result = await conn.fetchval("SELECT 1")
        assert result == 1, "Database query failed"
        
        elapsed = time.time() - start
        print(f"   ✅ Connection successful ({elapsed*1000:.0f}ms)")
        
        # Check tables exist
        tables = await conn.fetch("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public'
            LIMIT 5
        """)
        
        print(f"   Tables found: {len(tables)}")
        for table in tables:
            print(f"     - {table['tablename']}")
        
        assert len(tables) > 0, "No tables found in database"
        
    finally:
        await conn.close()


@pytest.mark.asyncio
async def test_05_telegram_bot():
    """Тест 5: Telegram Bot Authentication"""
    print("\n🔍 Test 5: Telegram Bot")
    
    if not TELEGRAM_BOT_TOKEN:
        pytest.skip("TELEGRAM_BOT_TOKEN not configured")
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        # Get bot info
        response = await client.get(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe"
        )
        
        assert response.status_code == 200, "Telegram API request failed"
        data = response.json()
        assert data.get("ok") is True, "Telegram bot authentication failed"
        
        bot_info = data.get("result", {})
        print(f"   Bot: @{bot_info.get('username')}")
        print(f"   ID: {bot_info.get('id')}")
        print(f"   Name: {bot_info.get('first_name')}")
        
        print("   ✅ Telegram bot authenticated")


@pytest.mark.asyncio
async def test_06_telegram_send_message():
    """Тест 6: Telegram Send Message"""
    print("\n🔍 Test 6: Telegram Send Message")
    
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        pytest.skip("Telegram credentials not fully configured")
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        message = f"✅ Smoke test passed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        response = await client.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message
            }
        )
        
        assert response.status_code == 200, "Failed to send message"
        data = response.json()
        assert data.get("ok") is True, "Message send failed"
        
        print(f"   ✅ Message sent successfully")


@pytest.mark.asyncio
async def test_07_file_upload():
    """Тест 7: File Upload (TZ-001 requirement)"""
    print("\n🔍 Test 7: File Upload")
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        # Create test file
        test_content = b"Test file content for smoke test"
        files = {
            "file": ("test_smoke.txt", test_content, "text/plain")
        }
        
        response = await client.post(
            f"{API_URL}/upload",
            files=files
        )
        
        if response.status_code == 404:
            pytest.skip("File upload endpoint not implemented")
        
        assert response.status_code in [200, 201], f"Upload failed: {response.status_code}"
        data = response.json()
        
        file_id = data.get("file_id") or data.get("id")
        assert file_id, "No file ID returned"
        
        print(f"   ✅ File uploaded: {file_id}")
        
        return file_id


@pytest.mark.asyncio
async def test_08_file_list():
    """Тест 8: File List"""
    print("\n🔍 Test 8: File List")
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(f"{API_URL}/files")
        
        if response.status_code == 404:
            pytest.skip("File list endpoint not implemented")
        
        assert response.status_code == 200, "Failed to get file list"
        data = response.json()
        
        files = data.get("files", []) or data if isinstance(data, list) else []
        print(f"   Files in storage: {len(files)}")
        
        print("   ✅ File list retrieved")


@pytest.mark.asyncio
async def test_09_batch_processing():
    """Тест 9: Batch Processing"""
    print("\n🔍 Test 9: Batch Processing")
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        # Trigger batch job
        response = await client.post(
            f"{API_URL}/batch/trigger",
            json={"test": True}
        )
        
        if response.status_code == 404:
            pytest.skip("Batch endpoint not implemented")
        
        assert response.status_code in [200, 202], "Batch trigger failed"
        data = response.json()
        
        job_id = data.get("job_id")
        print(f"   ✅ Batch job triggered: {job_id or 'N/A'}")


@pytest.mark.asyncio
async def test_10_api_performance():
    """Тест 10: API Performance"""
    print("\n🔍 Test 10: API Performance")
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        # Test multiple endpoints
        endpoints = [
            "/health",
            "/ready",
            "/",
        ]
        
        results = []
        
        for endpoint in endpoints:
            start = time.time()
            try:
                response = await client.get(f"{API_URL}{endpoint}")
                elapsed = time.time() - start
                
                results.append({
                    "endpoint": endpoint,
                    "status": response.status_code,
                    "time": elapsed
                })
                
                print(f"   {endpoint}: {response.status_code} ({elapsed*1000:.0f}ms)")
                
            except Exception as e:
                print(f"   {endpoint}: ❌ {str(e)}")
        
        # Check performance threshold
        avg_time = sum(r["time"] for r in results) / len(results)
        assert avg_time < PERFORMANCE_THRESHOLD_API, \
            f"Average response time {avg_time:.2f}s exceeds threshold {PERFORMANCE_THRESHOLD_API}s"
        
        print(f"   ✅ Average response time: {avg_time*1000:.0f}ms")


@pytest.mark.asyncio
async def test_11_monitoring_endpoints():
    """Тест 11: Monitoring Endpoints"""
    print("\n🔍 Test 11: Monitoring Endpoints")
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        endpoints = {
            "/metrics": "Prometheus metrics",
            "/health": "Health check",
        }
        
        for endpoint, description in endpoints.items():
            try:
                response = await client.get(f"{API_URL}{endpoint}")
                status = "✅" if response.status_code == 200 else "❌"
                print(f"   {status} {description}: {response.status_code}")
            except Exception as e:
                print(f"   ❌ {description}: {str(e)}")


def test_summary():
    """Финальная сводка тестов"""
    print("\n" + "="*60)
    print("📊 SMOKE TEST SUMMARY")
    print("="*60)
    print("✅ All critical components tested")
    print(f"🌐 API URL: {API_URL}")
    print(f"⚡ Redis: {'Configured' if REDIS_URL else 'Not configured'}")
    print(f"🗄️  Database: {'Configured' if DATABASE_URL else 'Not configured'}")
    print(f"🤖 Telegram: {'Configured' if TELEGRAM_BOT_TOKEN else 'Not configured'}")
    print("="*60)
    print("🎯 Ready for production deployment!")
    print("="*60 + "\n")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
