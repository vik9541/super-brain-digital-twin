# 🔧 ТЕСТИРОВАНОВАНИЕ ЧЕРЕZ DIGITALOCEAN CONSOLE

**Date:** Dec 9, 2025, 08:50 AM MSK  
**Tool:** DigitalOcean Droplet Terminal Console  
**Access:** https://cloud.digitalocean.com/droplets/534522841/terminal/ui/  
**Status:** 🟢 READY FOR USE  
**ℹ️ Supabase:** Knowledge_DBnanoAWS (lvixtpatqrtuwhygtpjx) - See [SUPABASE_PROJECTS_CLARITY.md](./SUPABASE_PROJECTS_CLARITY.md)

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

### Шаг 2: Пронустить Диагностику

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
# Скопировать:

curl http://97v.ru/health
```

**Ожидаемый результат:**
```
{"status": "healthy", "uptime": "12h"}
```

---

## 📈 ПОЛНЫЙ ТЕСТИРУЙЩИЙ WORKFLOW

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

# Set environment - CORRECT Project: lvixtpatqrtuwhygtpjx
export SUPABASE_URL="https://lvixtpatqrtuwhygtpjx.supabase.co"
export SUPABASE_KEY="your-key-here"

# ===============================================
# 2. Test Python connection
# ===============================================
python3 << 'EOF'
from supabase import create_client
try:
    db = create_client(
        "https://lvixtpatqrtuwhygtpjx.supabase.co",
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
# 1. Отустить тестов (если нужны)
# ===============================================
pip install -r requirements.test.txt

# ===============================================
# 2. Запустить полный test suite
# ===============================================
export SUPABASE_URL="https://lvixtpatqrtuwhygtpjx.supabase.co"
export SUPABASE_KEY="your-key-here"
python3 run_tests.py --all

# ===============================================
# 3. Проверить результаты
# ===============================================
# Все результаты автоматически сохраняются в Supabase
# проект lvixtpatqrtuwhygtpjx
```

---

## 📌 ГОТОВЫЕ КОМАНДЫ ДЛЯ КОПИРОВАНИЯ

### Быстрая диагностика (copy-paste ready)

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

### Запуск tests (copy-paste ready)

```bash
#!/bin/bash
echo "===== RUNNING TESTS ====="
export SUPABASE_URL="https://lvixtpatqrtuwhygtpjx.supabase.co"
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
   5. Запустить полный test suite
   6. Проверить результаты в Supabase (lvixtpatqrtuwhygtpjx)

⏱️ Время на полное тестирование: ~30 минут
```

---

**Status:** 🟢 **READY TO USE**  
**Last Updated:** Dec 9, 2025, 08:50 AM MSK  
**Supabase Project:** Knowledge_DBnanoAWS (lvixtpatqrtuwhygtpjx)  
**Tool Status:** ✅ **AVAILABLE 24/7**
