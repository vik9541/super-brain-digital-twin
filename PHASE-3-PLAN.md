# 🚀 PHASE 3 PLAN: BOT DEVELOPMENT

**Date:** Dec 8, 2025  
**Duration:** 8 hours (09:00-17:00 MSK)  
**Status:** ⏳ READY TO START  
**Predecessor:** Phase 2 (Due completion Dec 7, 23:35 MSK)  

---

## 🎯 OVERVIEW

**Phase 3 Goal:** Connect Telegram bot to N8N workflows via FastAPI webhooks

**Deliverables:**
- ✅ Telegram bot configured
- ✅ FastAPI webhook endpoints created
- ✅ Bot commands working (/ask, /analyze, /report)
- ✅ Real-time message handling
- ✅ Error handling & notifications
- ✅ Production deployment

**Success Criteria:**
- ✅ Bot receives /ask command
- ✅ Message sent to N8N Workflow #1
- ✅ Response returned to Telegram user
- ✅ Zero errors in logs
- ✅ Response time <2 seconds

---

## 📈 DETAILED TIMELINE

### **SUB-TASK 1: Bot Setup (1 hour)**
**Time:** 09:00-10:00 MSK

#### **Step 1: Create Bot (30 min)**
```
1. Open Telegram → Find @BotFather
2. Send: /start
3. Send: /newbot
4. Name: "Digital Twin Bot"
5. Username: "digitaltwin_bot" (must be unique)
6. Copy bot token (already have it)
7. Save: 8243753801:AAFAx3XCv0VapuDl7TeAqm5HLAq_klnhaoI
```

#### **Step 2: Configure Commands (30 min)**
```
Send to @BotFather:
/mybots → Select bot → Edit Commands

Add:
/start   - Start interaction
/ask     - Ask Perplexity a question
/analyze - Get daily analysis
/report  - Get hourly report
/help    - Show all commands
/status  - Check bot status
```

**Checklist:**
- [ ] Bot token obtained
- [ ] Commands configured
- [ ] Bot active in Telegram

---

### **SUB-TASK 2: FastAPI Integration (2 hours)**
**Time:** 10:00-12:00 MSK

#### **Step 1: Create Webhook Endpoints (1 hour)**

**Endpoint 1: /webhook/telegram (receive messages)**
```python
@app.post("/webhook/telegram")
async def telegram_webhook(update: dict):
    """
    Receive messages from Telegram bot
    Format: {"message": "{text}", "chat_id": 123456789, "user_id": 123}
    """
    message = update.get("message")
    user_id = update.get("user_id")
    
    # Route to N8N workflow
    workflow_response = await call_n8n_webhook(
        workflow="digital-twin-ask",
        data={"question": message, "user_id": user_id}
    )
    
    return {"status": "processed", "response": workflow_response}
```

**Endpoint 2: /webhook/n8n/response (receive workflow results)**
```python
@app.post("/webhook/n8n/response")
async def n8n_response(data: dict):
    """
    Receive analysis results from N8N
    Route to Telegram user
    """
    chat_id = data.get("chat_id")
    response_text = data.get("response")
    
    # Send to Telegram
    await send_telegram_message(chat_id, response_text)
    
    return {"status": "sent_to_telegram"}
```

**Endpoint 3: /health (API health check)**
```python
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "bot_status": "active",
        "n8n_connected": await check_n8n_connection()
    }
```

#### **Step 2: Add Error Handling (1 hour)**

**Error Handler Class:**
```python
class WebhookHandler:
    async def handle_error(self, error: Exception, context: dict):
        log.error(f"Webhook error: {error}", extra=context)
        
        # Send to Telegram
        await send_telegram_message(
            context["chat_id"],
            f"🚨 Error processing request: {str(error)[:100]}"
        )
        
        # Log to database
        await save_error_log(error, context)
    
    async def retry_failed_request(self, request_id: str, max_retries=3):
        for attempt in range(max_retries):
            try:
                # Retry logic
                pass
            except Exception as e:
                if attempt == max_retries - 1:
                    await self.handle_error(e, {"request_id": request_id})
```

