# 🔧 ТЕСТИРОВАНИЕ ЧЕРЕЗ DIGITALOCEAN CONSOLE

**Date:** Dec 8, 2025, 08:24 AM MSK  
**Tool:** DigitalOcean Droplet Terminal Console  
**Access:** https://cloud.digitalocean.com/droplets/534522841/terminal/ui/  
**Status:** 🟢 READY FOR USE  

---

## 🔍 ЧТО ТАКОЕ DIGITALOCEAN TERMINAL?

**DigitalOcean Console** - веб-терминал прямо в браузере для работы с вашим Droplet'ом.

**Преимущества:**
- ✅ Не нужно SSH клиент
- ✅ Не нужно конфиги и ключи
- ✅ Прямая команда через браузер
- ✅ Полный доступ к Kubernetes
- ✅ Просмотр логов в реальном времени
- ✅ Все инструменты уже установлены

---

## 🚀 БЫСТРЫЙ СТАРТ (2 МИНУТЫ)

### Шаг 1: Открыть Console

```
1. Перейти: https://cloud.digitalocean.com/droplets/534522841/terminal/ui/
2. Нажать на окно терминала
3. Готово к использованию! ✅
```

### Шаг 2: Запустить Диагностику

```bash
# Скопировать-вставить в терминал:

kubectl get pods -n production
```

**Ожидаемый результат:**
```
NAMESPACE     NAME                                    READY   STATUS
production    api-847495fbc4-686tk                    1/1     Running
production    digital-twin-bot-xxxxx-xxxxx            1/1     Running
```

### Шаг 3: Проверить API

```bash
# Скопировать-вставить:

curl http://97v.ru/health
```

**Ожидаемый результат:**
```
{"status": "healthy", "uptime": "12h"}
```

---

## 📊 ПОЛНЫЙ ТЕСТИРУЮЩИЙ WORKFLOW

### ЧАСТЬ 1: ИНФРАСТРУКТУРА (5 минут)

```bash
# ===============================================
# 1. Проверить Kubernetes статус
# ===============================================
echo "🔧 Checking Kubernetes..."
kubectl get pods -n production
kubectl get svc -n production
kubectl get nodes

# ===============================================
# 2. Проверить DNS
# ===============================================
echo "🔧 Checking DNS..."
dig 97v.ru +short
nslookup 97v.ru

# ===============================================
# 3. Проверить Network
# ===============================================
echo "🔧 Checking Network..."
ping -c 4 97v.ru
nc -zv 97v.ru 80
```

### ЧАСТЬ 2: API TESTS (5 минут)

```bash
# ===============================================
# 1. Health Endpoint
# ===============================================
echo "🌐 Testing API Health..."
curl -v http://97v.ru/health

# Expected: 200 OK

# ===============================================
# 2. Check pod logs
# ===============================================
echo "📁 Checking API logs..."
kubectl logs deployment/api -n production --tail=20

# Expected: Successful health checks

# ===============================================
# 3. Test from inside cluster
# ===============================================
echo "🚧 Testing internal access..."
kubectl run -it --image=curlimages/curl test --restart=Never -- curl http://api:8000/health

# Expected: 200 OK response
```

### ЧАСТЬ 3: DATABASE (5 минут)

```bash
# ===============================================
# 1. Test Supabase Connection
# ===============================================
echo "💾 Testing Database..."

# Set environment
export SUPABASE_URL="https://hbdrmgtcvlwjcecptfxd.supabase.co"
export SUPABASE_KEY="your-key-here"

# ===============================================
# 2. Test Python connection
# ===============================================
python3 << 'EOF'
from supabase import create_client
try:
    db = create_client(
        "https://hbdrmgtcvlwjcecptfxd.supabase.co",
        "your-key-here"
    )
    response = db.table('test_results').select('COUNT(*)').execute()
    print("✅ Database connected!")
    print(f"Response: {response}")
except Exception as e:
    print(f"❌ Connection failed: {e}")
EOF
```

### ЧАСТЬ 4: ЗАПУСТИТЬ ПОЛНЫЙ ТЕСТ (15 минут)

```bash
# ===============================================
# 1. Установить зависимости (если нужны)
# ===============================================
pip install -r requirements.test.txt

# ===============================================
# 2. Запустить полный test suite
# ===============================================
python3 run_tests.py --all

# ===============================================
# 3. Проверить результаты
# ===============================================
# Все результаты автоматически сохранятся в Supabase
```

---

## 📌 ГОТОВЫЕ КОМАНДЫ ДЛЯ КОПИРОВАНИЯ

