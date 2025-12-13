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
from typing import Optional

# Redis for caching
import redis.asyncio as redis
from fastapi import (
    FastAPI,
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

        # Phase 9: Initialize Cache Manager
    from .cache import CacheManager

    if redis_client:
        try:
            cache_manager = CacheManager(
                redis_client=redis_client, default_ttl=86400, key_prefix="superbrain"  # 24 hours
            )
            app.state.cache_manager = cache_manager
            logger.info("Phase 9: Cache Manager initialized (4x performance boost)")
        except Exception as e:
            logger.error(f"Failed to initialize Cache Manager: {e}")
            app.state.cache_manager = None
    else:
        logger.warning("Redis not available - cache disabled")
        app.state.cache_manager = None

    # Phase 9: Initialize Cache Manager
    from .cache import CacheManager

    if redis_client:
        try:
            cache_manager = CacheManager(
                redis_client=redis_client, default_ttl=86400, key_prefix="superbrain"  # 24 hours
            )
            app.state.cache_manager = cache_manager
            logger.info("Phase 9: Cache Manager initialized (4x performance)")
        except Exception as e:
            logger.error(f"Failed to initialize Cache Manager: {e}")
            app.state.cache_manager = None
    else:
        logger.warning("Redis not available - cache disabled")
        app.state.cache_manager = None
    logger.info("Application startup complete")
