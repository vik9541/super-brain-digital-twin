# 📊 DEPLOYMENT MONITORING GUIDE
## API v3.0.0 Real-Time Status Commands

**Use these commands to monitor the deployment**

---

## 🔄 REAL-TIME MONITORING

### Watch Deployment Rollout
```bash
kubectl rollout status deployment/api -n production --watch
```

**Output while rolling out:**
```
Waiting for deployment "api" rollout to finish: 2 out of 3 new replicas have been updated...
Waiting for deployment "api" rollout to finish: 2 out of 3 new replicas have been updated...
Waiting for deployment "api" rollout to finish: 3 out of 3 new replicas have been updated...
Waiting for deployment "api" rollout to finish: 1 old replicas are pending termination...
deployment "api" successfully rolled out
```

### Watch Pods in Real-Time
```bash
kubectl get pods -n production -l app=api --watch
```

**Desired output after deployment:**
```
NAME                    READY   STATUS    RESTARTS   AGE
api-8f5c9b2d1-abc12    2/2     Running   0          2m
api-8f5c9b2d1-def45    2/2     Running   0          3m
api-8f5c9b2d1-ghi78    2/2     Running   0          4m
```

### View Deployment Details
```bash
kubectl describe deployment api -n production
```

### Check Service and LoadBalancer
```bash
kubectl get svc api -n production
```

**Desired output:**
```
NAME   TYPE           CLUSTER-IP       EXTERNAL-IP    PORT(S)              AGE
api    LoadBalancer   10.245.x.x       1.2.3.4        80:30xxx/TCP   5m
```

---

## 🔍 VIEW LOGS

### Logs from All Pods
```bash
kubectl logs -f deployment/api -n production
```

### Logs from Specific Pod
```bash
kubectl logs -f pod/api-8f5c9b2d1-abc12 -n production
```

### Get Last 100 Lines
```bash
kubectl logs --tail=100 deployment/api -n production
```

### Logs with Timestamps
```bash
kubectl logs -f deployment/api -n production --timestamps=true
```

---

## 📅 CHECK EVENTS

### Recent Events
```bash
kubectl get events -n production --sort-by='.lastTimestamp'
```

### Watch Events
```bash
kubectl get events -n production --watch
```

---

## 👻 DEBUG COMMANDS

### Check if Secrets Exist
```bash
kubectl get secrets -n production
kubectl describe secret digital-twin-secrets -n production
```

### Check Image Pull Status
```bash
kubectl describe pod/api-8f5c9b2d1-abc12 -n production
```

Look for:
- Container ID (means image pulled)
- Readiness/Liveness probe results
- Environment variables from secret

### Check Pod CPU/Memory
```bash
kubectl top pods -n production
kubectl top nodes
```

---

## ✅ HEALTH CHECKS

### Once LoadBalancer EXTERNAL-IP is assigned:

```bash
# Replace EXTERNAL-IP with actual IP
EXTERNAL_IP="1.2.3.4"

# Health endpoint
curl http://$EXTERNAL_IP/health

# Ping endpoint
curl http://$EXTERNAL_IP/ping

# With Host header (for ingress)
curl -H "Host: api.97v.ru" http://$EXTERNAL_IP/health
```

---

## 🔎 TROUBLESHOOTING

### Pod Stuck in ImagePullBackOff
```bash
# Check image exists in registry
kubectl describe pod [pod-name] -n production

# View pull events
kubectl get events -n production | grep Pull
```

### Pod Not Ready
```bash
# Check readiness probe
kubectl describe pod [pod-name] -n production | grep -A 5 "Readiness"

# Check logs for startup errors
kubectl logs [pod-name] -n production
```

### CrashLoopBackOff
```bash
# View last logs before crash
kubectl logs --previous [pod-name] -n production

# Check pod description
kubectl describe pod [pod-name] -n production
```

---

## 🐛 USEFUL ALIASES

Add to ~/.bashrc:

```bash
alias k=kubectl
alias kgp='kubectl get pods -n production'
alias kgs='kubectl get svc -n production'
alias kd='kubectl describe'
alias kl='kubectl logs -f'
alias kw='kubectl get pods -n production --watch'
```

Then use:
```bash
k get pods -n production -l app=api --watch
kl deployment/api -n production
k describe deployment api -n production
```

---

## 🔐 QUICK STATUS CHECK

```bash
#!/bin/bash
# deployment-status.sh

echo "=== API DEPLOYMENT STATUS ==="
echo ""
echo "Deployment Status:"
kubectl rollout status deployment/api -n production

echo ""
echo "Pods:"
kubectl get pods -n production -l app=api

echo ""
echo "Service:"
kubectl get svc api -n production

echo ""
echo "Recent Events:"
kubectl get events -n production --sort-by='.lastTimestamp' | tail -10
```

Run with:
```bash
bash deployment-status.sh
```

---

## 📅 EXPECTED PROGRESSION

### Phase 1: Pulling Image (1-3 minutes)
```
STATUS: ContainerCreating / ImagePullBackOff
EVENT: Pulling image "registry.digitalocean.com/digital-twin-registry/api:v3.0.0"
```

### Phase 2: Starting Container (1-2 minutes)
```
STATUS: Running
EVENT: Started container api
```

### Phase 3: Readiness Probe (30-60 seconds)
```
READY: 1/2 or 2/2
EVENT: Readiness probe succeeded
```

### Phase 4: All Replicas Ready (3-5 minutes total)
```
ALL PODS: 2/2 Running
DEPLOYMENT: Successfully rolled out
```

### Phase 5: LoadBalancer Assigned IP (1-2 minutes)
```
EXTERNAL-IP: 1.2.3.4 (was <pending>)
```

---

## 👥 GETTING HELP

```bash
# Generic kubectl help
kubectl --help

# Help for specific command
kubectl get --help
kubectl describe --help
kubectl logs --help

# Get cluster info
kubectl cluster-info

# Get API server version
kubectl version
```

---

**Monitor and report status using these commands**