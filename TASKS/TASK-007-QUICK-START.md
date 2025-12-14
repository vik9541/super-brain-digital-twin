# TASK-007: WebSocket JWT Authentication - Quick Start

## ✅ Implementation Complete

All acceptance criteria met:
- ✅ WebSocket требует token в URL: `/ws/{token}`
- ✅ Токен проверяется ДО `await websocket.accept()`
- ✅ Если токен невалиден → соединение закрывается с кодом 1008
- ✅ Валидный токен → соединение принимается
- ✅ Тесты в `tests/test_websocket.py`
- ✅ Нет ошибок в коде

## 📂 Files Modified

1. **api/main.py** - WebSocket endpoint with JWT auth
2. **requirements.api.txt** - Added PyJWT>=2.8.0
3. **tests/test_websocket.py** - 10 comprehensive tests

## 🚀 How to Test

### 1. Install Dependencies

```powershell
cd c:\Projects\personal-assistant-bot
pip install -r requirements.api.txt
```

### 2. Run Tests

```powershell
# Run all WebSocket tests
pytest tests/test_websocket.py -v

# Run with coverage
pytest tests/test_websocket.py -v --cov=api.main --cov-report=html
```

### 3. Start API Server

```powershell
cd api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Test Manually with Python

Create `test_client.py`:

```python
import asyncio
import jwt
from datetime import datetime, timedelta
import websockets

# Generate token
SECRET_KEY = "dev-secret-key"
payload = {
    "user_id": "manual_test_user",
    "username": "tester",
    "exp": datetime.utcnow() + timedelta(hours=1)
}
token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

async def test_websocket():
    uri = f"ws://localhost:8000/ws/{token}"
    async with websockets.connect(uri) as websocket:
        # Receive welcome
        welcome = await websocket.recv()
        print(f"Welcome: {welcome}")
        
        # Send message
        await websocket.send("Hello from Python client!")
        
        # Receive response
        response = await websocket.recv()
        print(f"Response: {response}")

asyncio.run(test_websocket())
```

Run it:
```powershell
python test_client.py
```

### 5. Test Invalid Token

```python
import asyncio
import websockets

async def test_invalid():
    uri = "ws://localhost:8000/ws/invalid-token-here"
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected (should not happen)")
    except Exception as e:
        print(f"Rejected as expected: {e}")

asyncio.run(test_invalid())
```

## 🔐 Security Features

1. **Token Validation Before Accept**
   - Token verified BEFORE `websocket.accept()`
   - Invalid tokens rejected with code 1008

2. **Error Handling**
   - ExpiredSignatureError → Token expired
   - InvalidTokenError → Malformed/wrong secret
   - Proper logging for debugging

3. **Environment Variables**
   - `SECRET_KEY` from env (fallback: "dev-secret-key")
   - Production: set `SECRET_KEY` in .env

## 📊 Test Coverage

10 tests covering:
- ✅ Valid token connection
- ✅ Invalid token rejection
- ✅ Expired token rejection
- ✅ Missing token handling
- ✅ Malformed token rejection
- ✅ Multiple messages
- ✅ Function unit tests
- ✅ Health endpoint
- ✅ Performance (100 rapid messages)

## 🎯 API Endpoints

### WebSocket
- **URL:** `ws://localhost:8000/ws/{token}`
- **Auth:** JWT token in URL
- **Events:** connected, echo (extensible)

### Health Check
- **URL:** `http://localhost:8000/health`
- **Method:** GET
- **Response:** `{"status": "ok", "timestamp": "...", "service": "Super Brain API"}`

## 📝 Next Steps

1. **Generate Tokens:** Create `/api/auth/login` endpoint
2. **Event Broadcasting:** Add real-time event system
3. **Connection Manager:** Track active connections
4. **Rate Limiting:** Add per-user rate limits

## ✅ Checklist

- [x] Code implemented
- [x] Tests written
- [x] Dependencies added
- [x] Documentation created
- [ ] Manual testing performed
- [ ] Integration with auth system
- [ ] Deploy to production

## 🔗 Related

- TASK-006: Original bug report
- TASK-005: API Extensions
- PHASE7: Real-time sync