### Быстрая диагностика (скопировать целиком)

```bash
#!/bin/bash

echo "✅ KUBERNETES STATUS"
kubectl get pods -n production

echo ""
echo "✅ LOADBALANCER IP"
kubectl get svc api -n production -o jsonpath='{.status.loadBalancer.ingress[0].ip}'

echo ""
echo "✅ DNS RESOLUTION"
dig 97v.ru +short

echo ""
echo "✅ API HEALTH"
curl -s http://97v.ru/health | jq . || echo "Failed"

echo ""
echo "✅ API LOGS"
kubectl logs deployment/api -n production --tail=10
```

### Проверить мисматч IP (скопировать целиком)

```bash
#!/bin/bash

echo "🔍 CHECKING IP MISMATCH..."
echo ""

DNS_IP=$(dig 97v.ru +short | head -1)
SVC_IP=$(kubectl get svc api -n production -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

echo "DNS A-Record IP:  $DNS_IP"
echo "Service External: $SVC_IP"
echo ""

if [ "$DNS_IP" = "$SVC_IP" ]; then
    echo "✅ IPs MATCH!"
else
    echo "❌ IPs DON'T MATCH!"
    echo "🔧 Need to update DNS from $DNS_IP to $SVC_IP"
fi
```

### Исправить DNS (инструкция)

```bash
#!/bin/bash

echo "🔧 DNS FIX INSTRUCTIONS"
echo ""

NEW_IP=$(kubectl get svc api -n production -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

echo "1. Go to: https://cloud.digitalocean.com/networking/domains"
echo "2. Click on: 97v.ru"
echo "3. Find A record"
echo "4. Edit and change to: $NEW_IP"
echo "5. Save"
echo "6. Wait 5-15 minutes"
echo ""
echo "Then test:"
echo "  curl http://97v.ru/health"
```

### Запустить все тесты

```bash
#!/bin/bash

echo "🧪 RUNNING FULL TEST SUITE"
echo ""

# Set env variables
export SUPABASE_URL="https://hbdrmgtcvlwjcecptfxd.supabase.co"
export SUPABASE_KEY="your-key-here"
export API_URL="http://97v.ru"

# Run tests
python3 run_tests.py --all

echo ""
echo "✅ Tests completed! Check Supabase for results."
```

---

## 📚 СПРАВОЧНИК КОМАНД

### Kubernetes

```bash
# Список подов
kubectl get pods -n production

# Логи API
kubectl logs deployment/api -n production

# Реальные логи (streaming)
kubectl logs deployment/api -n production -f

# Описание сервиса
kubectl describe svc api -n production

# События в namespace
kubectl get events -n production --sort-by='.lastTimestamp'

# Перезагрузить deployment
kubectl rollout restart deployment/api -n production

# Проверить ресурсы
kubectl top pods -n production
kubectl top nodes
```

### DNS & Networking

```bash
# Просмотреть DNS
dig 97v.ru +short
nslookup 97v.ru
dig 97v.ru @8.8.8.8      # Google DNS

# Проверить связь
ping -c 4 97v.ru
ping -c 4 138.197.254.53

# Проверить порты
nc -zv 97v.ru 80
nc -zv 97v.ru 443

# Трассировка
traceroute 97v.ru
```

### API Testing

```bash
# Простой запрос
curl http://97v.ru/health

# Детальный запрос
curl -v http://97v.ru/health

# С сохранением ответа
curl -s http://97v.ru/health | jq .

# С заголовками
curl -i http://97v.ru/health

# HTTPS
curl https://97v.ru/health
```

### Python Testing

```bash
# Запустить run_tests.py
python3 run_tests.py --all
python3 run_tests.py --infrastructure
python3 run_tests.py --api
python3 run_tests.py --database

# Проверить конкретный тест
python3 << 'EOF'
import requests
response = requests.get('http://97v.ru/health')
print(f"Status: {response.status_code}")
print(f"Body: {response.json()}")
EOF
```

---

## 📈 STEP-BY-STEP: ПОЛНОЕ ТЕСТИРОВАНИЕ

### Шаг 1: Открыть DigitalOcean Console (1 мин)

```
URL: https://cloud.digitalocean.com/droplets/534522841/terminal/ui/
```

### Шаг 2: Проверить инфраструктуру (2 мин)

```bash
echo "=== KUBERNETES ==="
kubectl get pods -n production
kubectl get svc -n production
kubectl get nodes
```

### Шаг 3: Проверить DNS/Networking (2 мин)

