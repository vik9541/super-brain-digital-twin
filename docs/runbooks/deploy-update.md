# Runbook: Deploy Update

## Objective
Deploy new version of the application safely to production.

## Prerequisites
- Git access
- Server SSH access (root@97v.ru)
- 1 hour available for deployment and rollback if needed

## Steps

### 1. Pull Latest Code
```bash
ssh root@97v.ru
cd /var/www/super-brain-digital-twin
git pull origin main
```

**Expected output:** Already up to date OR changes pulled

### 2. Run Tests
```bash
pytest tests/
```

**Expected output:** All tests passed

### 3. Build Docker Image
```bash
docker build -t super-brain:v2.0 .
```

**Expected output:** Successfully built

### 4. Push to Registry
```bash
docker push registry.97v.ru/super-brain:v2.0
```

**Expected output:** Push successful

### 5. Update Deployment
```bash
kubectl set image deployment/api api=registry.97v.ru/super-brain:v2.0
```

**Expected output:** Deployment updated

### 6. Monitor Rollout
```bash
kubectl rollout status deployment/api
```

**Expected output:** deployment "api" successfully rolled out

### 7. Verify Health
```bash
curl http://97v.ru:8000/health
```

**Expected output:** {"status": "healthy"}

## Verification
- [ ] Deployment successful
- [ ] All pods running
- [ ] Health endpoint returns 200
- [ ] No error logs
- [ ] API endpoints responding

## Rollback
If deployment fails:
```bash
kubectl rollout undo deployment/api
kubectl rollout status deployment/api
```

## Duration
Approximately 30 minutes

## Troubleshooting

**Issue:** Tests failing
- Fix failing tests before deploying
- Do NOT proceed with broken tests

**Issue:** Build fails
- Check Dockerfile syntax
- Verify all dependencies installed

**Issue:** Pods not starting
```bash
kubectl logs deployment/api
kubectl describe pod <pod-name>
```

## Contact
admin@97v.ru
