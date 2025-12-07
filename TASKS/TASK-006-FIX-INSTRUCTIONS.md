# 🔧 TASK-006: Fix Instructions - API Deployment

**Date Created:** 7 December 2025, 18:45 MSK  
**Priority:** 🔴 P0 - CRITICAL  
**Status:** READY FOR DEPLOYMENT  
**Related:** TASK-006-BUGS-FOUND.md (BUG-001)

---

## 🎯 SUMMARY

**ROOT CAUSE:** API server deployment manifest was MISSING from k8s/ directory.

The API code exists (`api/main.py`) but was never deployed to Kubernetes cluster. This is why 97v.ru was completely unavailable.

**SOLUTION:** Created complete Kubernetes deployment manifest with:
- Deployment with 3 replicas
- LoadBalancer Service
- Health checks
- Resource limits
- Environment variables from secrets

---

## ✅ WHAT WAS FIXED

### 1. Created `k8s/api-deployment.yaml`

**File:** [`k8s/api-deployment.yaml`](https://github.com/vik9541/super-brain-digital-twin/blob/main/k8s/api-deployment.yaml)

**Contents:**
- ✅ Kubernetes Deployment with 3 replicas
- ✅ Rolling Update strategy (zero downtime)
- ✅ LoadBalancer Service (exposes on ports 80/443)
- ✅ Health probes (liveness + readiness)
- ✅ Resource requests and limits
- ✅ Supabase credentials from secrets
- ✅ Registry pull secrets

**Key Features:**
```yaml
replicas: 3                    # High availability
maxUnavailable: 0              # Zero downtime updates  
health checks: /health         # Automatic pod restart
resources: 256Mi-512Mi RAM     # Prevent OOM
LoadBalancer: ports 80/443     # Public access
```

---

## 📋 DEPLOYMENT INSTRUCTIONS

### Prerequisites

1. **Docker Image Built:**
```bash
cd /path/to/super-brain-digital-twin
docker build -f Dockerfile.api -t registry.digitalocean.com/digital-twin-registry/api:v3.0.0 .
docker push registry.digitalocean.com/digital-twin-registry/api:v3.0.0
```

2. **Kubernetes Cluster Access:**
```bash
# Verify cluster access
kubectl cluster-info
kubectl get nodes

# Check namespace exists
kubectl get namespace production || kubectl create namespace production
```

3. **Secrets Created:**
```bash
# Create Supabase credentials secret
kubectl create secret generic supabase-creds \
  --from-literal=url=YOUR_SUPABASE_URL \
  --from-literal=key=YOUR_SUPABASE_KEY \
  -n production

# Create registry pull secret (if not exists)
kubectl create secret docker-registry registry-credentials \
  --docker-server=registry.digitalocean.com \
  --docker-username=YOUR_DO_TOKEN \
  --docker-password=YOUR_DO_TOKEN \
  -n production
```

---

### Step 1: Deploy API

```bash
# Apply the deployment
kubectl apply -f k8s/api-deployment.yaml

# Expected output:
deployment.apps/api created
service/api created
```

---

### Step 2: Verify Deployment

```bash
# Check pods are running
kubectl get pods -n production -l app=api

# Expected output:
NAME                   READY   STATUS    RESTARTS   AGE
api-xxxxxxxxxx-xxxxx   1/1     Running   0          30s
api-xxxxxxxxxx-xxxxx   1/1     Running   0          30s
api-xxxxxxxxxx-xxxxx   1/1     Running   0          30s

# Check logs
kubectl logs -n production -l app=api --tail=50

# Should see:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete
```

---

### Step 3: Check Service

```bash
# Get service details
kubectl get svc api -n production

# Expected output:
NAME   TYPE           CLUSTER-IP      EXTERNAL-IP       PORT(S)
api    LoadBalancer   10.xxx.xxx.xxx  XXX.XXX.XXX.XXX   80:xxxxx/TCP,443:xxxxx/TCP

# IMPORTANT: Note the EXTERNAL-IP!
```

---

### Step 4: Configure DNS

**Point 97v.ru to the LoadBalancer EXTERNAL-IP:**

1. Go to your DNS provider (e.g., Cloudflare, Route53, DigitalOcean DNS)
2. Update A record:
   ```
   Type: A
   Name: 97v.ru
   Value: <EXTERNAL-IP from Step 3>
   TTL: 300
   ```
3. Wait 5-10 minutes for DNS propagation

---

### Step 5: Test API

```bash
# Test with LoadBalancer IP directly
curl http://<EXTERNAL-IP>/health

# Expected:
{"status":"healthy","timestamp":"2025-12-07T..."}

# Test via domain (after DNS propagates)
curl https://97v.ru/health
curl https://97v.ru/api/v1/metrics
```

---

### Step 6: Monitor

```bash
# Watch pods status
kubectl get pods -n production -l app=api -w

# Check events
kubectl get events -n production --sort-by='.lastTimestamp'

# Monitor logs in real-time
kubectl logs -n production -l app=api -f
```

---

## 🐛 TROUBLESHOOTING

### Issue: Pods not starting (ImagePullBackOff)

**Symptom:**
```
api-xxx   0/1     ImagePullBackOff   0          2m
```

**Solution:**
```bash
# Verify image exists
docker pull registry.digitalocean.com/digital-twin-registry/api:v3.0.0

# Check registry credentials
kubectl get secret registry-credentials -n production

# Re-create if needed
kubectl delete secret registry-credentials -n production
kubectl create secret docker-registry registry-credentials \
  --docker-server=registry.digitalocean.com \
  --docker-username=YOUR_TOKEN \
  --docker-password=YOUR_TOKEN \
  -n production
```

---

### Issue: Pods CrashLoopBackOff

**Symptom:**
```
api-xxx   0/1     CrashLoopBackOff   3          5m
```

**Solution:**
```bash
# Check logs
kubectl logs -n production <pod-name> --previous

# Common causes:
# 1. Missing SUPABASE_URL/KEY
kubectl describe secret supabase-creds -n production

# 2. Port already in use
# 3. Application error - check logs
```

---

### Issue: Service has no EXTERNAL-IP

**Symptom:**
```
api   LoadBalancer   10.xxx.xxx.xxx   <pending>   80:xxxxx/TCP
```

**Solution:**
```bash
# Check LoadBalancer provisioning
kubectl describe svc api -n production

# Events should show:
#   Normal  EnsuringLoadBalancer  Creating load balancer
#   Normal  EnsuredLoadBalancer   Ensured load balancer

# If stuck for >5 minutes, check cloud provider dashboard
# DigitalOcean → Networking → Load Balancers
```

---

### Issue: 502 Bad Gateway

**Symptom:**
```
curl https://97v.ru/health
502 Bad Gateway
```

**Solution:**
```bash
# Check pods are READY
kubectl get pods -n production -l app=api

# All should be 1/1 Ready

# Check readiness probe
kubectl describe pod -n production <pod-name>

# Look for:
#   Readiness: http-get http://:8000/health
#   Last State: Terminated (if restarting)
```

---

## ✅ VERIFICATION CHECKLIST

- [ ] Docker image built and pushed
- [ ] Secrets created (supabase-creds, registry-credentials)
- [ ] Deployment applied: `kubectl apply -f k8s/api-deployment.yaml`
- [ ] 3 pods running: `kubectl get pods -n production -l app=api`
- [ ] Service has EXTERNAL-IP: `kubectl get svc api -n production`
- [ ] DNS A record updated to EXTERNAL-IP
- [ ] Health endpoint responds: `curl http://<IP>/health`
- [ ] Domain works: `curl https://97v.ru/health`
- [ ] API endpoints accessible: `curl https://97v.ru/api/v1/metrics`
- [ ] Monitoring setup (optional): Prometheus/Grafana

---

## 📊 EXPECTED RESULTS

After successful deployment:

✅ **97v.ru is ONLINE**  
✅ **All 4 API endpoints accessible:**
   - `GET /health` → 200 OK
   - `GET /api/v1/analysis/{id}` → 200 OK
   - `POST /api/v1/batch-process` → 202 Accepted
   - `GET /api/v1/metrics` → 200 OK
   - `WebSocket /api/v1/live-events` → Connection OK

✅ **High Availability:**
   - 3 replicas running
   - Zero downtime updates
   - Auto-restart on failure

✅ **TASK-006 Testing can proceed:**
   - Unit tests
   - Integration tests
   - Load testing
   - UAT

---

## 🔄 ROLLBACK PROCEDURE

If deployment fails:

```bash
# Delete deployment
kubectl delete -f k8s/api-deployment.yaml

# Or rollback to previous version
kubectl rollout undo deployment/api -n production

# Check rollback status
kubectl rollout status deployment/api -n production
```

---

## 📝 POST-DEPLOYMENT

1. **Update TASK-006 status:**
   - Rerun all tests from TASK-006-PRODUCT-QA-TESTING.md
   - Update TASK-006-PRODUCT-QA-TESTING-COMPLETED.md with results

2. **Monitor for 24 hours:**
   - Check pod restarts: `kubectl get pods -n production -l app=api`
   - Monitor errors: `kubectl logs -n production -l app=api --tail=100`
   - Watch metrics: Check Grafana dashboard

3. **Address remaining issues:**
   - Fix ISSUE-002 to ISSUE-006 from TASK-006-BUGS-FOUND.md
   - Add authentication
   - Add rate limiting
   - Replace mock data with real Supabase queries

---

## 👥 CONTACTS

**DevOps Team:** See TASK-007  
**Backend Team:** api/main.py issues  
**QA Team:** TASK-006 testing

---

**Status:** ✅ READY FOR DEPLOYMENT  
**Next Action:** Execute deployment steps above  
**ETA:** 30 minutes  
**Risk Level:** Low (can rollback)

---

**Created by:** AI Assistant (Comet)  
**Date:** 7 December 2025, 18:45 MSK