```bash
echo "=== DNS & NETWORK ==="
dig 97v.ru +short
ping -c 4 97v.ru
nc -zv 97v.ru 80
```

### Шаг 4: Проверить API (2 мин)

```bash
echo "=== API TESTS ==="
curl -v http://97v.ru/health
kubectl logs deployment/api -n production --tail=5
```

### Шаг 5: Если API не работает (5 мин)

```bash
echo "=== DIAGNOSING ISSUE ==="

# Check IP mismatch
echo "DNS IP: $(dig 97v.ru +short)"
echo "Service IP: $(kubectl get svc api -n production -o jsonpath='{.status.loadBalancer.ingress[0].ip}')"

# Check if they match
if [ "$(dig 97v.ru +short)" != "$(kubectl get svc api -n production -o jsonpath='{.status.loadBalancer.ingress[0].ip}')" ]; then
    echo "🔴 IPs DON'T MATCH - Need to update DNS!"
else
    echo "✅ IPs match"
fi
```

### Шаг 6: Запустить полный тест (15 мин)

```bash
export SUPABASE_URL="https://hbdrmgtcvlwjcecptfxd.supabase.co"
export SUPABASE_KEY="your-key-here"
python3 run_tests.py --all
```

### Шаг 7: Проверить результаты (2 мин)

```bash
echo "=== TEST RESULTS ==="
# Результаты сохранены в Supabase
# https://app.supabase.com/project/[id]/editor/test_results
```

---

## 🔧 РЕШЕНИЕ ПРОБЛЕМ ВНЕ ТЕРМИНАЛА

### Если API не отвечает

```bash
# 1. Check if pod is running
kubectl get pod -n production -l app=api

# 2. Check logs for errors
kubectl logs deployment/api -n production --tail=50

# 3. Restart pod if needed
kubectl rollout restart deployment/api -n production

# 4. Wait and test again
sleep 30
curl http://97v.ru/health
```

### Если DNS не резолвится

```bash
# 1. Check DNS propagation
for i in {1..5}; do
  echo "Attempt $i: $(dig 97v.ru +short)"
  sleep 5
done

# 2. Check with different DNS servers
dig 97v.ru @8.8.8.8
dig 97v.ru @1.1.1.1

# 3. Flush local cache (if on local machine)
sudo systemctl restart systemd-resolved  # Linux
```

### Если тесты не запускаются

```bash
# 1. Check Python
python3 --version

# 2. Install requirements
pip install -r requirements.test.txt

# 3. Check if test file exists
ls -la run_tests.py

# 4. Try running manually
python3 run_tests.py --infrastructure
```

---

## 📝 КОПИРОВАТЬ-ВСТАВИТЬ БЛОКИ

### Полная диагностика (copy-paste ready)

```bash
#!/bin/bash
echo "===== FULL DIAGNOSTIC ====="
echo ""
echo "🔧 KUBERNETES:"
kubectl get pods -n production
echo ""
echo "🔧 SERVICES:"
kubectl get svc -n production
echo ""
echo "🔧 DNS:"
dig 97v.ru +short
echo ""
echo "🔧 API HEALTH:"
curl -s http://97v.ru/health || echo "FAILED"
echo ""
echo "🔧 API LOGS:"
kubectl logs deployment/api -n production --tail=5
echo ""
echo "===== DIAGNOSTIC COMPLETE ====="
```

### Запуск тестов (copy-paste ready)

```bash
#!/bin/bash
echo "===== RUNNING TESTS ====="
export SUPABASE_URL="https://hbdrmgtcvlwjcecptfxd.supabase.co"
export SUPABASE_KEY="your-key"
export API_URL="http://97v.ru"
echo "🧪 Starting tests..."
python3 run_tests.py --all
echo "✅ Tests completed!"
```

---

## 🌟 SUMMARY

```
🔧 DigitalOcean Terminal Tool
   URL: https://cloud.digitalocean.com/droplets/534522841/terminal/ui/

✅ Преимущества:
   - Не нужен SSH client
   - Все инструменты установлены
   - Полный доступ к Kubernetes
   - Просмотр логов в реальном времени

📈 Стандартный workflow:
   1. Открыть console в браузере
   2. Запустить диагностику
   3. Проверить API
   4. Если не работает - исправить DNS
   5. Запустить полный тест suite
   6. Проверить результаты в Supabase

⏱️ Времени на полное тестирование: ~30 минут
```

---

**Status:** 🟢 **READY TO USE**  
**Last Updated:** Dec 8, 2025, 08:24 AM MSK  
**Tool Status:** ✅ **AVAILABLE 24/7**  
