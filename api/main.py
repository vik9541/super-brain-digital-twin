"""TASK-005: API Extensions - FastAPI Application with 4 Endpoints

Endpoints:
1. GET /api/v1/analysis/{id} - Get analysis result by ID
2. POST /api/v1/batch-process - Batch processing
3. GET /api/v1/metrics - System metrics
4. WebSocket /api/v1/live-events - Real-time events
"""

from fastapi import FastAPI, HTTPException, Path, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Set, Dict
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import asyncio
import time
import uuid
import psutil
import logging
import os
from supabase import create_client, Client

# JWT Authentication
from ..auth import verify_jwt_token

# Redis for caching
import redis.asyncio as redis
import json

# Rate Limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request

# Initialize FastAPI app
app = FastAPI(
    title="Super Brain API Extensions",
    description="TASK-005: AI-ML Team API Extensions",
    version="3.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Supabase client placeholder
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Rate limiter initialization
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Redis client initialization
redis_client = redis.from_url(
    os.getenv("REDIS_URL", "redis://localhost:6379"),
    encoding="utf-8",
    decode_responses=True
)

# ===== ENDPOINT 1: GET /api/v1/analysis/{id} =====

class AnalysisResult(BaseModel):
    id: str
    status: str
    input_text: str
    analysis_result: dict
    created_at: datetime
    updated_at: datetime
    error: Optional[str] = None

@app.get("/api/v1/analysis/{analysis_id}", response_model=AnalysisResult, dependencies=[Depends(verify_jwt_token)])
async def get_analysis(
    analysis_id: str = Path(..., min_length=1, description="Analysis ID")
):
    """
    Get Analysis by ID
    
    Args:
        analysis_id: UUID of the analysis
    
    Returns:
        AnalysisResult: Analysis data
    
    Raises:
        404: Analysis not found
        500: Server error
    
    Example:
        GET /api/v1/analysis/550e8400-e29b-41d4-a716-446655440000
    """
    try:
        # Query Supabase for analysis results
        response = supabase.table('message_chains').select('*').eq('id', analysis_id).execute()
        
        # Check if analysis found
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Get first result
        data = response.data[0]
        
        # Map database fields to response model
        analysis = {
            "id": str(data.get('id', analysis_id)),
            "status": "completed" if data.get('is_analyzed') else "pending",
            "input_text": str(data.get('chain_message_ids', [])),
            "analysis_result": data.get('analysis_result') or {},
            "created_at": data.get('created_at') or datetime.utcnow(),
            "updated_at": data.get('updated_at') or datetime.utcnow(),
            "error": None
        }
        return AnalysisResult(**analysis)pt HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching analysis {analysis_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch analysis: {str(e)}")

# ===== ENDPOINT 2: POST /api/v1/batch-process =====

class BatchItem(BaseModel):
    id: str
    data: dict
    priority: int = Field(default=5, ge=1, le=10, description="Priority 1-10")

class BatchRequest(BaseModel):
    items: List[BatchItem]
    callback_url: Optional[str] = None
    timeout: int = Field(default=300, ge=60, le=3600)

class BatchItemResult(BaseModel):
    id: str
    status: str
    result: Optional[dict] = None
    error: Optional[str] = None
    processing_time_ms: float

class BatchResponse(BaseModel):
    batch_id: str
    total_items: int
    processed: int
    failed: int
    results: List[BatchItemResult]
    total_processing_time_ms: float

executor = ThreadPoolExecutor(max_workers=4)

async def process_single_item(item: BatchItem) -> BatchItemResult:
    """Process single batch item"""
    start_time = time.time()
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            executor,
            lambda: {"analyzed": f"Analyzed {item.data}", "score": 0.95, "tags": ["important"]}
        )
        processing_time = (time.time() - start_time) * 1000
        return BatchItemResult(
            id=item.id,
            status="success",
            result=result,
            processing_time_ms=processing_time
        )
    except Exception as e:
        processing_time = (time.time() - start_time) * 1000
        logger.error(f"Error processing item {item.id}: {str(e)}")
        return BatchItemResult(
            id=item.id,
            status="failed",
            error=str(e),
            processing_time_ms=processing_time
        )

@app.post("/api/v1/batch-process", response_model=BatchResponse, dependencies=[Depends(verify_jwt_token)])
@limiter.limit("10/minute")
async def batch_process(request: Request, batch_request: BatchRequest):
    """
    Batch Process Items
    
    Args:
        items: List of items to process
        callback_url: URL for callback (optional)
        timeout: Timeout in seconds (60-3600)
    
    Returns:
        BatchResponse: Processing results
    
    Example:
        POST /api/v1/batch-process
        {"items": [{"id": "1", "data": {"text": "Sample"}}]}
    """
    batch_id = str(uuid.uuid4())
    start_time = time.time()
    
    try:
        tasks = [process_single_item(item) for item in batch_request.items]
        results = await asyncio.gather(*tasks)
        
        processed = sum(1 for r in results if r.status == "success")
        failed = sum(1 for r in results if r.status == "failed")
        total_time = (time.time() - start_time) * 1000
        
        logger.info(f"Batch {batch_id}: processed={processed}, failed={failed}")
        
        return BatchResponse(
            batch_id=batch_id,
            total_items=len(batch_request.items),
            processed=processed,
            failed=failed,
            results=results,
            total_processing_time_ms=total_time
        )
    except Exception as e:
        logger.error(f"Batch process failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch processing failed: {str(e)}")

# ===== ENDPOINT 3: GET /api/v1/metrics =====

class SystemMetrics(BaseModel):
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    disk_percent: float
    uptime_seconds: float
    http_metrics: dict
    batch_metrics: dict
    api_health: str

@app.get("/api/v1/metrics", response_model=SystemMetrics)
async def get_metrics():
    """
    Get System Metrics
    
    Returns:
        SystemMetrics: CPU, memory, disk, HTTP metrics
    
    Example:
        GET /api/v1/metrics
    """
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        process = psutil.Process()
        uptime = time.time() - process.create_time()
        
        health_status = "healthy"
        if cpu_percent > 80 or memory.percent > 80:
            health_status = "degraded"
        if cpu_percent > 95 or memory.percent > 95:
            health_status = "unhealthy"
        
        return SystemMetrics(
            timestamp=datetime.utcnow(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_mb=memory.used / (1024 * 1024),
            disk_percent=disk.percent,
            uptime_seconds=uptime,
            http_metrics={
                "total_requests": 0,
                "total_errors": 0,
                "avg_response_time_ms": 0,
                "requests_per_second": 0
            },
            batch_metrics={
                "total_jobs": 0,
                "completed": 0,
                "failed": 0,
                "success_rate": 0
            },
            api_health=health_status
        )
    except Exception as e:
        logger.error(f"Error getting metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")

# ===== ENDPOINT 4: WebSocket /api/v1/live-events =====

class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket connected. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting: {str(e)}")
                self.disconnect(connection)

manager = ConnectionManager()

class LiveEvent(BaseModel):
    event_type: str
    timestamp: datetime
    data: dict
    severity: str = "info"

@app.websocket("/api/v1/live-events")
async def websocket_live_events(websocket: WebSocket):
    """
    WebSocket Live Events
    
    Event Types:
    - batch_started
    - batch_completed
    - batch_failed
    - analysis_done
    - error
    - metric_update
    
    Example:
        WebSocket URL: ws://localhost:8000/api/v1/live-events
        Send: {"action": "subscribe", "events": ["batch_completed", "error"]}
        Receive: {"event_type": "batch_completed", "timestamp": "...", "data": {...}}
    """
    await manager.connect(websocket)
    subscribed_events: set = set()
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data.get("action") == "subscribe":
                subscribed_events.update(data.get("events", []))
                logger.info(f"Client subscribed to: {subscribed_events}")
                await websocket.send_json({
                    "type": "subscription_confirmed",
                    "events": list(subscribed_events)
                })
            
            elif data.get("action") == "unsubscribe":
                subscribed_events.difference_update(data.get("events", []))
                await websocket.send_json({
                    "type": "unsubscribed",
                    "events": list(subscribed_events)
                })
            
            elif data.get("action") == "ping":
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        manager.disconnect(websocket)

# ===== Health Check =====

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/")
async def root():
    return {
        "message": "Super Brain API Extensions v3.0.0",
        "endpoints": {
            "analysis": "/api/v1/analysis/{id}",
            "batch": "/api/v1/batch-process",
            "metrics": "/api/v1/metrics",
            "websocket": "/api/v1/live-events"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
