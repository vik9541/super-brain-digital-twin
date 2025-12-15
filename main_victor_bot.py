"""
VICTOR BOT v2.0 - Main Application
Универсальный сенсор для сбора всех данных от Виктора

Deployment: 2025-12-15 09:17 - REST API fallback fix (commit 6452507)
"""

import logging
import os
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Загрузить переменные окружения
load_dotenv(".env.victor")

# Import router
from api.victor_bot_router import router as victor_router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ============================================================================
# LIFESPAN - Startup/Shutdown Events
# ============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager для запуска background workers
    """
    logger.info("🚀 Starting Victor Bot v2.0...")

    # Запустить background worker в отдельной задаче
    # worker_task = asyncio.create_task(start_worker())
    # logger.info("✅ Background worker started")
    logger.info("⚠️  Background worker disabled (use pooler workaround)")

    yield

    # Остановить worker
    logger.info("🛑 Stopping Victor Bot v2.0...")
    # worker_task.cancel()
    # try:
    #     await worker_task
    # except asyncio.CancelledError:
    #     pass
    logger.info("✅ Shutdown complete")


# ============================================================================
# CREATE FASTAPI APP
# ============================================================================

app = FastAPI(
    title="Victor Bot v2.0 API",
    description="Универсальный сенсор для сбора всех данных от Виктора через Telegram",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router
app.include_router(victor_router)

# ============================================================================
# HEALTH CHECK ENDPOINT (for Kubernetes)
# ============================================================================


@app.get("/health")
async def health_check():
    """Health check endpoint for Kubernetes liveness/readiness probes"""
    return {"status": "ok"}


# ============================================================================
# ROOT ENDPOINT
# ============================================================================


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Victor Bot v2.0 - Universal Sensor",
        "version": "2.0.0",
        "status": "running",
        "endpoints": {
            "webhook": "POST /api/telegram/webhook",
            "clarify": "POST /api/inbox/{inbox_id}/clarify",
            "list_inbox": "GET /api/inbox",
            "health": "GET /api/health",
        },
        "features": {
            "text_processing": "✅ Enabled",
            "file_upload": "✅ Enabled",
            "ocr": "✅ Enabled",
            "transcription": "✅ Enabled (OpenAI Whisper)",
            "image_analysis": "✅ Enabled (GPT-4 Vision)",
            "face_recognition": "⏳ Planned",
            "table_extraction": "⏳ Planned",
        },
    }


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    # Get configuration
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    environment = os.getenv("ENVIRONMENT", "development")

    # Run server
    if environment == "production":
        # Production: no reload, optimized
        uvicorn.run(
            "main_victor_bot:app",
            host=host,
            port=port,
            reload=False,
            log_level="info",
            access_log=True,
        )
    else:
        # Development: with reload
        uvicorn.run("main_victor_bot:app", host=host, port=port, reload=True, log_level="info")
