# 🔧 FIX GUIDE: API ACCESSIBILITY ISSUE

**Incident:** INC-2025-12-08-001  
**Problem:** API unreachable at 97v.ru (Empty reply from server)  
**Root Cause:** DNS/LoadBalancer IP mismatch  
**Estimated Fix Time:** 15-30 minutes  

---

## 🗒️ DIAGNOSIS

### What We Know

```
✅ API Pod:              RUNNING inside Kubernetes
✅ Internal Health:      WORKING (200 OK responses)
✅ LoadBalancer Service: CREATED (type: LoadBalancer)
❌ External Access:      BLOCKED (Empty reply)

❌ DNS Points To:        138.197.254.57
✅ Service IP:           138.197.254.53
⚠️  IP MISMATCH:          .57 vs .53
```

### Problem Signature

```bash
$ curl -v http://97v.ru/health
* Trying 138.197.254.57:80...
* Connected to 97v.ru (138.197.254.57) port 80 (#0)
> GET /health HTTP/1.1
> Host: 97v.ru
>
* Empty reply from server
* Closing connection 0
curl: (52) Empty reply from server  ❌
```

---

## 🚀 SOLUTION PATH

### Option A: Update DNS (Most Likely Fix)

**If LoadBalancer IP is correct (138.197.254.53), DNS needs update**

#### Step 1: Verify Current Service IP

```bash
#!/bin/bash
echo "🔍 Checking Kubernetes Service..."

# Get current external IP
EXTERNAL_IP=$(kubectl get svc api -n production \
  -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

echo "Service External IP: $EXTERNAL_IP"

# Get all services
echo ""
echo "All LoadBalancer services:"
kubectl get svc -n production | grep LoadBalancer
```

**Expected Output:**
```
Service External IP: 138.197.254.53

NAME          TYPE          EXTERNAL-IP        PORT(S)
api           LoadBalancer  138.197.254.53     80:32558/TCP
```

#### Step 2: Update DigitalOcean DNS

**Via DigitalOcean Control Panel:**

1. **Navigate to DNS:**
   - https://cloud.digitalocean.com/networking/domains
   - Click on: `97v.ru`

2. **Find A Record:**
   - Look for record type `A` pointing to `97v.ru`
   - Current value: `138.197.254.57` (WRONG)
   - New value: `138.197.254.53` (CORRECT)

3. **Update Record:**
   - Click Edit (pencil icon)
   - Change value from `138.197.254.57` to `138.197.254.53`
   - Save

4. **Wait for Propagation:**
   - DNS updates take 5-15 minutes
   - Check every minute:
   ```bash
   watch -n 1 'dig 97v.ru +short'
   # When it shows 138.197.254.53, DNS is propagated!
   ```

#### Step 3: Verify DNS Update

```bash
#!/bin/bash
echo "🔍 Verifying DNS propagation..."

# Check with different DNS servers
echo "Google DNS (8.8.8.8):"
nslookup 97v.ru 8.8.8.8

echo ""
echo "Cloudflare DNS (1.1.1.1):"
nslookup 97v.ru 1.1.1.1

echo ""
echo "Quad9 DNS (9.9.9.9):"
nslookup 97v.ru 9.9.9.9

# All should return: 138.197.254.53
```

#### Step 4: Test API Access

```bash
#!/bin/bash
echo "🧪 Testing API access..."

# Test 1: DNS Resolution
echo "Test 1: DNS Resolution"
dig 97v.ru +short
echo ""

# Test 2: TCP Connectivity
echo "Test 2: TCP Connection"
nc -zv 97v.ru 80
echo ""

# Test 3: HTTP Health Check
echo "Test 3: HTTP Health Check"
curl -v http://97v.ru/health

# Expected:
# HTTP/1.1 200 OK
# {"status": "healthy"}
```

**Success Indicators:**
```bash
✅ DNS resolves to 138.197.254.53
✅ TCP port 80 open
✅ HTTP 200 OK response
✅ JSON body returned
```

---

### Option B: Delete Duplicate Service (If Conflict Exists)

**If there are multiple LoadBalancer services:**

```bash
#!/bin/bash
echo "🔍 Checking for duplicate services..."

# List all services
kubectl get svc -n production

# If you see BOTH 'api' and 'api-service':
# One is current, one is old

# Determine which is correct:
echo ""
echo "Comparing services:"
echo "=== api ==="
kubectl describe svc api -n production | grep -E "(Type|External-IP|Endpoints)"

echo ""
echo "=== api-service ==="
kubectl describe svc api-service -n production | grep -E "(Type|External-IP|Endpoints)"

# Delete the OLD one (check Age column)
# Example: api-service is 2d21h old → DELETE it
echo ""
echo "Deleting old service..."
kubectl delete svc api-service -n production
echo "✅ Deleted old service"
```

