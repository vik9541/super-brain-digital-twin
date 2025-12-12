"""Phase 3: Message Router
Routes messages to appropriate N8N workflows and manages response queuing
"""

import asyncio
import logging
import os
import uuid
from collections import deque
from datetime import datetime
from typing import Dict, Literal, Optional

import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
N8N_WEBHOOK_BASE = os.getenv("N8N_WEBHOOK_BASE", "https://lavrentev.app.n8n.cloud/webhook")

# Workflow mapping
WORKFLOW_URLS = {
    "ask": f"{N8N_WEBHOOK_BASE}/digital-twin-ask",
    "analyze": f"{N8N_WEBHOOK_BASE}/daily-analysis",
    "report": f"{N8N_WEBHOOK_BASE}/hourly-report",
    "perplexity": f"{N8N_WEBHOOK_BASE}/digital-twin-ask",
    "daily": f"{N8N_WEBHOOK_BASE}/daily-analysis",
    "hourly": f"{N8N_WEBHOOK_BASE}/hourly-report",
}

WorkflowType = Literal["ask", "analyze", "report", "perplexity", "daily", "hourly"]


class MessageRouter:
    """Routes messages to appropriate N8N workflows"""

    def __init__(self):
        self.request_history: Dict[str, Dict] = {}
        self.pending_requests: deque = deque(maxlen=1000)

    async def route_message(self, message: dict) -> str:
        """
        Route to appropriate workflow based on content
        Returns workflow name
        """
        text = message.get("text", "").lower()

        if text.startswith("/ask"):
            return "ask"
        elif text.startswith("/analyze"):
            return "analyze"
        elif text.startswith("/report"):
            return "report"
        else:
            # Default to ask workflow for general messages
            return "ask"

    async def execute(self, message: dict) -> Dict:
        """
        Execute routing and call appropriate workflow
        """
        try:
            # Generate request ID
            request_id = str(uuid.uuid4())

            # Route message
            workflow = await self.route_message(message)

            # Prepare workflow data
            workflow_data = {
                "request_id": request_id,
                "question": message.get("text", ""),
                "user_id": message.get("user_id"),
                "chat_id": message.get("chat_id"),
                "timestamp": datetime.now().isoformat(),
            }

            # Call workflow
            logger.info(f"Routing request {request_id} to workflow '{workflow}'")
            response = await self.call_workflow(workflow, workflow_data)

            # Store in history
            self.request_history[request_id] = {
                "workflow": workflow,
                "message": message,
                "response": response,
                "timestamp": datetime.now().isoformat(),
            }

            return response

        except Exception as e:
            logger.error(f"Message routing error: {e}")
            return {"error": str(e)}

    async def call_workflow(self, workflow: str, data: Dict) -> Dict:
        """Call N8N workflow via webhook"""
        try:
            url = WORKFLOW_URLS.get(workflow)
            if not url:
                raise ValueError(f"Unknown workflow: {workflow}")

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=data)
                response.raise_for_status()
                logger.info(f"Workflow '{workflow}' executed successfully")
                return response.json()

        except httpx.TimeoutException:
            logger.error(f"Timeout calling workflow '{workflow}'")
            return {"error": "Workflow timeout"}
        except Exception as e:
            logger.error(f"Workflow execution error: {e}")
            return {"error": str(e)}

    def get_request_status(self, request_id: str) -> Optional[Dict]:
        """Get status of a specific request"""
        return self.request_history.get(request_id)

    def get_pending_count(self) -> int:
        """Get number of pending requests"""
        return len(self.pending_requests)


class ResponseQueue:
    """Manages response queue for async processing"""

    def __init__(self):
        self.queue: Dict[str, Dict] = {}
        self.timeout_seconds = 300  # 5 minutes

    async def enqueue(self, request_id: str, user_id: int, data: Dict):
        """Add request to queue"""
        self.queue[request_id] = {
            "user_id": user_id,
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "status": "pending",
        }
        logger.info(f"Request {request_id} enqueued for user {user_id}")

    async def dequeue(self, request_id: str) -> Optional[Dict]:
        """Get and remove request from queue"""
        request = self.queue.pop(request_id, None)
        if request:
            logger.info(f"Request {request_id} dequeued")
        return request

    async def get(self, request_id: str) -> Optional[Dict]:
        """Get request without removing"""
        return self.queue.get(request_id)

    async def update_status(self, request_id: str, status: str):
        """Update request status"""
        if request_id in self.queue:
            self.queue[request_id]["status"] = status
            logger.info(f"Request {request_id} status updated to {status}")

    async def cleanup_expired(self):
        """Remove expired requests"""
        now = datetime.now()
        expired = []

        for request_id, request in self.queue.items():
            timestamp = datetime.fromisoformat(request["timestamp"])
            age = (now - timestamp).total_seconds()

            if age > self.timeout_seconds:
                expired.append(request_id)

        for request_id in expired:
            del self.queue[request_id]
            logger.warning(f"Request {request_id} expired and removed")

        return len(expired)

    def get_queue_size(self) -> int:
        """Get current queue size"""
        return len(self.queue)

    def get_all_pending(self) -> Dict[str, Dict]:
        """Get all pending requests"""
        return {k: v for k, v in self.queue.items() if v["status"] == "pending"}


# Global instances
router = MessageRouter()
queue = ResponseQueue()


async def cleanup_task():
    """Background task to cleanup expired requests"""
    while True:
        await asyncio.sleep(60)  # Run every minute
        expired_count = await queue.cleanup_expired()
        if expired_count > 0:
            logger.info(f"Cleaned up {expired_count} expired requests")


def get_router() -> MessageRouter:
    """Get global router instance"""
    return router


def get_queue() -> ResponseQueue:
    """Get global queue instance"""
    return queue
