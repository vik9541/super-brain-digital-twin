"""Phase 3: FastAPI Webhook Handler
Handles incoming/outgoing webhooks for Telegram bot and N8N workflows
"""

import os
import logging
from datetime import datetime
from typing import Dict, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import httpx
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8457627946:AAHUNkHo3PIsT VFgh9BRQ9TRn7Fc6eXm51k")
TELEGRAM_API_BASE = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
N8N_WEBHOOK_BASE = os.getenv("N8N_WEBHOOK_BASE", "https://lavrentev.app.n8n.cloud/webhook")

# Pydantic models
class TelegramWebhookUpdate(BaseModel):
    """Incoming webhook from Telegram"""
    message: Optional[Dict] = None
    user_id: Optional[int] = None
    chat_id: Optional[int] = None

class N8NResponse(BaseModel):
    """Response from N8N workflow"""
    chat_id: int
    response: str
    request_id: Optional[str] = None
    timestamp: Optional[str] = None

class HealthCheck(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    bot_status: str
    n8n_connected: bool

# Initialize FastAPI app
app = FastAPI(title="Digital Twin Webhook Handler", version="3.0.0")

# In-memory request queue (for production, use Redis)
request_queue: Dict[str, Dict] = {}


async def send_telegram_message(chat_id: int, text: str) -> bool:
    """Send message to Telegram user"""
    try:
        url = f"{TELEGRAM_API_BASE}/sendMessage"
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                url,
                json={"chat_id": chat_id, "text": text}
            )
            response.raise_for_status()
            logger.info(f"Message sent to chat {chat_id}")
            return True
    except Exception as e:
        logger.error(f"Failed to send Telegram message: {e}")
        return False


async def call_n8n_webhook(workflow: str, data: Dict) -> Dict:
    """Call N8N workflow webhook"""
    try:
        url = f"{N8N_WEBHOOK_BASE}/{workflow}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=data)
            response.raise_for_status()
            logger.info(f"N8N workflow '{workflow}' called successfully")
            return response.json()
    except Exception as e:
        logger.error(f"N8N webhook error for '{workflow}': {e}")
        return {"error": str(e)}


async def check_n8n_connection() -> bool:
    """Check if N8N is reachable"""
    try:
        url = f"{N8N_WEBHOOK_BASE}/health"
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            return response.status_code == 200
    except:
        return False


@app.post("/webhook/telegram")
async def telegram_webhook(update: TelegramWebhookUpdate, background_tasks: BackgroundTasks):
    """
    Endpoint 1: Receive messages from Telegram bot
    Format: {"message": "{text}", "chat_id": 123456789, "user_id": 123}
    """
    try:
        logger.info(f"Received Telegram update: {update.dict()}")
        
        # Extract message details
        message_text = update.message.get("text", "") if update.message else ""
        user_id = update.user_id or (update.message.get("from", {}).get("id") if update.message else None)
        chat_id = update.chat_id or (update.message.get("chat", {}).get("id") if update.message else None)
        
        if not message_text or not chat_id:
            raise HTTPException(status_code=400, detail="Invalid update format")
        
        # Route to appropriate N8N workflow
        workflow = "digital-twin-ask"  # Default workflow
        if message_text.startswith("/analyze"):
            workflow = "daily-analysis"
        elif message_text.startswith("/report"):
            workflow = "hourly-report"
        
        # Call N8N workflow
        workflow_data = {
            "question": message_text.replace("/ask", "", 1).strip(),
            "user_id": user_id,
            "chat_id": chat_id,
            "timestamp": datetime.now().isoformat()
        }
        
        workflow_response = await call_n8n_webhook(workflow, workflow_data)
        
        return {
            "status": "processed",
            "workflow": workflow,
            "response": workflow_response
        }
        
    except Exception as e:
        logger.error(f"Telegram webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhook/n8n/response")
async def n8n_response(data: N8NResponse):
    """
    Endpoint 2: Receive analysis results from N8N
    Route to Telegram user
    """
    try:
        logger.info(f"Received N8N response for chat {data.chat_id}")
        
        # Send response to Telegram
        success = await send_telegram_message(data.chat_id, data.response)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to send message to Telegram")
        
        return {
            "status": "sent_to_telegram",
            "chat_id": data.chat_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"N8N response handler error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health() -> HealthCheck:
    """
    Endpoint 3: API health check
    """
    n8n_connected = await check_n8n_connection()
    
    return HealthCheck(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        bot_status="active",
        n8n_connected=n8n_connected
    )


@app.get("/status")
async def status():
    """Detailed status endpoint"""
    n8n_connected = await check_n8n_connection()
    
    return {
        "api": "🟢 OK",
        "telegram_bot": "🟢 OK",
        "n8n_connection": "🟢 OK" if n8n_connected else "🔴 DOWN",
        "timestamp": datetime.now().isoformat(),
        "version": "3.0.0"
    }


@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("🚀 Webhook Handler started")
    logger.info(f"N8N Base URL: {N8N_WEBHOOK_BASE}")
    
    # Check N8N connection
    n8n_ok = await check_n8n_connection()
    if n8n_ok:
        logger.info("✅ N8N connection verified")
    else:
        logger.warning("⚠️ N8N connection failed")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("🛑 Webhook Handler shutting down")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
