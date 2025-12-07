# TASK-005: API Extensions
## Super Brain API v3.0.0

**AI-ML Team**: Andrey M., Dmitry K., Olga K.  
**Status**: Ready for Deployment  
**Deadline**: December 12, 2025, 17:00 MSK

---

## 📋 Overview

FastAPI application with 4 core endpoints:

1. **GET** `/api/v1/analysis/{id}` - Retrieve analysis results
2. **POST** `/api/v1/batch-process` - Batch processing
3. **GET** `/api/v1/metrics` - System metrics
4. **WebSocket** `/api/v1/live-events` - Real-time events

---

## 🚀 Quick Start

### Local Development

```bash
# Install dependencies
pip install -r ../requirements.api.txt

# Run server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Access API
open http://localhost:8000
open http://localhost:8000/docs  # Swagger UI
```

### Docker Deployment

```bash
# Build image
docker build -f Dockerfile.api -t registry.digitalocean.com/digital-twin-registry/api:v3.0.0 .

# Run container
docker run -p 8000:8000 \
  -e SUPABASE_URL=your_url \
  -e SUPABASE_KEY=your_key \
  registry.digitalocean.com/digital-twin-registry/api:v3.0.0

# Push to registry
docker push registry.digitalocean.com/digital-twin-registry/api:v3.0.0
```

### Kubernetes Deployment

```bash
# Update image
kubectl set image deployment/api api=registry.digitalocean.com/digital-twin-registry/api:v3.0.0 -n production

# Check rollout status
kubectl rollout status deployment/api -n production
```

---

## 📡 API Endpoints

### 1. GET /api/v1/analysis/{id}

**Description**: Retrieve analysis result by ID

**Example**:
```bash
curl -X GET http://localhost:8000/api/v1/analysis/550e8400-e29b-41d4-a716-446655440000
```

**Response**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "input_text": "Sample text",
  "analysis_result": {"score": 0.95, "tags": ["important"]},
  "created_at": "2025-12-10T10:00:00",
  "updated_at": "2025-12-10T10:05:00"
}
```

### 2. POST /api/v1/batch-process

**Description**: Process multiple items in batch

**Example**:
```bash
curl -X POST http://localhost:8000/api/v1/batch-process \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"id": "1", "data": {"text": "Sample 1"}, "priority": 5},
      {"id": "2", "data": {"text": "Sample 2"}, "priority": 8}
    ],
    "timeout": 300
  }'
```

**Response**:
```json
{
  "batch_id": "batch-123",
  "total_items": 2,
  "processed": 2,
  "failed": 0,
  "results": [...],
  "total_processing_time_ms": 245.5
}
```

### 3. GET /api/v1/metrics

**Description**: Get system and API metrics

**Example**:
```bash
curl -X GET http://localhost:8000/api/v1/metrics
```

**Response**:
```json
{
  "timestamp": "2025-12-10T10:30:00",
  "cpu_percent": 35.2,
  "memory_percent": 42.1,
  "memory_mb": 512.3,
  "disk_percent": 65.0,
  "uptime_seconds": 3600,
  "http_metrics": {...},
  "batch_metrics": {...},
  "api_health": "healthy"
}
```

### 4. WebSocket /api/v1/live-events

**Description**: Real-time event streaming

**Example (Python)**:
```python
import asyncio
import websockets
import json

async def connect():
    uri = "ws://localhost:8000/api/v1/live-events"
    async with websockets.connect(uri) as ws:
        # Subscribe to events
        await ws.send(json.dumps({
            "action": "subscribe",
            "events": ["batch_completed", "error"]
        }))
        
        # Receive events
        async for message in ws:
            event = json.loads(message)
            print(f"Event: {event}")

asyncio.run(connect())
```

**Example (wscat)**:
```bash
npm install -g wscat
wscat -c ws://localhost:8000/api/v1/live-events

# Send: {"action": "subscribe", "events": ["batch_completed"]}
# Receive: {"type": "subscription_confirmed", "events": [...]}
```

---

## 🧪 Testing

### Run Tests

```bash
# Run all tests
pytest tests/test_api_extensions.py -v

# Run with coverage
pytest tests/test_api_extensions.py --cov=api --cov-report=html

# Run specific test
pytest tests/test_api_extensions.py::test_get_metrics -v
```

### Load Testing

```bash
# Test batch processing (100 items)
python -c "
import requests
import json

items = [{'id': f'item-{i}', 'data': {'text': f'Sample {i}'}} for i in range(100)]
response = requests.post('http://localhost:8000/api/v1/batch-process', json={'items': items})
print(f'Status: {response.status_code}')
print(f'Time: {response.json()[\"total_processing_time_ms\"]}ms')
"
```

---

## ✅ Success Criteria

- ✅ 4 endpoints implemented and tested
- ✅ Batch processing: min 3 items/sec
- ✅ WebSocket events: 95% accuracy
- ✅ Response time: <500ms for all endpoints
- ✅ No memory leaks
- ✅ WebSocket streaming working
- ✅ All tests passing

---

## 📊 Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| Response Time | <500ms | ✅ |
| Batch Throughput | >3 items/s | ✅ |
| WebSocket Accuracy | >95% | ✅ |
| Memory Usage | <512MB | ✅ |
| CPU Usage | <80% | ✅ |

---

## 🛠 Tech Stack

- **Framework**: FastAPI 0.109.0
- **Server**: Uvicorn 0.27.0
- **Database**: Supabase 2.3.4
- **Testing**: Pytest 7.4.4
- **Monitoring**: psutil 5.9.7
- **WebSocket**: websockets 12.0

---

## 📞 Support Contacts

- **ML Lead**: Andrey M. (andrey@97k.ru)
- **Backend**: Dmitry K. (dmitry@97k.ru)
- **QA**: Olga K. (olga@97k.ru)
- **Tech Lead**: Viktor (viktor@97k.ru)

---

## 📚 References

- [FastAPI WebSocket Docs](https://fastapi.tiangolo.com/advanced/websockets/)
- [Pydantic Docs](https://docs.pydantic.dev/)
- [AsyncIO Documentation](https://docs.python.org/3/library/asyncio.html)
- [Prometheus Python Client](https://prometheus.io/docs/instrumenting/clientlibs/python/)

---

**Version**: v3.0.0  
**Last Updated**: December 7, 2025
