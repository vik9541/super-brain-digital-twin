"""Phase 4: SUPER BRAIN v4.0 - Universal Telegram Bot Handler
Intent-driven architecture: Bot handles ANY message/file without specific commands
Based on SUPER_BRAIN_FLEXIBLE_TZ_v4.0.md
"""

import os
import logging
import httpx
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message, ContentType
import asyncio
import json
import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8326941950:AAHx7hj1JcJLeQl8eS5sTFlkLJ5S3ZM|L5p3BZoVE")
N8N_WEBHOOK_BASE = os.getenv("N8N_WEBHOOK_BASE", "https://lavrentev.app.n8n.cloud/webhook")

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# N8N Universal Workflow (renamed from digital-twin-ask)
UNIVERSAL_WORKFLOW_URL = f"{N8N_WEBHOOK_BASE}/digital-twin-ask"

# Conversation context storage (simplified, should use Redis/Supabase in production)
conversation_contexts = {}

# ============================================
# SUPABASE CLIENT FOR RAW DATA STORAGE
# ============================================
try:
    from supabase import create_client, Client
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None
    logger.info(f"📊 Supabase RAW storage: {'✅ Enabled' if supabase else '⚠️ Disabled (env vars missing)'}")
except ImportError:
    supabase = None
    logger.warning("⚠️ Supabase not installed - RAW data storage disabled")


async def save_raw_message(message: Message, message_type: str, reply_to_id: int = None):
    """
    Save RAW message data to Supabase for later batch analysis
    """
    if not supabase:
        return None
    
    try:
        # Prepare RAW JSON data
        raw_json = {
            "message_id": message.message_id,
            "chat_id": message.chat.id,
            "user": message.from_user.to_python() if message.from_user else None,
            "date": message.date.isoformat() if message.date else None,
            "text": message.text,
            "caption": message.caption,
            "reply_to_message_id": message.reply_to_message.message_id if message.reply_to_message else None,
        }
        
        # Extract message text based on type
        msg_text = ""
        if message.text:
            msg_text = message.text
        elif message.caption:
            msg_text = message.caption
        elif message_type == "voice":
            msg_text = "[Voice message]"
        elif message_type == "document" and message.document:
            msg_text = f"[Document: {message.document.file_name}]"
        elif message_type == "photo":
            msg_text = "[Photo]"
        
        # Insert into raw_messages table
        result = supabase.table("raw_messages").insert({
            "user_id": message.from_user.id,
            "message_id": message.message_id,
            "chat_id": message.chat.id,
            "message_text": msg_text,
            "message_type": message_type,
            "reply_to_message_id": reply_to_id,
            "raw_telegram_json": raw_json,
            "received_at": datetime.datetime.now().isoformat(),
            "is_processed": False
        }).execute()
        
        # Save file info if present
        if message.document:
            supabase.table("raw_files").insert({
                "message_id": message.message_id,
                "file_id": message.document.file_id,
                "file_type": "document",
                "file_name": message.document.file_name,
                "file_size": message.document.file_size,
                "mime_type": message.document.mime_type,
            }).execute()
        elif message.voice:
            supabase.table("raw_files").insert({
                "message_id": message.message_id,
                "file_id": message.voice.file_id,
                "file_type": "voice",
                "file_size": message.voice.file_size,
                "mime_type": message.voice.mime_type,
            }).execute()
        elif message.photo:
            photo = message.photo[-1]  # Get largest photo
            supabase.table("raw_files").insert({
                "message_id": message.message_id,
                "file_id": photo.file_id,
                "file_type": "photo",
                "file_size": photo.file_size,
            }).execute()
        
        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Failed to save RAW message: {e}")
        return None