**Checklist:**
- [ ] 3 endpoints created
- [ ] Error handlers implemented
- [ ] Logging configured
- [ ] Tested locally

---

### **SUB-TASK 3: Bot Commands (2 hours)**
**Time:** 12:00-14:00 MSK

#### **Command 1: /start**
```python
@bot.message_handler(commands=['start'])
async def cmd_start(message):
    text = """
🌟 Welcome to Digital Twin Bot!

I'm an AI assistant powered by Perplexity AI.

Commands:
/ask - Ask me a question
/analyze - Get daily analysis
/report - Get hourly report
/help - Show help

Let's talk!
    """
    await bot.reply_to(message, text)
```

#### **Command 2: /ask**
```python
@bot.message_handler(commands=['ask'])
async def cmd_ask(message):
    # Extract question
    question = message.text.replace('/ask ', '', 1)
    
    if not question:
        await bot.reply_to(message, "🤔 Please ask a question: /ask [your question]")
        return
    
    # Send to N8N Workflow #1
    response = await httpx.post(
        "https://lavrentev.app.n8n.cloud/webhook/digital-twin-ask",
        json={
            "question": question,
            "user_id": message.from_user.id,
            "chat_id": message.chat.id
        }
    )
    
    # Get response
    result = response.json()
    await bot.reply_to(message, result['answer'])
```

#### **Command 3: /analyze**
```python
@bot.message_handler(commands=['analyze'])
async def cmd_analyze(message):
    await bot.reply_to(message, "📄 Generating daily analysis...")
    
    # Trigger N8N Workflow #2 (if available)
    # Or get cached report from database
    response = await get_daily_analysis()
    
    await bot.reply_to(message, response)
```

#### **Command 4: /report**
```python
@bot.message_handler(commands=['report'])
async def cmd_report(message):
    await bot.reply_to(message, "📈 Generating hourly report...")
    
    # Trigger N8N Workflow #3 (if available)
    # Or get from cache
    response = await get_hourly_report()
    
    await bot.reply_to(message, response)
```

#### **Command 5: /help**
```python
@bot.message_handler(commands=['help'])
async def cmd_help(message):
    text = """
🔠 Available Commands:

/start - Welcome message
/ask - Ask a question to Perplexity
/analyze - Get daily analysis
/report - Get hourly report
/help - Show this help
/status - Check bot status

Example:
/ask What is machine learning?
    """
    await bot.reply_to(message, text)
```

#### **Command 6: /status**
```python
@bot.message_handler(commands=['status'])
async def cmd_status(message):
    status = await check_all_systems()
    
    text = f"""
👋 Bot Status:
🟢 API: {status['api']}
🟢 N8N WF#1: {status['wf1']}
🟢 N8N WF#2: {status['wf2']}
🟢 N8N WF#3: {status['wf3']}
🟢 Database: {status['db']}
    """
    
    await bot.reply_to(message, text)
```

**Checklist:**
- [ ] /start command working
- [ ] /ask command working
- [ ] /analyze command working
- [ ] /report command working
- [ ] /help command working
- [ ] /status command working

---

### **SUB-TASK 4: Real-Time Handling (2 hours)**
**Time:** 14:00-16:00 MSK

#### **Message Routing**
```python
class MessageRouter:
    async def route_message(self, message: dict) -> str:
        """
        Route to appropriate workflow based on content
        """
        text = message.get("text", "").lower()
        
        if text.startswith("/ask"):
            return "workflow-1-perplexity"
        elif text.startswith("/analyze"):
            return "workflow-2-daily"
        elif text.startswith("/report"):
            return "workflow-3-hourly"
        else:
            return "workflow-1-perplexity"  # Default
    
    async def execute(self, message: dict):
        workflow = await self.route_message(message)
        response = await call_workflow(workflow, message)
        return response
```

