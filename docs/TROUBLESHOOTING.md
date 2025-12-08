# Troubleshooting Guide

## Overview
Common issues and solutions for the Super Brain Digital Twin system.

## API Issues

### Connection Refused
**Symptoms:** Cannot connect to API

**Solutions:**
```bash
# Check API status
systemctl status super-brain-api

# Check if port is open
netstat -tulpn | grep 8000

# Test connection
curl http://97v.ru:8000/health
```

### 401 Unauthorized
**Symptoms:** "Invalid or missing API key"

**Solutions:**
1. Verify API key header:
```bash
curl -H "X-API-Key: YOUR_KEY" http://97v.ru:8000/api/v1/twins
```
2. Check key in environment
3. Request new key from admin

### 429 Too Many Requests
**Symptoms:** Rate limit exceeded

**Solutions:**
- Wait 60 seconds
- Reduce request frequency
- Implement exponential backoff
- Contact admin for higher limits

### 500 Internal Server Error
**Symptoms:** Server errors

**Solutions:**
```bash
# Check logs
journalctl -u super-brain-api --since "1 hour ago"

# Check system resources
curl http://97v.ru:8000/api/v1/metrics

# Restart service if needed
systemctl restart super-brain-api
```

## Database Issues

### Connection Timeout
**Symptoms:** Database timeouts

**Solutions:**
```bash
# Check PostgreSQL status
systemctl status postgresql

# Test connection
psql -h localhost -U postgres

# Check connection string
cat .env | grep POSTGRES_URL
```

### Disk Space Full
**Symptoms:** "No space left on device"

**Solutions:**
```bash
# Check disk usage
df -h

# Clean old logs
rm -rf /var/log/old/*

# Archive old data
pg_dump old_data > archive.sql
```

## Performance Issues

### High CPU Usage
**Symptoms:** CPU > 90%

**Solutions:**
```bash
# Check processes
top -u root

# Review metrics
curl http://97v.ru:8000/api/v1/metrics

# Scale if needed
docker-compose up -d --scale api=3
```

### Slow API Response
**Symptoms:** Requests taking > 5 seconds

**Solutions:**
1. Check system load
2. Review database queries
3. Check network connectivity
4. Scale horizontally

## Kubernetes Issues

### Pod CrashLoopBackOff
**Symptoms:** Pod keeps restarting

**Solutions:**
```bash
# Check logs
kubectl logs pod-name

# Describe pod
kubectl describe pod pod-name

# Check events
kubectl get events
```

### ImagePullBackOff
**Symptoms:** Cannot pull Docker image

**Solutions:**
```bash
# Check image name
kubectl describe pod pod-name

# Verify registry access
docker pull image-name

# Check secrets
kubectl get secrets
```

## When to Escalate

Escalate to on-call team if:
- Multiple service failures
- Data corruption detected
- Security breach suspected
- Unable to diagnose within 30 minutes

**Contact:** admin@97v.ru

## Common Error Codes

| Code | Meaning | Solution |
|------|---------|----------|
| 400 | Bad Request | Check request format |
| 401 | Unauthorized | Verify API key |
| 404 | Not Found | Check endpoint URL |
| 429 | Rate Limited | Wait and retry |
| 500 | Server Error | Check logs, restart |
| 503 | Unavailable | Service is down |

## Diagnostic Commands

```bash
# Quick health check
curl http://97v.ru:8000/health

# Full system check
curl -H "X-API-Key: KEY" http://97v.ru:8000/api/v1/metrics

# Check logs
journalctl -u super-brain-api -f

# Test database
psql -h localhost -U postgres -c "SELECT 1"

# Check Docker containers
docker ps -a

# Check Kubernetes pods
kubectl get pods
```

## See Also
- [API Documentation](API_DOCUMENTATION.md)
- [Admin Guide](ADMIN_GUIDE.md)
- [User Guide](USER_GUIDE.md)

**Last updated:** 2025-12-08  
**Version:** 1.0.0
