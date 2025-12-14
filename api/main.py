"""TASK-005: API Extensions - FastAPI Application with 4 Endpoints

Endpoints:
1. GET /api/v1/analysis/{id} - Get analysis result by ID
2. POST /api/v1/batch-process - Batch processing
3. GET /api/v1/metrics - System metrics
4. WebSocket /api/v1/live-events - Real-time events
"""

import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

import jwt

# Redis for caching
import redis.asyncio as redis
from fastapi import (
    FastAPI,
    WebSocket,
    WebSocketDisconnect,
    status,
)

# Rate Limiting
from supabase import Client, create_client

# JWT Authentication

# Phase 9: Cache API routes

# Phase 7.2: WebSocket real-time sync

# from .workspaces.routes import router as workspaces_router  # TODO: Fix circular import


# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for clients (will be initialized in lifespan)
supabase: Optional[Client] = None
redis_client: Optional[redis.Redis] = None

# Supabase config
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# JWT Authentication config
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
ALGORITHM = "HS256"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle context manager for FastAPI application.
    Initializes external service connections on startup and cleans up on shutdown.
    """
    global supabase, redis_client

    logger.info("Starting application...")

    # Initialize Supabase client
    try:
        if SUPABASE_URL and SUPABASE_KEY:
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
            logger.info("Supabase client initialized successfully")
        else:
            logger.warning("Supabase credentials not provided - running without Supabase")
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")
        supabase = None

    # Initialize Redis client (optional)
    try:
        redis_client = redis.from_url(
            os.getenv("REDIS_URL", "redis://localhost:6379"),
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=2,
        )
        # Test connection
        await redis_client.ping()
        logger.info("Redis client initialized successfully")
    except Exception as e:
        logger.warning(f"Redis not available - {e}")
        redis_client = None

    logger.info("Application startup complete")

    yield

    # Cleanup on shutdown
    logger.info("Shutting down application...")
    if redis_client:
        await redis_client.close()
        logger.info("Redis client closed")


app = FastAPI(
    title="Super Brain API",
    description="Digital Twin API with AI capabilities",
    version="4.1",
    lifespan=lifespan,
)


# ============================================
# JWT AUTHENTICATION FOR WEBSOCKET
# ============================================


def verify_websocket_token(token: str) -> Optional[dict]:
    """
    Verify JWT token for WebSocket authentication.

    Args:
        token: JWT token string

    Returns:
        Decoded payload if valid, None if invalid/expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.info(f"Token verified for user: {payload.get('user_id')}")
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        return None


# ============================================
# WEBSOCKET ENDPOINT WITH JWT AUTH
# ============================================


@app.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    """
    Secure WebSocket endpoint with JWT authentication.

    Authentication:
        Token is passed in URL: /ws/{jwt_token}
        Token is verified BEFORE accepting connection

    Events:
        - batch_started
        - batch_completed
        - batch_failed
        - analysis_done
        - error
        - metric_update

    Example:
        ws://localhost:8000/ws/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    """
    # SECURITY: Verify token BEFORE accepting connection
    user_data = verify_websocket_token(token)

    # Accept connection first (WebSocket protocol requirement)
    await websocket.accept()

    # Then immediately close if token is invalid
    if not user_data:
        logger.warning(f"WebSocket connection rejected: invalid token")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
        return

    user_id = user_data.get("user_id", "unknown")
    logger.info(f"WebSocket connection accepted for user: {user_id}")

    try:
        # Send welcome message
        await websocket.send_json(
            {
                "type": "connected",
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "message": "WebSocket connection established",
            }
        )

        # Main event loop
        while True:
            data = await websocket.receive_text()
            logger.info(f"Received from {user_id}: {data}")

            # Echo response (replace with actual logic)
            await websocket.send_json(
                {
                    "type": "echo",
                    "timestamp": datetime.utcnow().isoformat(),
                    "data": data,
                    "user_id": user_id,
                }
            )

    except WebSocketDisconnect:
        logger.info(f"Client {user_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for {user_id}: {e}")
        try:
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR, reason="Internal error")
        except:
            pass


# ============================================
# HEALTH CHECK
# ============================================


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Super Brain API",
    }
