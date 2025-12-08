# Administrator Guide

## Overview
Guide for system administrators to deploy, configure, and maintain the Super Brain Digital Twin system.

## Audience
- System Administrators
- DevOps Engineers
- IT Operations

## Prerequisites
- Server access (SSH: root@97v.ru)
- DigitalOcean account
- Basic Linux/Docker knowledge

## Installation

### System Requirements
- Ubuntu 20.04+
- 4GB RAM minimum
- 20GB disk space
- Docker & Docker Compose

### Installation Steps
```bash
# Clone repository
git clone https://github.com/vik9541/super-brain-digital-twin.git
cd super-brain-digital-twin

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start services
docker-compose up -d
```

## Configuration

### Environment Variables
```bash
API_KEY=your-secret-key-here
POSTGRES_URL=postgresql://user:pass@host/db
PORT=8000
HOST=0.0.0.0
```

### Database Setup
```bash
# Access server
ssh root@97v.ru

# Check PostgreSQL
systemctl status postgresql

# Create database
createdb super_brain
```

## Monitoring

### Check System Health
```bash
# API health
curl http://97v.ru:8000/health

# System metrics
curl -H "X-API-Key: YOUR_KEY" http://97v.ru:8000/api/v1/metrics

# Check logs
journalctl -u super-brain-api -f
```

### Performance Metrics
- CPU usage: Monitor via `/api/v1/metrics`
- Memory usage: Check system metrics
- API response times: Review logs

## Maintenance

### Daily Tasks
- Check system health endpoint
- Review error logs
- Monitor resource usage

### Weekly Tasks
- Database backup
- Security updates
- Performance review

### Monthly Tasks
- Full system backup
- Security audit
- Capacity planning

## Troubleshooting

### API Not Responding
```bash
# Check service status
systemctl status super-brain-api

# Restart service
systemctl restart super-brain-api

# Check logs
journalctl -u super-brain-api --since "1 hour ago"
```

### Database Connection Issues
```bash
# Check PostgreSQL
systemctl status postgresql

# Test connection
psql -h localhost -U postgres -d super_brain

# Review connection strings
cat .env | grep POSTGRES
```

### High CPU Usage
```bash
# Check running processes
top -u root

# Review API metrics
curl http://97v.ru:8000/api/v1/metrics

# Scale if needed
docker-compose up -d --scale api=3
```

## Backups

### Database Backup
```bash
#!/bin/bash
# Backup script
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump super_brain > backup_$DATE.sql
aws s3 cp backup_$DATE.sql s3://backups/
```

### Retention Policy
- Daily backups: Keep 7 days
- Weekly backups: Keep 4 weeks
- Monthly backups: Keep 12 months

## Updates

### Application Updates
```bash
# Pull latest code
git pull origin main

# Update dependencies
pip install -r requirements.txt

# Restart services
docker-compose restart
```

### Zero-Downtime Deployment
```bash
# Build new image
docker build -t super-brain:latest .

# Rolling update
docker-compose up -d --no-deps --build api

# Verify deployment
curl http://97v.ru:8000/health
```

## Security

### API Key Management
- Rotate keys quarterly
- Use strong random keys
- Store keys in secure vault
- Never commit keys to Git

### SSL/TLS
```bash
# Install certbot
apt install certbot

# Get certificate
certbot certonly --standalone -d 97v.ru

# Configure nginx for HTTPS
```

### Firewall Rules
```bash
# Allow HTTP/HTTPS
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8000/tcp

# Enable firewall
ufw enable
```

## Contact
- Email: admin@97v.ru
- GitHub: https://github.com/vik9541/super-brain-digital-twin/issues

**Last updated:** 2025-12-08  
**Version:** 1.0.0
