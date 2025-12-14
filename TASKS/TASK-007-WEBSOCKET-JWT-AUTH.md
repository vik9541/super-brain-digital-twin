# TASK-007: Защита WebSocket с JWT-аутентификацией

## 📋 Контекст
В `main.py.backup:371` WebSocket принимает любые подключения без проверки токена. Уязвимость описана в `TASK-006-BUGS-FOUND.md:256-270`. Нужно добавить JWT-аутентификацию и валидацию токена перед подключением.

## 🎯 Требования

**Файл:** `bots/personal-assistant-bot/main.py`

### Функции для добавления:

1. `verify_websocket_token(token: str) -> dict` — проверка JWT токена
2. `@app.websocket("/ws/{token}")` — защищённый WebSocket endpoint

### Зависимости:

```python
from fastapi import WebSocket, WebSocketDisconnect, status
from datetime import datetime, timedelta
import jwt
```

### Пример кода:

```python
import jwt
from datetime import datetime, timedelta

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
ALGORITHM = "HS256"

def verify_websocket_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

@app.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    # Проверить токен ДО accept
    user_data = verify_websocket_token(token)
    if not user_data:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
        return
    
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Обработка сообщения
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        print(f"Client {user_data.get('user_id')} disconnected")
```

## ✅ Acceptance Criteria

- [x] WebSocket требует token в URL: `/ws/{token}`
- [x] Токен проверяется ДО `await websocket.accept()`
- [x] Если токен невалиден → соединение закрывается с кодом 1008
- [x] Валидный токен → соединение принимается
- [x] Тесты в `tests/test_websocket.py`
- [x] Нет ошибок при `python main.py`

## 🧪 How to Test

```powershell
# 1. Запустить бот
python main.py

# 2. В другом терминале - получить токен
curl -X POST http://localhost:8000/api/auth/login -H "Content-Type: application/json" -d '{"username":"test","password":"test"}'

# 3. Скопировать токен и подключиться к WebSocket
# Использовать инструмент типа websocat или написать клиент на Python

# 4. Запустить тесты
pytest tests/test_websocket.py -v
```

## 📊 Estimate

- **Time:** 1.5h
- **Complexity:** MEDIUM

## 🔗 Related Tasks

- TASK-006: Bugs Found (source of this security issue)
- PHASE7: Deployment (WebSocket for real-time sync)

## 📝 Notes

- Используйте переменную окружения `SECRET_KEY` для production
- В dev-режиме можно использовать fallback `"dev-secret-key"`
- Не забудьте добавить `PyJWT` в `requirements.txt`
- WebSocket URL должен быть документирован в API docs

## 🎯 Priority

**HIGH** - Security vulnerability that allows unauthorized access to real-time events

## Status

**COMPLETED** - Implemented: 2025-12-14

### Implementation Summary:

✅ **Files Modified:**
- [api/main.py](../api/main.py) - Added JWT auth, WebSocket endpoint
- [requirements.api.txt](../requirements.api.txt) - Added PyJWT>=2.8.0
- [tests/test_websocket.py](../tests/test_websocket.py) - Full test coverage

✅ **Features:**
- `verify_websocket_token()` function with proper error handling
- Secure WebSocket endpoint at `/ws/{token}`
- Token validation BEFORE connection acceptance
- Comprehensive test suite (10 tests)
- Health check endpoint

✅ **Security:**
- JWT validation with ExpiredSignatureError handling
- InvalidTokenError handling
- Policy violation (1008) for invalid tokens
- No connection accepted without valid token