---

### Option C: Recreate LoadBalancer Service

**If service is misconfigured:**

#### Step 1: Get Current Config

```bash
# Export current service
kubectl get svc api -n production -o yaml > api-service-backup.yaml
echo "✅ Backup saved to api-service-backup.yaml"
```

#### Step 2: Delete and Recreate

```bash
#!/bin/bash
echo "🔧 Recreating LoadBalancer service..."

# Delete current service
kubectl delete svc api -n production
echo "✅ Deleted service"

# Wait for deletion
sleep 5

# Create new service
kubectl apply -f - << 'EOF'
apiVersion: v1
kind: Service
metadata:
  name: api
  namespace: production
spec:
  type: LoadBalancer
  selector:
    app: api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  sessionAffinity: None
EOF

echo "✅ Service recreated"

# Wait for LoadBalancer to get IP
echo "⏳ Waiting for LoadBalancer to get external IP..."
sleep 30

# Check new IP
echo ""
echo "New External IP:"
kubectl get svc api -n production -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
echo ""
```

#### Step 3: Update DNS with New IP

```bash
# Get new IP
NEW_IP=$(kubectl get svc api -n production \
  -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

echo "Update DNS A record for 97v.ru to: $NEW_IP"
echo ""
echo "Steps:"
echo "1. Go to https://cloud.digitalocean.com/networking/domains"
echo "2. Click 97v.ru"
echo "3. Edit A record"
echo "4. Change value to: $NEW_IP"
echo "5. Save"
echo "6. Wait 5-15 minutes for propagation"
```

---

### Option D: Create Ingress for Better Routing

**Modern approach with NGINX Ingress:**

```bash
#!/bin/bash
echo "🔧 Creating NGINX Ingress..."

# Check if Ingress Controller exists
echo "Checking Ingress Controller:"
kubectl get pods -n ingress-nginx

# If empty, install:
# helm install ingress-nginx ingress-nginx/ingress-nginx -n ingress-nginx --create-namespace

# Create Ingress resource
kubectl apply -f - << 'EOF'
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api-ingress
  namespace: production
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - 97v.ru
    secretName: api-tls-cert
  rules:
  - host: 97v.ru
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api
            port:
              number: 8000
EOF

echo "✅ Ingress created"
echo ""
echo "Ingress status:"
kubectl get ingress -n production
```

---

## 📈 AUTOMATED FIX SCRIPT

**Copy-paste ready script:**

```bash
#!/bin/bash
set -e

echo "🔧 AUTO-FIX: API Accessibility Issue"
echo "======================================"
echo ""

# 1. Get current service status
echo "🔍 Step 1: Checking current status..."
echo ""

SERVICE_IP=$(kubectl get svc api -n production \
  -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "NOT FOUND")

DNS_IP=$(dig 97v.ru +short | head -1)

echo "Kubernetes Service IP: $SERVICE_IP"
echo "DNS A Record IP:       $DNS_IP"
echo ""

if [ "$SERVICE_IP" = "$DNS_IP" ]; then
    echo "✅ IPs match! Checking connectivity..."
    if curl -s http://97v.ru/health > /dev/null; then
        echo "✅ API is accessible! Problem may be resolved."
        exit 0
    else
        echo "❌ API still not responding. Checking logs..."
    fi
else
    echo "❌ IPs don't match. Need to update DNS."
    echo ""
    echo "🔧 Step 2: Instructions to fix"
    echo "======================================"
    echo ""
    echo "1. Go to: https://cloud.digitalocean.com/networking/domains"
    echo "2. Click on: 97v.ru"
    echo "3. Find A record pointing to: $DNS_IP"
    echo "4. Edit it to point to: $SERVICE_IP"
    echo "5. Save changes"
    echo "6. Wait 5-15 minutes"
    echo ""
    echo "Then run:"
    echo "  while ! curl -s http://97v.ru/health; do sleep 10; done && echo 'API is UP!'"
    exit 1
fi

# 2. Check pod status
echo ""
echo "🔍 Step 3: Checking pod status..."
echo ""

POD_STATUS=$(kubectl get pod -n production -l app=api \
  -o jsonpath='{.items[0].status.phase}' 2>/dev/null || echo "NOT FOUND")

echo "Pod Status: $POD_STATUS"

if [ "$POD_STATUS" != "Running" ]; then
    echo "❌ Pod not running! Restarting deployment..."
    kubectl rollout restart deployment/api -n production
    echo "✅ Deployment restarted. Waiting for pod to start..."
    sleep 30
fi

# 3. Final test
echo ""
echo "🔍 Step 4: Final connectivity test..."
echo ""

if curl -s http://97v.ru/health > /dev/null; then
    echo "✅ SUCCESS! API is now accessible at http://97v.ru"
    curl -s http://97v.ru/health | jq .
    exit 0
else
    echo "❌ API still not responding. Manual intervention needed."
    echo ""
    echo "Debug commands:"
    echo "  kubectl get svc -n production"
    echo "  kubectl logs deployment/api -n production"
    echo "  dig 97v.ru"
    echo "  curl -v http://97v.ru/health"
    exit 1
fi
```

