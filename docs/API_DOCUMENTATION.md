# REST API Documentation

## Overview
This document provides comprehensive documentation for the Super Brain Digital Twin API - a FastAPI-based REST service that powers the digital twin system.

## Audience
- API Developers
- Integration Engineers
- DevOps Teams
- System Administrators

## Prerequisites
- API Key (X-API-Key header)
- HTTPS connection recommended
- JSON request/response format

## Table of Contents
1. [Authentication](#authentication)
2. [Base URL](#base-url)
3. [Endpoints](#endpoints)
4. [Error Codes](#error-codes)
5. [Rate Limiting](#rate-limiting)
6. [Examples](#examples)

---

## Authentication

### Bearer Token Format
All protected endpoints require authentication using an API key passed in the `X-API-Key` header.

**Header Format:**
```
X-API-Key: your-api-key-here
```

### How to Obtain Token
Contact your system administrator to receive an API key. Default key for development: `super-secret-key-change-me`

⚠️ **IMPORTANT**: Change the default API key in production!

### Token Expiration
API keys do not expire but can be rotated by the administrator.

### Error Responses
- **401 Unauthorized**: Invalid or missing API key
- **403 Forbidden**: Valid key but insufficient permissions

---

## Base URL

**Production:** `http://97v.ru:8000`  
**Local Development:** `http://localhost:8000`

---

## Endpoints

### 1. GET /

**Description:** Root endpoint providing API information and status.

**Authentication:** None required

**Request Format:**
```bash
curl http://97v.ru:8000/
```

**Response Example:**
```json
{
  "name": "Digital Twin API",
  "version": "2.0.0",
  "status": "running",
  "auth": "X-API-Key required for /api/v1/*",
  "metrics": "/metrics (Prometheus)"
}
```

**Error Codes:**
- None (always returns 200 OK)

**Rate Limits:** None

---

### 2. GET /health

**Description:** Health check endpoint for monitoring and load balancers.

**Authentication:** None required

**Request Format:**
```bash
curl http://97v.ru:8000/health
```

**Response Example:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-08T11:00:00.000000",
  "version": "2.0.0"
}
```

**Error Codes:**
- None (always returns 200 OK when service is running)

**Rate Limits:** None

**Example curl command:**
```bash
curl -s http://97v.ru:8000/health | jq
```

---

### 3. GET /api/v1/twins

**Description:** List all digital twins in the system.

**Authentication:** Required (X-API-Key)

**Request Format:**
```bash
curl -H "X-API-Key: your-key" http://97v.ru:8000/api/v1/twins
```

**Response Example:**
```json
{
  "twins": [
    {
      "id": "twin-001",
      "name": "Factory A",
      "status": "active"
    },
    {
      "id": "twin-002",
      "name": "Factory B",
      "status": "idle"
    }
  ]
}
```

**Error Codes:**
- **401**: Invalid or missing API key
- **500**: Internal server error

**Rate Limits:** 100 requests/minute

**Example curl command:**
```bash
curl -H "X-API-Key: super-secret-key-change-me" http://97v.ru:8000/api/v1/twins | jq
```

---

### 4. GET /api/v1/analysis/{id}

**Description:** Retrieve analysis results for a specific twin by ID.

**Authentication:** Required (X-API-Key)

**Path Parameters:**
- `id` (string): Twin identifier

**Request Format:**
```bash
curl -H "X-API-Key: your-key" http://97v.ru:8000/api/v1/analysis/{id}
```

**Response Example:**
```json
{
  "id": "analysis-123",
  "score": 0.95,
  "tags": ["important", "priority"],
  "timestamp": "2025-12-08T11:00:00"
}
```

**Error Codes:**
- **401**: Invalid or missing API key
- **404**: Analysis not found
- **500**: Internal server error

**Rate Limits:** 100 requests/minute

**Example curl command:**
```bash
curl -H "X-API-Key: super-secret-key-change-me" http://97v.ru:8000/api/v1/analysis/twin-001 | jq
```

---

### 5. POST /api/v1/batch-process

**Description:** Submit a batch of items for processing.

**Authentication:** Required (X-API-Key)

**Request Format:**
```bash
curl -X POST -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{"items": ["item1", "item2"]}' \
  http://97v.ru:8000/api/v1/batch-process
```

**Request Body:**
```json
{
  "items": ["item1", "item2", "item3"]
}
```

**Response Example:**
```json
{
  "batch_id": "batch-456",
  "processed": 3,
  "failed": 0,
  "status": "completed"
}
```

**Error Codes:**
- **400**: Invalid request body
- **401**: Invalid or missing API key
- **413**: Payload too large (max 1000 items)
- **500**: Internal server error

**Rate Limits:** 10 requests/minute

**Example curl command:**
```bash
curl -X POST -H "X-API-Key: super-secret-key-change-me" \
  -H "Content-Type: application/json" \
  -d '{"items": ["test1", "test2"]}' \
  http://97v.ru:8000/api/v1/batch-process | jq
```

---

### 6. GET /api/v1/metrics

**Description:** Retrieve system metrics including CPU, memory, and uptime.

**Authentication:** Required (X-API-Key)

**Request Format:**
```bash
curl -H "X-API-Key: your-key" http://97v.ru:8000/api/v1/metrics
```

**Response Example:**
```json
{
  "cpu_percent": 72.1,
  "memory_percent": 36.5,
  "uptime_seconds": 18
}
```

**Error Codes:**
- **401**: Invalid or missing API key
- **500**: Internal server error

**Rate Limits:** 100 requests/minute

**Example curl command:**
```bash
curl -H "X-API-Key: super-secret-key-change-me" http://97v.ru:8000/api/v1/metrics | jq
```

---

### 7. GET /metrics

**Description:** Prometheus metrics endpoint for monitoring integration.

**Authentication:** None required

**Request Format:**
```bash
curl http://97v.ru:8000/metrics
```

**Response Format:** Prometheus text format

**Example Response:**
```
# TYPE process_cpu_seconds_total counter
process_cpu_seconds_total 12.34
# TYPE process_resident_memory_bytes gauge
process_resident_memory_bytes 45678912
```

**Error Codes:**
- None (always returns 200 OK)

**Rate Limits:** None

**Example curl command:**
```bash
curl http://97v.ru:8000/metrics
```

---

## Error Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid request format or parameters |
| 401 | Unauthorized | Invalid or missing API key |
| 403 | Forbidden | Valid key but insufficient permissions |
| 404 | Not Found | Resource does not exist |
| 413 | Payload Too Large | Request body exceeds size limit |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server encountered an error |
| 503 | Service Unavailable | Service temporarily unavailable |

**Error Response Format:**
```json
{
  "detail": "Error message here",
  "status_code": 401
}
```

---

## Rate Limiting

### Limits by Endpoint

| Endpoint | Rate Limit |
|----------|------------|
| GET / | Unlimited |
| GET /health | Unlimited |
| GET /metrics | Unlimited |
| GET /api/v1/twins | 100/minute |
| GET /api/v1/analysis/{id} | 100/minute |
| POST /api/v1/batch-process | 10/minute |
| GET /api/v1/metrics | 100/minute |

### Rate Limit Headers

When rate limited, the API returns:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining in current window
- `X-RateLimit-Reset`: Time when limit resets (Unix timestamp)

### Handling Rate Limits

When you receive a `429 Too Many Requests` response:
1. Wait for the time specified in `X-RateLimit-Reset`
2. Implement exponential backoff
3. Cache responses when possible
4. Contact administrator for higher limits

---

## Authentication Flow Diagram

```
┌──────────┐                           ┌──────────┐
│  Client  │                           │   API    │
└────┬─────┘                           └────┬─────┘
     │                                      │
     │  1. Request with X-API-Key header    │
     ├─────────────────────────────────────>│
     │                                      │
     │  2. Validate API Key                 │
     │                                      ├──┐
     │                                      │  │
     │                                      │<─┘
     │                                      │
     │  3a. Return data (if valid)          │
     │<─────────────────────────────────────┤
     │                                      │
     │  3b. Return 401 (if invalid)         │
     │<─────────────────────────────────────┤
     │                                      │
```

---

## Examples

### Complete Workflow Example

```bash
#!/bin/bash

API_KEY="super-secret-key-change-me"
BASE_URL="http://97v.ru:8000"

# 1. Check API health
echo "=== Health Check ==="
curl -s $BASE_URL/health | jq

# 2. Get all twins
echo -e "\n=== List Twins ==="
curl -s -H "X-API-Key: $API_KEY" $BASE_URL/api/v1/twins | jq

# 3. Get analysis for specific twin
echo -e "\n=== Get Analysis ==="
curl -s -H "X-API-Key: $API_KEY" $BASE_URL/api/v1/analysis/twin-001 | jq

# 4. Submit batch processing
echo -e "\n=== Batch Process ==="
curl -s -X POST -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"items": ["item1", "item2", "item3"]}' \
  $BASE_URL/api/v1/batch-process | jq

# 5. Check system metrics
echo -e "\n=== System Metrics ==="
curl -s -H "X-API-Key: $API_KEY" $BASE_URL/api/v1/metrics | jq
```

### Python Example

```python
import requests

API_KEY = "super-secret-key-change-me"
BASE_URL = "http://97v.ru:8000"
headers = {"X-API-Key": API_KEY}

# Health check
response = requests.get(f"{BASE_URL}/health")
print("Health:", response.json())

# List twins
response = requests.get(f"{BASE_URL}/api/v1/twins", headers=headers)
print("Twins:", response.json())

# Batch process
data = {"items": ["item1", "item2"]}
response = requests.post(f"{BASE_URL}/api/v1/batch-process", 
                        json=data, headers=headers)
print("Batch:", response.json())
```

---

## FAQ

**Q: Where do I get an API key?**  
A: Contact your system administrator. For development, use `super-secret-key-change-me`.

**Q: Can I use the API without authentication?**  
A: Only `/`, `/health`, and `/metrics` endpoints are public. All `/api/v1/*` endpoints require authentication.

**Q: What's the maximum request size?**  
A: 10MB for most endpoints. Batch processing limited to 1000 items per request.

**Q: Is there a test environment?**  
A: Yes, run locally with `uvicorn main:app --reload` on `http://localhost:8000`.

**Q: How do I report API issues?**  
A: Create an issue on GitHub or contact support@example.com.

---

## See Also

- [User Guide](USER_GUIDE.md)
- [Administrator Guide](ADMIN_GUIDE.md)
- [Developer Guide](DEVELOPER_GUIDE.md)
- [Troubleshooting](TROUBLESHOOTING.md)

---

## Contact

For API support and questions:
- GitHub Issues: https://github.com/vik9541/super-brain-digital-twin/issues
- Email: support@97v.ru
- Documentation: http://97v.ru:8000/docs

---

**Last updated:** 2025-12-08  
**Next review:** 2025-03-08  
**Version:** 2.0.0
