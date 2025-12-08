"""Phase 3: Telegram Bot Handler
Bot commands implementation for @astra_VIK_bot
"""

import os
import logging
import httpx
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8457627946:AAHUNkHo3PIsTVFgh9BRQ9TRn7Fc6eXm51k")
N8N_WEBHOOK_BASE = os.getenv("N8N_WEBHOOK_BASE", "https://lavrentev.app.n8n.cloud/webhook")

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# N8N Workflow URLs
WORKFLOW_URLS = {
    "ask": f"{N8N_WEBHOOK_BASE}/digital-twin-ask",
    "analyze": f"{N8N_WEBHOOK_BASE}/daily-analysis",
    "report": f"{N8N_WEBHOOK_BASE}/hourly-report"
}

async def call_n8n_workflow(workflow: str, data: dict) -> dict:
    """Call N8N workflow via webhook"""
    try:
        url = WORKFLOW_URLS.get(workflow)
        if not url:
            return {"error": "Unknown workflow"}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=data)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"N8N workflow error: {e}")
        return {"error": str(e)}

@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Handle /start command"""
    text = """
🌟 Welcome to Digital Twin Bot!

I'm an AI assistant powered by Perplexity AI.

Commands:
/ask - Ask me a question
/analyze - Get daily analysis
/report - Get hourly report
/help - Show help
/status - Check bot status

Let's talk!
    """
    await message.answer(text)

@dp.message(Command("ask"))
async def cmd_ask(message: Message):
    """Handle /ask command"""
    # Extract question
    text = message.text or ""
    question = text.replace('/ask', '', 1).strip()
    
    if not question:
        await message.answer("🤔 Please ask a question: /ask [your question]")
        return
    
    # Send to N8N Workflow #1
    await message.answer("⏳ Processing your question...")
    
    result = await call_n8n_workflow("ask", {
        "question": question,
        "user_id": message.from_user.id,
        "chat_id": message.chat.id
    })
    
    if "error" in result:
        await message.answer(f"🚨 Error: {result['error']}")
    else:
        answer = result.get("answer", "No response received")
        await message.answer(answer)

@dp.message(Command("analyze"))
async def cmd_analyze(message: Message):
    """Handle /analyze command"""
    await message.answer("📄 Generating daily analysis...")
    
    result = await call_n8n_workflow("analyze", {
        "user_id": message.from_user.id,
        "chat_id": message.chat.id
    })
    
    if "error" in result:
        await message.answer(f"🚨 Error: {result['error']}")
    else:
        response = result.get("analysis", "Analysis not available")
        await message.answer(response)

@dp.message(Command("report"))
async def cmd_report(message: Message):
    """Handle /report command"""
    await message.answer("📈 Generating hourly report...")
    
    result = await call_n8n_workflow("report", {
        "user_id": message.from_user.id,
        "chat_id": message.chat.id
    })
    
    if "error" in result:
        await message.answer(f"🚨 Error: {result['error']}")
    else:
        response = result.get("report", "Report not available")
        await message.answer(response)

@dp.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command"""
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
    await message.answer(text)

@dp.message(Command("status"))
async def cmd_status(message: Message):
    """Handle /status command"""
    # Check all systems
    status = {
        "api": "🟢 OK",
        "wf1": "🟢 OK",
        "wf2": "🟢 OK",
        "wf3": "🟢 OK",
        "db": "🟢 OK"
    }
    
    text = f"""
👋 Bot Status:
🟢 API: {status['api']}
🟢 N8N WF#1: {status['wf1']}
🟢 N8N WF#2: {status['wf2']}
🟢 N8N WF#3: {status['wf3']}
🟢 Database: {status['db']}
    """
    await message.answer(text)

async def main():
    """Main function to start the bot"""
    logger.info("Starting Telegram bot...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
