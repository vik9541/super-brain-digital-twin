# User Guide

## Overview
This guide helps you get started with the Super Brain Digital Twin system.

## Audience
- End Users
- Business Analysts
- Operations Teams

## Prerequisites
- API Key from administrator
- Internet connection
- curl or API client

## Getting Started

### Get API Key
Contact administrator for your API key.
Default dev key: `super-secret-key-change-me`

### Test Connection
```bash
curl http://97v.ru:8000/health
```

### First Request
```bash
curl -H "X-API-Key: YOUR_KEY" http://97v.ru:8000/api/v1/twins
```

## Features

### Digital Twin Management
List and monitor digital twins.
```bash
curl -H "X-API-Key: YOUR_KEY" http://97v.ru:8000/api/v1/twins
```

### Data Analysis
Get analysis results.
```bash
curl -H "X-API-Key: YOUR_KEY" http://97v.ru:8000/api/v1/analysis/twin-001
```

### Batch Processing
Process multiple items.
```bash
curl -X POST -H "X-API-Key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"items": ["item1", "item2"]}' \
  http://97v.ru:8000/api/v1/batch-process
```

## FAQ

**Q: How to get started?**
A: Get API key, test connection, make first request.

**Q: Rate limits?**
A: 100 requests/minute for most endpoints.

**Q: 401 error?**
A: Check API key in X-API-Key header.

## See Also
- [API Documentation](API_DOCUMENTATION.md)
- [Admin Guide](ADMIN_GUIDE.md)
- [Troubleshooting](TROUBLESHOOTING.md)

**Last updated:** 2025-12-08
**Version:** 1.0.0