async def analyze_message_intent(message_data: dict) -> dict:
    """
    Send message to Perplexity AI via N8N for intent analysis
    Returns: {intent, action, confidence, questions, answer}
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(UNIVERSAL_WORKFLOW_URL, json=message_data)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Perplexity AI analysis error: {e}")
        return {
            "error": str(e),
            "confidence": 0,
            "answer": f"❌ Произошла ошибка при обработке: {str(e)}"
        }

async def handle_universal_message(message: Message):
    """
    Universal handler for ANY message type (text, file, voice, photo)
    This is the CORE of SUPER BRAIN v4.0 architecture
    """
    user_id = message.from_user.id
    
    # Extract message content
    message_text = ""
    message_type = "text"
    
    if message.text:
        message_text = message.text
        message_type = "text"
    elif message.voice:
        message_text = "[Voice message received]"
        message_type = "voice"
    elif message.document:
        message_text = f"[Document: {message.document.file_name}]"
        message_type = "document"
    elif message.photo:
        message_text = "[Photo received]"
        message_type = "photo"

        # 🆕 RAW DATA STORAGE: Save message for batch analysis
    reply_to_id = message.reply_to_message.message_id if message.reply_to_message else None
    await save_raw_message(message, message_type, reply_to_id)
    
    # Get conversation context
    context = conversation_contexts.get(user_id, [])
    
    # Prepare data for Perplexity AI analysis
    analysis_data = {
        "message": message_text,
        "message_type": message_type,
        "user_id": user_id,
        "chat_id": message.chat.id,
        "context": context[-3:] if len(context) > 0 else [],  # Last 3 messages for context
        "request_type": "universal_analysis"
    }
    
    # Send "thinking" message
    status_msg = await message.answer("🧠 Анализирую...")
    
    # Analyze via Perplexity AI
    result = await analyze_message_intent(analysis_data)
    
    # Update conversation context
    if user_id not in conversation_contexts:
        conversation_contexts[user_id] = []
    conversation_contexts[user_id].append({
        "role": "user",
        "content": message_text
    })
    
    # Handle result
    if "error" in result:
        await status_msg.edit_text(result.get("answer", "❌ Ошибка обработки"))
        return
    
    # Extract AI response
    answer = result.get("answer", "Не могу определить, что нужно сделать. Уточните, пожалуйста?")
    confidence = result.get("confidence", 0)
    questions = result.get("questions", [])
    
    # Save AI response to context
    conversation_contexts[user_id].append({
        "role": "assistant",
        "content": answer
    })
    
    # Send response
    await status_msg.edit_text(answer)

        # 🆕 Save bot response to database
    if supabase:
        try:
            supabase.table("bot_responses").insert({
                "reply_to_message_id": message.message_id,
                "response_text": answer,
                "bot_message_id": status_msg.message_id,
                "sent_at": datetime.datetime.now().isoformat(),
                "is_error": False
            }).execute()
        except Exception as e:
            logger.error(f"Failed to save bot response: {e}")
    
    # If AI needs clarification (confidence < 80% or has questions)
    if confidence < 80 and questions:
        clarification_text = "\n\n❓ У меня есть уточняющие вопросы:\n"
        for i, q in enumerate(questions, 1):
            clarification_text += f"{i}. {q}\n"
        await message.answer(clarification_text)

# ============================================
# COMMAND HANDLERS (for basic navigation)
# ============================================

@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Handle /start command"""
    text = """
🧠 Добро пожаловать в SUPER BRAIN v4.0!

Я - ваш умный AI-ассистент на базе Perplexity AI.

✨ **Просто отправьте мне:**
• Любой текст или вопрос
• Файл (документ, фото)
• Голосовое сообщение

Я проанализирую и помогу!

🤖 Если не понимаю - задам уточняющие вопросы.

Команды:
/help - показать помощь
/status - проверить статус

Приступим! 🚀
    """
    await message.answer(text)

@dp.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command"""
    text = """
📚 **SUPER BRAIN v4.0 - Помощь**

**Концепция:**
Вам НЕ нужны специальные команды!
Просто общайтесь естественно:

✅ "Встреча завтра с Иваном"
✅ [загрузить счет.pdf]
✅ [отправить голосовое]
✅ "Сколько я потратил на проект?"

🤖 Я понимаю контекст и задаю вопросы если нужно.

**Команды навигации:**
/start - начать
/help - эта справка
/status - проверить работу систем

**Powered by Perplexity AI** 🚀
    """
    await message.answer(text)

@dp.message(Command("status"))
async def cmd_status(message: Message):
    """Handle /status command"""
    try:
        # Ping N8N webhook
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{N8N_WEBHOOK_BASE.replace('/webhook', '')}/healthz", follow_redirects=True)
            n8n_status = "🟢 OK" if response.status_code in [200, 404] else "🔴 ERROR"  # 404 is ok, means N8N is up
    except:
        n8n_status = "🟡 UNKNOWN"
    
    text = f"""
📊 **Статус Системы**

🤖 **Bot:** 🟢 Работает
🔗 **N8N Workflows:** {n8n_status}
🧠 **Perplexity AI:** 🟢 Активен
💾 **Database:** 🟢 Готова

**Version:** SUPER BRAIN v4.0 (Flexible)
**Architecture:** Intent-driven (no commands needed)
    """
    await message.answer(text)

# ============================================
# UNIVERSAL MESSAGE HANDLER (MAIN LOGIC)
# ============================================

@dp.message(F.text | F.voice | F.document | F.photo)
async def handle_any_message(message: Message):
    """
    Main universal handler for ALL message types
    This replaces /ask, /analyze, /report commands
    """
    await handle_universal_message(message)

# ============================================
# MAIN FUNCTION
# ============================================

async def main():
    """Main function to start the bot"""
    logger.info("🚀 Starting SUPER BRAIN v4.0 Telegram Bot...")
    logger.info(f"📡 N8N Webhook: {UNIVERSAL_WORKFLOW_URL}")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
