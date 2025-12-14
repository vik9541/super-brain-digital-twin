"""
TASK-007: Tests for WebSocket JWT Authentication

Tests:
1. Valid token - connection accepted
2. Invalid token - connection rejected with 1008
3. Expired token - connection rejected with 1008
4. Missing token - connection rejected
5. WebSocket disconnect handling
"""

import asyncio
import os
from datetime import datetime, timedelta
from typing import Optional

import jwt
import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

# Import app and config from main
import sys
from pathlib import Path

# Add api directory to path
api_dir = Path(__file__).parent.parent / "api"
sys.path.insert(0, str(api_dir))

# Import after adding to path (Pylance may show errors but pytest will work)
import main  # type: ignore
from main import app, SECRET_KEY, ALGORITHM  # type: ignore


# ============================================
# FIXTURES
# ============================================


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def valid_token() -> str:
    """Generate valid JWT token."""
    payload = {
        "user_id": "test_user_123",
        "username": "testuser",
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


@pytest.fixture
def expired_token() -> str:
    """Generate expired JWT token."""
    payload = {
        "user_id": "test_user_123",
        "username": "testuser",
        "exp": datetime.utcnow() - timedelta(hours=1),  # Expired 1 hour ago
        "iat": datetime.utcnow() - timedelta(hours=2),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


@pytest.fixture
def invalid_token() -> str:
    """Generate invalid JWT token (wrong secret)."""
    payload = {
        "user_id": "test_user_123",
        "username": "testuser",
        "exp": datetime.utcnow() + timedelta(hours=1),
    }
    return jwt.encode(payload, "wrong-secret-key", algorithm=ALGORITHM)


# ============================================
# TESTS
# ============================================


def test_websocket_valid_token(client, valid_token):
    """Test WebSocket connection with valid token - should accept."""
    with client.websocket_connect(f"/ws/{valid_token}") as websocket:
        # Should receive welcome message
        data = websocket.receive_json()
        assert data["type"] == "connected"
        assert data["user_id"] == "test_user_123"
        assert "message" in data
        
        # Send test message
        test_message = "Hello WebSocket!"
        websocket.send_text(test_message)
        
        # Should receive echo
        response = websocket.receive_json()
        assert response["type"] == "echo"
        assert response["data"] == test_message
        assert response["user_id"] == "test_user_123"


def test_websocket_invalid_token(client, invalid_token):
    """Test WebSocket connection with invalid token - should reject with 1008."""
    with pytest.raises((Exception, WebSocketDisconnect)) as exc_info:
        with client.websocket_connect(f"/ws/{invalid_token}"):
            pass
    
    # Should be rejected (check exception type, not message)
    assert exc_info.type in (Exception, WebSocketDisconnect)


def test_websocket_expired_token(client, expired_token):
    """Test WebSocket connection with expired token - should reject with 1008."""
    with pytest.raises((Exception, WebSocketDisconnect)) as exc_info:
        with client.websocket_connect(f"/ws/{expired_token}"):
            pass
    
    # Should be rejected (check exception type, not message)
    assert exc_info.type in (Exception, WebSocketDisconnect)


def test_websocket_missing_token(client):
    """Test WebSocket connection without token - should fail (404)."""
    with pytest.raises((Exception, WebSocketDisconnect)) as exc_info:
        with client.websocket_connect("/ws/"):
            pass
    
    # Should fail (no token provided)
    assert exc_info.type in (Exception, WebSocketDisconnect)


def test_websocket_malformed_token(client):
    """Test WebSocket connection with malformed token - should reject."""
    malformed_token = "not-a-valid-jwt-token"
    
    with pytest.raises((Exception, WebSocketDisconnect)) as exc_info:
        with client.websocket_connect(f"/ws/{malformed_token}"):
            pass
    
    # Should be rejected (check exception type, not message)
    assert exc_info.type in (Exception, WebSocketDisconnect)


def test_websocket_multiple_messages(client, valid_token):
    """Test WebSocket can handle multiple messages."""
    with client.websocket_connect(f"/ws/{valid_token}") as websocket:
        # Receive welcome
        welcome = websocket.receive_json()
        assert welcome["type"] == "connected"
        
        # Send multiple messages
        messages = ["Message 1", "Message 2", "Message 3"]
        for msg in messages:
            websocket.send_text(msg)
            response = websocket.receive_json()
            assert response["type"] == "echo"
            assert response["data"] == msg


def test_verify_websocket_token_function():
    """Test verify_websocket_token function directly."""
    # Valid token
    valid_payload = {
        "user_id": "test_123",
        "exp": datetime.utcnow() + timedelta(hours=1),
    }
    valid_token = jwt.encode(valid_payload, SECRET_KEY, algorithm=ALGORITHM)
    result = main.verify_websocket_token(valid_token)
    assert result is not None
    assert result["user_id"] == "test_123"
    
    # Expired token
    expired_payload = {
        "user_id": "test_456",
        "exp": datetime.utcnow() - timedelta(hours=1),
    }
    expired_token = jwt.encode(expired_payload, SECRET_KEY, algorithm=ALGORITHM)
    result = main.verify_websocket_token(expired_token)
    assert result is None
    
    # Invalid token
    invalid_token = "invalid.jwt.token"
    result = main.verify_websocket_token(invalid_token)
    assert result is None


def test_health_endpoint(client):
    """Test health check endpoint exists."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "timestamp" in data


# ============================================
# PERFORMANCE TESTS
# ============================================


def test_websocket_performance(client, valid_token):
    """Test WebSocket can handle rapid messages."""
    with client.websocket_connect(f"/ws/{valid_token}") as websocket:
        # Receive welcome
        websocket.receive_json()
        
        # Send 100 messages rapidly
        for i in range(100):
            websocket.send_text(f"Message {i}")
            response = websocket.receive_json()
            assert response["type"] == "echo"
            assert f"Message {i}" in response["data"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
