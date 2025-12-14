"""
SUPER BRAIN v4.0 - Telegram Bot Handler
Universal message processing with Perplexity AI integration
"""

import asyncio
import base64
import datetime
import json
import logging
import os
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

import httpx
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message

# ============================================
# CONFIGURATION
# ============================================

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
N8N_WEBHOOK_BASE = os.getenv("N8N_WEBHOOK_BASE", "https://lavrentev.app.n8n.cloud/webhook")
UNIVERSAL_WORKFLOW_URL = f"{N8N_WEBHOOK_BASE}/universal"
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# In-memory conversation context
conversation_contexts = {}

# ============================================
# SUPABASE CLIENT FOR RAW DATA STORAGE
# ============================================

supabase = None
try:
    from supabase import Client, create_client

    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

    if SUPABASE_URL and SUPABASE_KEY:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info(f"Supabase RAW storage: ENABLED ({SUPABASE_URL})")
    else:
        logger.warning("Supabase: env vars missing - RAW data storage disabled")
except ImportError as e:
    logger.warning(f"Supabase not installed - RAW data storage disabled: {e}")
except Exception as e:
    logger.error(f"Supabase init error: {e}")


# ============================================
# HELPER FUNCTIONS
# ============================================


async def download_file_as_base64(file_id: str, file_type: str = "photo") -> str | None:
    """Download file from Telegram and convert to Base64"""
    try:
        file = await bot.get_file(file_id)
        file_path = file.file_path
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"

        async with httpx.AsyncClient() as client:
            response = await client.get(file_url)
            response.raise_for_status()
            file_bytes = response.content
            base64_data = base64.b64encode(file_bytes).decode("utf-8")
            logger.info(f"Downloaded {file_type}: {len(file_bytes)} bytes")
            return base64_data
    except Exception as e:
        logger.error(f"Failed to download file {file_id}: {e}")
        return None


async def save_raw_message(message: Message, message_type: str, reply_to_id: int | None = None):
    """Save RAW message to Supabase"""
    if not supabase:
        return None

    try:
        raw_json = {
            "message_id": message.message_id,
            "chat_id": message.chat.id,
            "user": message.from_user.model_dump() if message.from_user else None,
            "date": message.date.isoformat() if message.date else None,
            "text": message.text,
            "caption": message.caption,
        }

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
            msg_text = message.caption if message.caption else "[Photo]"

        result = (
            supabase.table("raw_messages")
            .insert(
                {
                    "user_id": message.from_user.id,
                    "message_id": message.message_id,
                    "chat_id": message.chat.id,
                    "message_text": msg_text,
                    "message_type": message_type,
                    "reply_to_message_id": reply_to_id,
                    "raw_telegram_json": raw_json,
                    "received_at": datetime.datetime.now().isoformat(),
                    "is_processed": False,
                }
            )
            .execute()
        )

        return result.data[0] if result.data else None
    except Exception as e:
        logger.error(f"Failed to save RAW message: {e}")
        return None


async def analyze_message_intent(message_data: dict) -> dict:
    """Send message to N8N/Perplexity AI for analysis"""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(UNIVERSAL_WORKFLOW_URL, json=message_data)
            response.raise_for_status()

            if not response.content:
                return {
                    "error": "Empty response",
                    "confidence": 0,
                    "answer": "Пустой ответ от сервера",
                }

            try:
                return response.json()
            except json.JSONDecodeError:
                return {
                    "error": "Invalid JSON",
                    "confidence": 0,
                    "answer": f"Ошибка: {response.text[:200]}",
                }
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        return {"error": str(e), "confidence": 0, "answer": f"Ошибка: {str(e)}"}