**Run it:**
```bash
bash fix_api.sh
```

---

## 📈 MONITORING DURING FIX

### Watch DNS Propagation

```bash
# Keep checking until IP updates:
watch -n 5 'echo "DNS: $(dig 97v.ru +short)"; echo "Service: $(kubectl get svc api -n production -o jsonpath="{.status.loadBalancer.ingress[0].ip}")"'

# Or use this loop:
for i in {1..30}; do
  DNS=$(dig 97v.ru +short)
  SVC=$(kubectl get svc api -n production -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
  echo "[$i/30] DNS: $DNS | Service: $SVC"
  if [ "$DNS" = "$SVC" ]; then
    echo "✅ IPs MATCH! Testing..."
    curl -s http://97v.ru/health | jq . && exit 0
  fi
  sleep 10
done
```

### Watch API Logs

```bash
# Real-time logs from API pod:
kubectl logs deployment/api -n production -f

# Watch for:
# ✅ INFO: health checks passing
# ✅ Incoming requests from different IPs
# ❌ ERROR messages (if any)
```

### Monitor Service Status

```bash
# Watch service changes:
kubectl get svc api -n production -w

# Watch pod status:
kubectl get pods -n production -w
```

---

## ✅ VERIFICATION AFTER FIX

### Checklist

```bash
#!/bin/bash
echo "👍 Verification Checklist"
echo "========================"
echo ""

echo -n "✅ DNS resolves correctly: "
dig 97v.ru +short | grep 138 && echo "PASS" || echo "FAIL"

echo -n "✅ Service has External-IP: "
kubectl get svc api -n production | grep LoadBalancer | grep -E "138\.197\.254" && echo "PASS" || echo "FAIL"

echo -n "✅ Pod is running: "
kubectl get pod -n production -l app=api | grep Running && echo "PASS" || echo "FAIL"

echo -n "✅ Health endpoint responds: "
curl -s -o /dev/null -w "%{http_code}" http://97v.ru/health | grep 200 && echo "PASS" || echo "FAIL"

echo -n "✅ HTTPS works: "
curl -s -o /dev/null -w "%{http_code}" https://97v.ru/health | grep 200 && echo "PASS" || echo "FAIL"

echo ""
echo "✅ All checks passed if all say PASS"
```

### Full Test

```bash
# Run complete test suite again:
python3 run_tests.py --api

# Expected:
# ✅ Health Endpoint: PASSED
# ✅ GET /api/v1/analysis/{id}: PASSED
# ✅ GET /api/v1/metrics: PASSED
# ...
```

---

## 🚨 IF STILL NOT WORKING

### Escalation Steps

1. **Check DigitalOcean Status**
   - https://status.digitalocean.com/
   - Any incidents reported?

2. **Verify Firewall**
   ```bash
   # DigitalOcean > Networking > Firewalls
   # Should allow: TCP 80, TCP 443 from anywhere
   ```

3. **Test from Different Networks**
   ```bash
   # Use mobile hotspot or different ISP
   curl -v http://97v.ru/health
   ```

4. **Check Kubernetes Events**
   ```bash
   kubectl get events -n production --sort-by='.lastTimestamp'
   ```

5. **Contact DigitalOcean Support**
   - Ticket: LoadBalancer not routing to 97v.ru
   - Affected IP: 138.197.254.53
   - Cluster: your-cluster-name

---

## 🌟 SUMMARY

```
Problem:     API unreachable at 97v.ru
Root Cause:  DNS A-record points to wrong IP (138.197.254.57 vs .53)
Solution:    Update DNS A-record in DigitalOcean
Time to Fix: 15-30 minutes
SLA:         < 1 hour

Next Steps:
1. Run diagnosis script
2. Update DNS record
3. Wait for propagation
4. Verify connectivity
5. Run full test suite
```

**Status:** 🔴 **READY FOR EXECUTION**