#### **Response Queuing**
```python
class ResponseQueue:
    async def enqueue(self, request_id: str, user_id: int):
        await cache.set(f"request:{request_id}", user_id, expire=300)
    
    async def dequeue(self, request_id: str) -> dict:
        return await cache.get(f"request:{request_id}")
    
    async def notify_user(self, user_id: int, response: str):
        await bot.send_message(user_id, response)
```

#### **Error Notifications**
```python
class ErrorNotifier:
    async def notify_user_error(self, user_id: int, error: str):
        await bot.send_message(
            user_id,
            f"🚨 Error: {error}\n\nTry again or contact support."
        )
    
    async def notify_admin(self, error: dict):
        log.error("Critical error", extra=error)
        # Send to admin Telegram
        # Send to monitoring system
```

**Checklist:**
- [ ] Message routing configured
- [ ] Response queuing working
- [ ] Error notifications active
- [ ] User feedback messages set

---

### **SUB-TASK 5: Testing & Deployment (1 hour)**
**Time:** 16:00-17:00 MSK

#### **Testing**
```bash
# Test /start command
curl -X POST http://localhost:8000/webhook/telegram \
  -d '{"message": "/start", "user_id": 123, "chat_id": 123}'

# Test /ask command
curl -X POST http://localhost:8000/webhook/telegram \
  -d '{"message": "/ask What is AI?", "user_id": 123, "chat_id": 123}'

# Test health endpoint
curl http://localhost:8000/health
```

#### **Deployment**
```bash
# Build Docker image
docker build -t digital-twin-bot:v1 .

# Push to registry
docker push your-registry/digital-twin-bot:v1

# Deploy to Kubernetes
kubectl apply -f k8s/bot-deployment.yaml

# Verify
kubectl get pods
kubectl logs -f deployment/digital-twin-bot
```

**Checklist:**
- [ ] All commands tested locally
- [ ] Webhook connectivity verified
- [ ] Error handling tested
- [ ] Docker image built
- [ ] Kubernetes deployment created
- [ ] Health checks passing
- [ ] Ready for production

---

## 📈 FILES TO CREATE

### **1. bot_handler.py** (400 lines)
- Telegram bot command handlers
- Message routing
- Command implementations

### **2. webhook_handler.py** (300 lines)
- FastAPI webhook endpoints
- N8N integration
- Error handling

### **3. message_router.py** (200 lines)
- Route messages to workflows
- Response handling
- Queue management

### **4. error_handler.py** (200 lines)
- Error logging
- User notifications
- Admin alerts

### **5. k8s/bot-deployment.yaml** (50 lines)
- Kubernetes deployment config
- Service definition
- Health checks

---

## ⏰ TIMELINE SUMMARY

```
09:00-10:00 (1h) - Bot Setup
10:00-12:00 (2h) - FastAPI Integration  
12:00-14:00 (2h) - Bot Commands
14:00-16:00 (2h) - Real-time Handling
16:00-17:00 (1h) - Testing & Deployment

🌟 17:00 MSK - PHASE 3 COMPLETE!
```

---

## ✅ SUCCESS CRITERIA

- [ ] Bot receives messages from Telegram
- [ ] Commands (/ask, /analyze, /report) working
- [ ] N8N workflows triggered
- [ ] Responses returned to user
- [ ] <2 second response time
- [ ] Zero errors in logs
- [ ] Health checks passing
- [ ] Deployed in Kubernetes
- [ ] Ready for Phase 4 (Testing)

---

## 📄 RESOURCES

- **GitHub Issue:** Create new Issue for Phase 3
- **Previous Phase:** [Phase 2 Activation Guide](TASKS/TASK-001-PHASE-2-ACTIVATION-GUIDE.md)
- **Project Status:** [PROJECT_STATUS.md](PROJECT_STATUS.md)
- **API Status:** [DEPLOYMENT/API_DEPLOYMENT_VERIFICATION.md](DEPLOYMENT/API_DEPLOYMENT_VERIFICATION.md)

---

**Status:** 🟢 READY TO START

**Start Time:** Dec 8, 2025, 09:00 MSK

**Expected Completion:** Dec 8, 2025, 17:00 MSK

**Next Phase:** Phase 4 (Testing) - Dec 9
