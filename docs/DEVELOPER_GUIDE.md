# Developer Guide

## Overview
Guide for developers to extend and contribute to the Super Brain Digital Twin system.

## Audience
- Software Developers
- Backend Engineers
- Contributors

## Prerequisites
- Python 3.8+
- Git
- FastAPI knowledge
- Docker basics

## Architecture

### System Overview
```
┌──────────────┐
│   Client     │
└──────┬───────┘
       │
┌──────▼───────┐
│   FastAPI    │
│   (Port 8000)│
└──────┬───────┘
       │
┌──────▼───────┐
│  PostgreSQL  │
└──────────────┘
```

### Components
- **API Layer**: FastAPI REST endpoints
- **Auth**: API key authentication
- **Metrics**: Prometheus integration
- **Database**: PostgreSQL (optional)

## Project Structure

```
super-brain-digital-twin/
├── api/
│   ├── main.py          # FastAPI application
│   ├── auth.py          # Authentication
│   ├── endpoints/       # API endpoints
│   └── models.py        # Data models
├── tests/               # Test suite
├── k8s/                 # Kubernetes configs
├── docs/                # Documentation
├── monitoring/          # Grafana/Prometheus
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Development Setup

### Clone Repository
```bash
git clone https://github.com/vik9541/super-brain-digital-twin.git
cd super-brain-digital-twin
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Environment Setup
```bash
cp .env.example .env
# Edit .env with your settings
```

### Run Development Server
```bash
cd api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Testing

### Unit Tests
```bash
pytest tests/unit/
```

### Integration Tests
```bash
pytest tests/integration/
```

### Test Coverage
```bash
pytest --cov=api tests/
```

## API Development

### Adding New Endpoint
```python
@app.get("/api/v1/new-endpoint")
async def new_endpoint(api_key: str = Depends(verify_api_key)):
    return {"message": "Hello World"}
```

### Authentication
All `/api/v1/*` endpoints require X-API-Key header.

### Response Format
```python
{
  "status": "success",
  "data": {...},
  "timestamp": "2025-12-08T11:00:00"
}
```

## Contributing

### Code Style
- Follow PEP 8
- Use type hints
- Add docstrings
- Write tests

### PR Process
1. Fork repository
2. Create feature branch
3. Write tests
4. Submit PR
5. Code review
6. Merge

### Commit Messages
```
feat: Add new endpoint
fix: Fix authentication bug
docs: Update API documentation
test: Add unit tests
```

## See Also
- [API Documentation](API_DOCUMENTATION.md)
- [User Guide](USER_GUIDE.md)
- [Admin Guide](ADMIN_GUIDE.md)

**Last updated:** 2025-12-08
**Version:** 1.0.0