async def handle_universal_message(message: Message):
    """Universal handler for ANY message type"""
    user_id = message.from_user.id

    message_text = ""
    message_type = "text"
    file_data = None

    if message.text:
        message_text = message.text
        message_type = "text"
    elif message.voice:
        message_text = "[Voice message]"
        message_type = "voice"
        file_data = await download_file_as_base64(message.voice.file_id, "voice")
    elif message.document:
        message_text = f"[Document: {message.document.file_name}]"
        message_type = "document"
        file_data = await download_file_as_base64(message.document.file_id, "document")
    elif message.photo:
        photo = message.photo[-1]
        message_text = message.caption if message.caption else "[Photo]"
        message_type = "photo"
        file_data = await download_file_as_base64(photo.file_id, "photo")
        if not file_data:
            await message.answer("Не удалось загрузить фото")
            return

    reply_to_id = message.reply_to_message.message_id if message.reply_to_message else None
    await save_raw_message(message, message_type, reply_to_id)

    context = conversation_contexts.get(user_id, [])

    analysis_data = {
        "message": message_text,
        "message_type": message_type,
        "user_id": user_id,
        "chat_id": message.chat.id,
        "context": context[-3:],
        "request_type": "universal_analysis",
    }

    if file_data:
        analysis_data["file_base64"] = file_data
        analysis_data["has_file"] = True

    status_msg = await message.answer("Анализирую...")
    result = await analyze_message_intent(analysis_data)

    if user_id not in conversation_contexts:
        conversation_contexts[user_id] = []
    conversation_contexts[user_id].append({"role": "user", "content": message_text})

    if "error" in result:
        await status_msg.edit_text(result.get("answer", "Ошибка"))
        return

    answer = result.get("answer", "Не понял. Уточните?")
    confidence = result.get("confidence", 0)
    questions = result.get("questions", [])

    conversation_contexts[user_id].append({"role": "assistant", "content": answer})
    await status_msg.edit_text(answer)

    if confidence < 80 and questions:
        clarification = "\n\nУточняющие вопросы:\n"
        for i, q in enumerate(questions, 1):
            clarification += f"{i}. {q}\n"
        await message.answer(clarification)


# ============================================
# COMMAND HANDLERS
# ============================================


@dp.message(Command("start"))
async def cmd_start(message: Message):
    text = """
Добро пожаловать в SUPER BRAIN v4.0!

Я - AI-ассистент на базе Perplexity AI.

Просто отправьте мне:
- Любой текст или вопрос
- Файл (документ, фото)
- Голосовое сообщение

Команды:
/help - помощь
/status - статус систем
"""
    await message.answer(text)


@dp.message(Command("help"))
async def cmd_help(message: Message):
    text = """
SUPER BRAIN v4.0 - Помощь

Вам НЕ нужны команды!
Просто пишите естественно:
- "Встреча завтра с Иваном"
- Загрузите файл
- Отправьте голосовое

/start - начать
/help - помощь
/status - статус
"""
    await message.answer(text)


@dp.message(Command("status"))
async def cmd_status(message: Message):
    n8n_status = "UNKNOWN"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{N8N_WEBHOOK_BASE.replace('/webhook', '')}/healthz", follow_redirects=True
            )
            n8n_status = "OK" if response.status_code in [200, 404] else "ERROR"
    except:
        pass

    supabase_status = "Connected" if supabase else "Disabled"
    perplexity_status = "OK" if PERPLEXITY_API_KEY else "No API Key"

    text = f"""
Статус Системы

Bot: Работает
N8N: {n8n_status}
Perplexity: {perplexity_status}
Database: {supabase_status}

Version: SUPER BRAIN v4.0
"""
    await message.answer(text)


# ============================================
# UNIVERSAL MESSAGE HANDLER
# ============================================


@dp.message(F.text | F.voice | F.document | F.photo)
async def handle_any_message(message: Message):
    await handle_universal_message(message)


# ============================================
# MAIN
# ============================================


async def main():
    logger.info("Starting SUPER BRAIN v4.0...")
    logger.info(f"N8N: {UNIVERSAL_WORKFLOW_URL}")
    logger.info(f"Supabase: {'Enabled' if supabase else 'Disabled'}")
    logger.info(f"Perplexity: {'Enabled' if PERPLEXITY_API_KEY else 'Disabled'}")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
