# 🤖 TELEGRAM BOT: ПОШАГОВЫЙ ПЛАН ЗАПУСКА
## TASK-001 Action Plan (immediately)

**Дата:** 7 декабря 2025, 20:30 MSK  
**Приоритет:** 🔴 CRITICAL - NEXT IMMEDIATE  
**Дедлайн:** 23 декабря 2025 (16 дней)  
**Ответственный:** Andrey M. (AI Lead)

---

## 🎯 КОНЕЧНАЯ ЦЕЛЬ

Запущенный Telegram bot (@digital_twin_bot) в production, который:
- ✅ Принимает сообщения от пользователей
- ✅ Интегрирует запросы с Perplexity AI
- ✅ Логирует все диалоги в Supabase
- ✅ Развёрнут на K8s с 2 replicas
- ✅ Готов к использованию 23 Dec 2025

---

## 📋 ФАЗА 1: ПОДГОТОВКА (7-8 Dec) - 1 день

### ШАГ 1.1: Получить Telegram Bot Token ✅

**Что делать:**
1. Откройте Telegram Desktop или Web
2. Найдите **@BotFather**
3. Пошлите команду: `/newbot`
4. Ответьте на вопросы:
   - Bot name: `Digital Twin Bot`
   - Bot username: `digital_twin_bot` (будет @digital_twin_bot)

**Полученные результаты:**
```
✅ BotFather вернет:
   Token: 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
```

---

### ШАГ 1.2: Добавить Token в K8s Secrets

```bash
# Encode token в base64
TOKEN_BASE64=$(echo -n "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11" | base64)

# Добавить в existing secret
kubectl patch secret digital-twin-secrets -n production \
  -p '{"data":{"TELEGRAM_BOT_TOKEN":"'$TOKEN_BASE64'"}}'

# Verify
kubectl get secret digital-twin-secrets -n production -o yaml | grep TELEGRAM
```

---

## 📋 ФАЗА 2: РАЗРАБОТКА (8-14 Dec) - 7 дней

### ШАГ 2.1: Необходимые зависимости

```bash
pip install \
  python-telegram-bot==21.0 \
  supabase==2.9.1 \
  httpx==0.26.0 \
  python-dotenv==1.0.0
```

### ШАГ 2.2: Критические команды

```python
# bot.py - main commands
/start   - Greeting & instructions
/help    - All available commands
/ask     - Ask Perplexity AI
/history - Show last 10 queries
/api_status - Check system health
/analyze - Data analysis (v1.1)
/report - Get report (v1.1)
```

### ШАГ 2.3: Интеграция Perplexity

```python
# integrations/perplexity.py
async def ask_perplexity(question: str) -> str:
    response = await httpx.post(
        "https://api.perplexity.ai/chat/completions",
        headers={"Authorization": f"Bearer {PERPLEXITY_API_KEY}"},
        json={
            "model": "sonar",
            "messages": [{"role": "user", "content": question}],
            "max_tokens": 2000
        }
    )
    return response.json()["choices"][0]["message"]["content"]
```

---

## 📋 ФАЗА 3: ТЕСТИРОВАНИЕ (14-20 Dec) - 6 дней

```bash
# Локальный тест
 export TELEGRAM_BOT_TOKEN="your-token"
python bot.py

# Unit tests
python -m pytest tests/test_bot.py -v
```

---

## 📋 ФАЗА 4: DEPLOYMENT (20-22 Dec) - 2 дня

### ШАГ 4.1: Dockerfile.bot

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.bot.txt .
RUN pip install -r requirements.bot.txt
COPY bot.py .
CMD ["python", "bot.py"]
```

### ШАГ 4.2: K8s Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: digital-twin-bot
  namespace: production
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: bot
        image: registry.digitalocean.com/.../bot:v1.0
        env:
        - name: TELEGRAM_BOT_TOKEN
          valueFrom:
            secretKeyRef:
              name: digital-twin-secrets
              key: TELEGRAM_BOT_TOKEN
```

---

## 📋 ФАЗА 5: PRODUCTION (22-23 Dec) - 1 день

### ШАГ 5.1: Set Telegram Webhook

```bash
curl -X POST https://api.telegram.org/bot{TOKEN}/setWebhook \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://97v.ru/bot/webhook"}'
```

### ШАГ 5.2: Verify Production

```bash
kubectl get pods -n production -l app=digital-twin-bot -w
kubectl logs -f deployment/digital-twin-bot -n production
```

---

## 📋 CHECKLIST

- [ ] Get Bot Token from @BotFather
- [ ] Add Token to K8s Secret
- [ ] Create bot.py with commands
- [ ] Integrate Perplexity
- [ ] Integrate Supabase logging
- [ ] Local testing (polling mode)
- [ ] Unit tests passing
- [ ] Dockerfile.bot created
- [ ] K8s deployment yaml ready
- [ ] GitHub Actions workflow
- [ ] Docker image pushed
- [ ] 2 replicas running
- [ ] Webhook set on Telegram
- [ ] All commands working
- [ ] Production ready

---

## 🎯 SUCCESS CRITERIA

✅ Bot работает в @digital_twin_bot  
✅ /start выводит приветствие  
✅ /ask работает с Perplexity  
✅ Все диалоги логируются в Supabase  
✅ K8s deployment с 2 replicas  
✅ Zero downtime updates  
✅ Health checks passing  
✅ Logs readable в kubectl

---

**Document created:** 7 Dec 2025  
**Status:** ✅ READY FOR IMPLEMENTATION  
**Priority:** 🔴🔴🔴 CRITICAL