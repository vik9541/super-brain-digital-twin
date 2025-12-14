#!/usr/bin/env python3
"""
WebSocket Client для тестирования TASK-007
Подключается к защищенному WebSocket endpoint с JWT токеном
"""

import asyncio
import json
import os
from datetime import datetime, timedelta

import jwt

# Конфигурация (из api/main.py)
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
ALGORITHM = "HS256"
WEBSOCKET_URL = "ws://localhost:8000/ws/{token}"


def generate_test_token(user_id: str = "test_user", expires_hours: int = 1) -> str:
    """Генерация JWT токена для тестирования."""
    payload = {
        "user_id": user_id,
        "username": "test_user",
        "exp": datetime.utcnow() + timedelta(hours=expires_hours),
        "iat": datetime.utcnow(),
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    print(f"✅ JWT токен сгенерирован для user: {user_id}")
    print(f"🔑 Token: {token[:50]}...")
    return token


async def test_websocket_connection():
    """Тестирование WebSocket подключения с JWT."""
    try:
        import websockets
    except ImportError:
        print("❌ Нужно установить websockets:")
        print("   pip install websockets")
        return

    # Генерируем токен
    token = generate_test_token()
    url = WEBSOCKET_URL.format(token=token)
    
    print(f"\n🚀 Подключаемся к: {url[:50]}...")
    
    try:
        async with websockets.connect(url) as websocket:
            print("✅ WebSocket соединение установлено!")
            
            # Получаем welcome сообщение
            welcome = await websocket.recv()
            welcome_data = json.loads(welcome)
            print(f"\n📨 Welcome message:")
            print(f"   Type: {welcome_data.get('type')}")
            print(f"   User: {welcome_data.get('user_id')}")
            print(f"   Timestamp: {welcome_data.get('timestamp')}")
            
            # Отправляем тестовые сообщения
            test_messages = [
                "Hello WebSocket!",
                "Testing JWT authentication",
                "TASK-007 works! 🎉"
            ]
            
            for msg in test_messages:
                print(f"\n📤 Отправляем: {msg}")
                await websocket.send(msg)
                
                # Получаем echo
                response = await websocket.recv()
                response_data = json.loads(response)
                print(f"📥 Получен ответ:")
                print(f"   Type: {response_data.get('type')}")
                print(f"   Data: {response_data.get('data')}")
                
                await asyncio.sleep(0.5)
            
            print("\n✅ Все сообщения успешно обработаны!")
            print("🎉 TASK-007 WebSocket работает корректно!")
            
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"❌ Ошибка подключения: {e}")
        print("   Проверьте, что сервер запущен: uvicorn main:app")
    except Exception as e:
        print(f"❌ Ошибка: {e}")


async def test_invalid_token():
    """Тестирование подключения с невалидным токеном."""
    try:
        import websockets
    except ImportError:
        return
    
    print("\n\n🧪 Тест 2: Невалидный токен")
    print("=" * 50)
    
    invalid_token = "invalid.jwt.token.here"
    url = WEBSOCKET_URL.format(token=invalid_token)
    
    print(f"🚀 Пробуем подключиться с невалидным токеном...")
    
    try:
        async with websockets.connect(url) as websocket:
            # Пробуем получить сообщение
            try:
                msg = await asyncio.wait_for(websocket.recv(), timeout=2)
                print(f"❌ ОШИБКА: Получено сообщение: {msg}")
            except asyncio.TimeoutError:
                print(f"❌ ОШИБКА: Таймаут - соединение не закрылось")
    except websockets.exceptions.ConnectionClosedError as e:
        if e.code == 1008:
            print(f"✅ Соединение закрыто с кодом 1008 (Policy Violation)")
            print(f"   Причина: {e.reason}")
        else:
            print(f"⚠️ Соединение закрыто с кодом {e.code}: {e.reason}")
    except websockets.exceptions.ConnectionClosed as e:
        if e.code == 1008:
            print(f"✅ Соединение закрыто с кодом 1008 (Policy Violation)")
            print(f"   Причина: {e.reason}")
        else:
            print(f"⚠️ Соединение закрыто с кодом {e.code}: {e.reason}")
    except Exception as e:
        print(f"⚠️ Другая ошибка: {type(e).__name__}: {e}")


async def test_expired_token():
    """Тестирование подключения с истекшим токеном."""
    try:
        import websockets
    except ImportError:
        return
    
    print("\n\n🧪 Тест 3: Истекший токен")
    print("=" * 50)
    
    # Токен истек час назад
    payload = {
        "user_id": "test_user",
        "exp": datetime.utcnow() - timedelta(hours=1),
    }
    expired_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    url = WEBSOCKET_URL.format(token=expired_token)
    
    print(f"🚀 Пробуем подключиться с истекшим токеном...")
    
    try:
        async with websockets.connect(url) as websocket:
            # Пробуем получить сообщение
            try:
                msg = await asyncio.wait_for(websocket.recv(), timeout=2)
                print(f"❌ ОШИБКА: Получено сообщение: {msg}")
            except asyncio.TimeoutError:
                print(f"❌ ОШИБКА: Таймаут - соединение не закрылось")
    except websockets.exceptions.ConnectionClosedError as e:
        if e.code == 1008:
            print(f"✅ Истекший токен: соединение закрыто с кодом 1008")
            print(f"   Причина: {e.reason}")
        else:
            print(f"⚠️ Соединение закрыто с кодом {e.code}: {e.reason}")
    except websockets.exceptions.ConnectionClosed as e:
        if e.code == 1008:
            print(f"✅ Истекший токен: соединение закрыто с кодом 1008")
            print(f"   Причина: {e.reason}")
        else:
            print(f"⚠️ Соединение закрыто с кодом {e.code}: {e.reason}")
    except Exception as e:
        print(f"⚠️ Другая ошибка: {type(e).__name__}: {e}")


async def main():
    """Главная функция."""
    print("=" * 60)
    print("🧪 ТЕСТИРОВАНИЕ WEBSOCKET С JWT АУТЕНТИФИКАЦИЕЙ")
    print("=" * 60)
    print(f"📅 Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔗 URL: ws://localhost:8000/ws/{{token}}")
    print("=" * 60)
    
    print("\n\n🧪 Тест 1: Валидный токен")
    print("=" * 50)
    await test_websocket_connection()
    
    await test_invalid_token()
    await test_expired_token()
    
    print("\n\n" + "=" * 60)
    print("✅ ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
