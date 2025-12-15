"""
VICTOR BOT v2.0 - Universal Sensor API
Главный роутер для Telegram Webhook и обработки всех типов сообщений
"""

import asyncio
import logging
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

import httpx
from fastapi import APIRouter, BackgroundTasks, HTTPException
from psycopg_pool import AsyncConnectionPool
from pydantic import BaseModel, Field

# ТЗ-001: File Storage & Multi-File Analysis
from api import file_processor

# Windows fix для psycopg3 async
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
VICTOR_CHAT_ID = int(os.getenv("VICTOR_CHAT_ID", "0"))
DATABASE_URL = os.getenv("DATABASE_URL")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_KEY")  # Используем тот же ключ для REST API
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET", "victor-files")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ============================================================================
# PYDANTIC MODELS
# ============================================================================


class TelegramUser(BaseModel):
    id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None


class TelegramChat(BaseModel):
    id: int
    type: str


class TelegramPhotoSize(BaseModel):
    file_id: str
    file_unique_id: str
    file_size: Optional[int] = None
    width: int
    height: int


class TelegramVideo(BaseModel):
    file_id: str
    file_unique_id: str
    file_size: Optional[int] = None
    width: int
    height: int
    duration: int
    mime_type: Optional[str] = None


class TelegramAudio(BaseModel):
    file_id: str
    file_unique_id: str
    file_size: Optional[int] = None
    duration: int
    mime_type: Optional[str] = None
    file_name: Optional[str] = None
    performer: Optional[str] = None
    title: Optional[str] = None


class TelegramVoice(BaseModel):
    file_id: str
    file_unique_id: str
    file_size: Optional[int] = None
    duration: int
    mime_type: Optional[str] = None


class TelegramDocument(BaseModel):
    file_id: str
    file_unique_id: str
    file_name: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None


class TelegramContact(BaseModel):
    phone_number: str
    first_name: str
    last_name: Optional[str] = None
    user_id: Optional[int] = None
    vcard: Optional[str] = None


class TelegramLocation(BaseModel):
    latitude: float
    longitude: float
    horizontal_accuracy: Optional[float] = None


class TelegramMessage(BaseModel):
    message_id: int
    from_: TelegramUser = Field(..., alias="from")
    chat: TelegramChat
    date: int
    text: Optional[str] = None
    photo: Optional[List[TelegramPhotoSize]] = None
    video: Optional[TelegramVideo] = None
    audio: Optional[TelegramAudio] = None
    voice: Optional[TelegramVoice] = None
    document: Optional[TelegramDocument] = None
    contact: Optional[TelegramContact] = None
    location: Optional[TelegramLocation] = None
    caption: Optional[str] = None


class TelegramUpdate(BaseModel):
    update_id: int
    message: Optional[TelegramMessage] = None


class ClarifyRequest(BaseModel):
    answer: str
    metadata: Optional[Dict[str, Any]] = None


# ============================================================================
# DATABASE CONNECTION
# ============================================================================

# Глобальный DB pool (создается один раз при старте)
_db_pool: Optional[AsyncConnectionPool] = None


async def get_db_pool():
    """Получить connection pool к БД (psycopg3 async)"""
    global _db_pool

    if _db_pool is None:
        if not DATABASE_URL:
            raise ValueError("DATABASE_URL not configured")

        # psycopg3 AsyncConnectionPool (совместим с PgBouncer)
        _db_pool = AsyncConnectionPool(
            DATABASE_URL,
            min_size=1,
            max_size=5,
            kwargs={"options": "-c jit=off"},  # PgBouncer compatibility
        )
        await _db_pool.open()
        logger.info("✅ psycopg3 AsyncConnectionPool created")

    return _db_pool


# ============================================================================
# HELPER FUNCTIONS - psycopg3 compatibility
# ============================================================================


async def fetchval(conn, query: str, *args):
    """Helper для получения одного значения (эквивалент asyncpg.fetchval)"""
    async with conn.cursor() as cur:
        await cur.execute(query, args)
        row = await cur.fetchone()
        return row[0] if row else None


async def fetchrow(conn, query: str, *args):
    """Helper для получения одной строки (эквивалент asyncpg.fetchrow)"""
    async with conn.cursor() as cur:
        await cur.execute(query, args)
        row = await cur.fetchone()
        if row:
            # Преобразуем в dict для обратной совместимости
            return dict(zip([desc[0] for desc in cur.description], row))
        return None


async def fetch(conn, query: str, *args):
    """Helper для получения всех строк (эквивалент asyncpg.fetch)"""
    async with conn.cursor() as cur:
        await cur.execute(query, args)
        rows = await cur.fetchall()
        if rows:
            # Преобразуем в list[dict]
            return [dict(zip([desc[0] for desc in cur.description], row)) for row in rows]
        return []


async def execute(conn, query: str, *args):
    """Helper для выполнения команды (эквивалент asyncpg.execute)"""
    async with conn.cursor() as cur:
        await cur.execute(query, args)


async def save_to_supabase_rest(table: str, data: dict) -> bool:
    """
    Сохранить данные в Supabase через REST API (обходной путь для pooler)
    """
    try:
        url = f"{SUPABASE_URL}/rest/v1/{table}"
        headers = {
            "apikey": SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=headers, timeout=10.0)
            response.raise_for_status()
            logger.info(f"✅ REST API: Saved to {table}: {data.get('id', 'unknown')}")
            return True

    except Exception as e:
        logger.error(f"❌ REST API save failed for {table}: {e}")
        return False


async def send_to_telegram(
    text: str, to_user_id: int, reply_markup: Optional[Dict[str, Any]] = None
):
    """
    Отправить сообщение в Telegram

    Args:
        text: Текст сообщения
        to_user_id: ID чата получателя
        reply_markup: Клавиатура для ответа (опционально)
    """
    chat_id = to_user_id

    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not configured")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}

    if reply_markup:
        payload["reply_markup"] = reply_markup

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, timeout=10.0)
            response.raise_for_status()
            logger.info(f"✅ Sent to Telegram: {text[:50]}...")
            return response.json()
        except Exception as e:
            logger.error(f"❌ Failed to send to Telegram: {e}")
            raise


async def ask_victor(
    question: str,
    chat_id: int,
    options: Optional[List[str]] = None,
    inbox_id: Optional[UUID] = None,
    needs_text: bool = False,
):
    """
    Спросить Виктора через Telegram с кнопками или текстовым ответом
    """
    markup = None

    if options and not needs_text:
        # Создаём inline кнопки
        markup = {
            "inline_keyboard": [
                [{"text": opt, "callback_data": f"clarify:{inbox_id}:{opt}"}] for opt in options
            ]
        }

    await send_to_telegram(question, chat_id, markup)


def classify_text(text: str) -> str:
    """
    Классифицировать текст по типам наблюдений
    """
    text_lower = text.lower()

    # Встреча
    if any(word in text_lower for word in ["встреча", "встретился", "звонок", "созвон"]):
        return "meeting"

    # Задача
    if any(word in text_lower for word in ["нужно", "сделать", "задача", "todo", "выполнить"]):
        return "task"

    # Идея
    if any(word in text_lower for word in ["идея", "может быть", "интересно", "подумать"]):
        return "idea"

    # Расход
    if any(word in text_lower for word in ["купил", "оплатил", "потратил", "₽", "руб"]):
        return "expense"

    # Решение
    if any(word in text_lower for word in ["решил", "выбрал", "определился", "принял решение"]):
        return "decision"

    # По умолчанию - заметка
    return "note"


async def download_telegram_file(file_id: str) -> tuple[str, bytes]:
    """
    Скачать файл из Telegram и вернуть (file_path, file_bytes)
    """
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN not configured")

    # 1. Получить file_path
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getFile"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params={"file_id": file_id})
        response.raise_for_status()
        result = response.json()
        file_path = result["result"]["file_path"]

    # 2. Скачать файл
    download_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"
    async with httpx.AsyncClient() as client:
        response = await client.get(download_url)
        response.raise_for_status()
        file_bytes = response.content

    logger.info(f"✅ Downloaded file: {file_path} ({len(file_bytes)} bytes)")
    return file_path, file_bytes


async def save_file_to_storage(file_bytes: bytes, file_name: str) -> str:
    """
    Сохранить файл в Supabase Storage и вернуть публичный URL

    TODO: Implement actual Supabase Storage upload
    Сейчас возвращаем заглушку
    """
    # Для MVP сохраняем локально
    file_id = str(uuid4())
    local_path = f"./uploads/{file_id}_{file_name}"

    os.makedirs("./uploads", exist_ok=True)

    with open(local_path, "wb") as f:
        f.write(file_bytes)

    # В production здесь будет:
    # - Upload to Supabase Storage
    # - Return public URL

    public_url = f"/files/{file_id}_{file_name}"
    logger.info(f"✅ Saved file to: {public_url}")

    return public_url


# ============================================================================
# BOT HANDLERS
# ============================================================================


# ============================================================================
# ТЗ-001: FILE STORAGE COMMANDS
# ============================================================================


async def handle_add_command(sender_chat_id: int):
    """
    Команда /add - Инструкция пользователю отправить файлы
    """
    message = (
        "📁 <b>Режим сбора файлов активирован</b>\n\n"
        "Отправьте один или несколько файлов:\n"
        "• Фотографии (🖼️)\n"
        "• Документы PDF, DOC, TXT (📝)\n"
        "• Видео (🎥)\n\n"
        "Когда закончите, используйте:\n"
        "/files - посмотреть список\n"
        "/analyze - начать анализ\n"
        "/clear - очистить сессию\n\n"
        "🕒 Файлы хранятся 12 часов"
    )
    await send_to_telegram(message, sender_chat_id)


async def handle_files_command(sender_chat_id: int):
    """
    Команда /files - Показать список файлов в сессии
    """
    files = await file_processor.get_user_files(sender_chat_id)

    if not files:
        message = "📂 <b>Сессия пуста</b>\n\nИспользуйте /add чтобы добавить файлы"
    else:
        total_size = sum(f.get("file_size", 0) for f in files)
        message = f"📁 <b>Файлы в сессии</b> ({len(files)})\n\n"

        for i, file_data in enumerate(files, 1):
            file_name = file_data.get("file_name", "unknown")
            file_type = file_data.get("file_type", "file")
            file_size_mb = file_data.get("file_size", 0) / 1024 / 1024

            icon = "📝" if file_type == "document" else "🖼️" if file_type == "photo" else "🎥"

            message += f"{i}. {icon} <code>{file_name}</code> ({file_size_mb:.2f} MB)\n"

        message += f"\n📊 Всего: {total_size / 1024 / 1024:.2f} MB\n\n"
        message += "Используйте /analyze для обработки"

    await send_to_telegram(message, sender_chat_id)


async def handle_analyze_command(sender_chat_id: int, pool: Optional[AsyncConnectionPool]):
    """
    Команда /analyze - Обработать все файлы через AI
    """
    files = await file_processor.get_user_files(sender_chat_id)

    if not files:
        await send_to_telegram("⚠️ Нет файлов для анализа. Используйте /add", sender_chat_id)
        return

    # Отправить уведомление о начале анализа
    await send_to_telegram(f"🔍 <b>Начинаю анализ...</b>\n\nФайлов: {len(files)}", sender_chat_id)

    # Обработать каждый файл
    results = []

    for file_data in files:
        local_path = Path(file_data.get("local_path", ""))
        file_type = file_data.get("file_type")

        if file_type == "photo":
            result = await file_processor.process_image(local_path)
        elif file_type == "document":
            result = await file_processor.process_document(local_path)
        else:
            result = {"type": "unknown", "status": "skipped"}

        results.append(result)

    # Сохранить в базу данных
    if pool:
        await file_processor.save_analysis_to_db(sender_chat_id, files, results, pool)

    # Отправить результаты
    formatted_results = file_processor.format_analysis_results(files, results)
    await send_to_telegram(formatted_results, sender_chat_id)

    # Очистить сессию после анализа
    await file_processor.clear_user_files(sender_chat_id)


async def handle_clear_command(sender_chat_id: int):
    """
    Команда /clear - Очистить сессию
    """
    success = await file_processor.clear_user_files(sender_chat_id)

    if success:
        await send_to_telegram("🗑️ <b>Сессия очищена</b>\n\nВсе файлы удалены", sender_chat_id)
    else:
        await send_to_telegram("⚠️ Ошибка очистки сессии", sender_chat_id)


# ============================================================================
# TEXT PROCESSING
# ============================================================================


async def handle_text(
    text: str,
    message_id: int,
    pool: Optional[AsyncConnectionPool] = None,
    sender_chat_id: Optional[int] = None,
):
    """
    Обработка текстового сообщения → observation (REST API версия)
    """
    logger.info(f"📝 Processing text: {text[:50]}...")

    # Классифицировать тип
    obs_type = classify_text(text)

    observation_id = str(uuid.uuid4())

    # Создать observation через REST API
    observation_data = {
        "id": observation_id,
        "type": obs_type,
        "content": text,
        "timestamp": datetime.now().isoformat(),
        "source": "telegram",
    }

    success = await save_to_supabase_rest("victor_observations", observation_data)

    if success:
        # Создать inbox запись
        inbox_data = {
            "id": str(uuid.uuid4()),
            "content_type": "text",
            "content": text,
            "processing_status": "done",
            "telegram_message_id": message_id,
            "linked_observation_id": observation_id,
            "is_processed": True,
        }

        await save_to_supabase_rest("victor_inbox", inbox_data)
        await send_to_telegram(f"✅ Записано как <b>{obs_type}</b>", sender_chat_id)
        logger.info(f"✅ Text saved as observation: {obs_type}")
    else:
        logger.error(f"❌ Failed to save observation")
        await send_to_telegram(
            f"⚠️ Ошибка сохранения, но текст получен: {text[:50]}", sender_chat_id
        )


async def handle_photo(
    photo: List[TelegramPhotoSize],
    caption: Optional[str],
    message_id: int,
    pool: AsyncConnectionPool,
    sender_chat_id: Optional[int] = None,
):
    """
    Обработка фото → сохранение в Redis для последующего анализа (ТЗ-001)
    """
    logger.info(f"📸 Processing photo...")

    # Берём самое большое фото
    largest_photo = max(photo, key=lambda p: p.file_size or 0)

    # Скачиваем файл
    file_path, file_bytes = await download_telegram_file(largest_photo.file_id)

    # ТЗ-001: Сохранить локально в /tmp/uploads/{user_id}/
    upload_dir = Path(f"/tmp/uploads/{sender_chat_id}")
    upload_dir.mkdir(parents=True, exist_ok=True)

    local_file_path = upload_dir / f"photo_{message_id}.jpg"
    with open(local_file_path, "wb") as f:
        f.write(file_bytes)

    # Сохранить метаданные в Redis
    await file_processor.store_file_metadata(
        user_id=sender_chat_id,
        file_id=largest_photo.file_id,
        file_name=f"photo_{message_id}.jpg",
        file_type="photo",
        file_size=largest_photo.file_size or 0,
        local_path=str(local_file_path),
    )

    await send_to_telegram(
        f"✅ Фото добавлено в сессию\\n\\nИспользуйте:\\n/files - посмотреть список\\n/analyze - начать анализ",
        sender_chat_id,
    )

    logger.info(f"✅ Photo stored in Redis session")

    # Сохраняем в storage
    public_url = await save_file_to_storage(file_bytes, "photo.jpg")

    async with pool.connection() as conn:
        # Создать VictorFile
        file_id = await fetchval(
            conn,
            """
            INSERT INTO victor_files (
                original_file_name, file_type, file_size, file_url, file_path,
                telegram_file_id, telegram_file_unique_id, user_description,
                metadata
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            RETURNING id
        """,
            f"photo_{datetime.now().isoformat()}.jpg",
            "image/jpeg",
            largest_photo.file_size or 0,
            public_url,
            file_path,
            largest_photo.file_id,
            largest_photo.file_unique_id,
            caption or "",
            {"width": largest_photo.width, "height": largest_photo.height},
        )

        # Создать inbox
        inbox_id = await fetchval(
            conn,
            """
            INSERT INTO victor_inbox (
                content_type, file_id, processing_status,
                telegram_message_id, user_question
            ) VALUES ($1, $2, $3, $4, $5)
            RETURNING id
        """,
            "file",
            file_id,
            "pending_clarification",
            message_id,
            "Что на фото?",
        )

    # Спросить Виктора
    await ask_victor(
        "📸 Что на фото?",
        chat_id=sender_chat_id,
        options=["чек", "документ", "лицо", "план", "другое"],
        inbox_id=inbox_id,
    )

    logger.info(f"✅ Photo saved, awaiting clarification: {inbox_id}")


async def handle_video(
    video: TelegramVideo,
    caption: Optional[str],
    message_id: int,
    pool: AsyncConnectionPool,
    sender_chat_id: Optional[int] = None,
):
    """
    Обработка видео → спрашиваем описание
    """
    logger.info(f"🎬 Processing video...")

    # Скачать файл
    file_path, file_bytes = await download_telegram_file(video.file_id)

    # Сохранить
    public_url = await save_file_to_storage(file_bytes, "video.mp4")

    async with pool.connection() as conn:
        file_id = await fetchval(
            conn,
            """
            INSERT INTO victor_files (
                original_file_name, file_type, file_size, file_url, file_path,
                telegram_file_id, telegram_file_unique_id, user_description,
                metadata
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            RETURNING id
        """,
            f"video_{datetime.now().isoformat()}.mp4",
            video.mime_type or "video/mp4",
            video.file_size or 0,
            public_url,
            file_path,
            video.file_id,
            video.file_unique_id,
            caption or "",
            {"width": video.width, "height": video.height, "duration": video.duration},
        )

        inbox_id = await fetchval(
            conn,
            """
            INSERT INTO victor_inbox (
                content_type, file_id, processing_status,
                telegram_message_id, user_question
            ) VALUES ($1, $2, $3, $4, $5)
            RETURNING id
        """,
            "file",
            file_id,
            "pending_clarification",
            message_id,
            "Что в видео? (описи)",
        )

    await ask_victor(
        "🎬 Что в видео? Опиши:", chat_id=sender_chat_id, inbox_id=inbox_id, needs_text=True
    )

    logger.info(f"✅ Video saved: {inbox_id}")


async def handle_audio(
    audio: TelegramAudio,
    caption: Optional[str],
    message_id: int,
    pool: AsyncConnectionPool,
    sender_chat_id: Optional[int] = None,
):
    """
    Обработка аудио → автоматически в очередь транскрипции
    """
    logger.info(f"🎙️ Processing audio...")

    file_path, file_bytes = await download_telegram_file(audio.file_id)
    public_url = await save_file_to_storage(file_bytes, audio.file_name or "audio.mp3")

    async with pool.connection() as conn:
        file_id = await fetchval(
            conn,
            """
            INSERT INTO victor_files (
                original_file_name, file_type, file_size, file_url, file_path,
                telegram_file_id, telegram_file_unique_id,
                processing_queue, user_description, metadata
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            RETURNING id
        """,
            audio.file_name or f"audio_{datetime.now().isoformat()}.mp3",
            audio.mime_type or "audio/mpeg",
            audio.file_size or 0,
            public_url,
            file_path,
            audio.file_id,
            audio.file_unique_id,
            "pending_transcription",  # ← Автоматически в очередь!
            caption or "",
            {"duration": audio.duration, "performer": audio.performer, "title": audio.title},
        )

        # Добавить в очередь обработки
        await execute(
            conn,
            """
            INSERT INTO victor_processing_queue (
                file_id, processing_type, priority, status
            ) VALUES ($1, $2, $3, $4)
        """,
            file_id,
            "transcribe_audio",
            7,
            "pending",
        )

        await execute(
            conn,
            """
            INSERT INTO victor_inbox (
                content_type, file_id, processing_status, telegram_message_id
            ) VALUES ($1, $2, $3, $4)
        """,
            "file",
            file_id,
            "processing",
            message_id,
        )

    await send_to_telegram("🎙️ Аудио сохранено. Будет транскрибировано.", sender_chat_id)
    logger.info(f"✅ Audio queued for transcription")


async def handle_voice(
    voice: TelegramVoice,
    caption: Optional[str],
    message_id: int,
    pool: AsyncConnectionPool,
    sender_chat_id: Optional[int] = None,
):
    """
    Обработка голосового → автоматически в очередь
    """
    logger.info(f"🎤 Processing voice message...")

    file_path, file_bytes = await download_telegram_file(voice.file_id)
    public_url = await save_file_to_storage(file_bytes, "voice.ogg")

    async with pool.connection() as conn:
        file_id = await fetchval(
            conn,
            """
            INSERT INTO victor_files (
                original_file_name, file_type, file_size, file_url, file_path,
                telegram_file_id, telegram_file_unique_id,
                processing_queue, metadata
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            RETURNING id
        """,
            f"voice_{datetime.now().isoformat()}.ogg",
            "audio/ogg",
            voice.file_size or 0,
            public_url,
            file_path,
            voice.file_id,
            voice.file_unique_id,
            "pending_transcription",
            {"duration": voice.duration},
        )

        await execute(
            conn,
            """
            INSERT INTO victor_processing_queue (
                file_id, processing_type, priority, status
            ) VALUES ($1, $2, $3, $4)
        """,
            file_id,
            "transcribe_voice",
            8,
            "pending",
        )

        await execute(
            conn,
            """
            INSERT INTO victor_inbox (
                content_type, file_id, processing_status, telegram_message_id
            ) VALUES ($1, $2, $3, $4)
        """,
            "file",
            file_id,
            "processing",
            message_id,
        )

    await send_to_telegram("🎤 Голос записан. Очередь транскрипции.", sender_chat_id)
    logger.info(f"✅ Voice queued")


async def handle_document(
    doc: TelegramDocument,
    caption: Optional[str],
    message_id: int,
    pool: AsyncConnectionPool,
    sender_chat_id: Optional[int] = None,
):
    """
    Обработка документа → сохранение в Redis для последующего анализа (ТЗ-001)
    """
    logger.info(f"📄 Processing document: {doc.file_name}")

    file_path, file_bytes = await download_telegram_file(doc.file_id)

    # ТЗ-001: Сохранить локально
    upload_dir = Path(f"/tmp/uploads/{sender_chat_id}")
    upload_dir.mkdir(parents=True, exist_ok=True)

    local_file_path = upload_dir / doc.file_name
    with open(local_file_path, "wb") as f:
        f.write(file_bytes)

    # Сохранить метаданные в Redis
    await file_processor.store_file_metadata(
        user_id=sender_chat_id,
        file_id=doc.file_id,
        file_name=doc.file_name,
        file_type="document",
        file_size=doc.file_size or 0,
        local_path=str(local_file_path),
    )

    await send_to_telegram(
        f"✅ Документ <code>{doc.file_name}</code> добавлен\\n\\nИспользуйте:\\n/files - посмотреть список\\n/analyze - начать анализ",
        sender_chat_id,
    )

    logger.info(f"✅ Document stored in Redis session")
    public_url = await save_file_to_storage(file_bytes, doc.file_name)

    async with pool.connection() as conn:
        file_id = await fetchval(
            conn,
            """
            INSERT INTO victor_files (
                original_file_name, file_type, file_size, file_url, file_path,
                telegram_file_id, telegram_file_unique_id, user_description
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING id
        """,
            doc.file_name,
            doc.mime_type or "application/octet-stream",
            doc.file_size or 0,
            public_url,
            file_path,
            doc.file_id,
            doc.file_unique_id,
            caption or "",
        )

        inbox_id = await fetchval(
            conn,
            """
            INSERT INTO victor_inbox (
                content_type, file_id, processing_status, telegram_message_id
            ) VALUES ($1, $2, $3, $4)
            RETURNING id
        """,
            "file",
            file_id,
            "pending_clarification",
            message_id,
        )

    # Подбираем опции по расширению
    ext = doc.file_name.split(".")[-1].lower()
    if ext == "pdf":
        suggestions = ["контракт", "счёт-фактура", "отчёт", "другое"]
    elif ext in ["xlsx", "xls", "csv"]:
        suggestions = ["таблица", "отчёт", "смета", "другое"]
    else:
        suggestions = ["документ", "письмо", "отчёт", "другое"]

    await ask_victor(
        f"📄 Документ: <b>{doc.file_name}</b>\nЧто это?",
        chat_id=sender_chat_id,
        options=suggestions,
        inbox_id=inbox_id,
    )

    logger.info(f"✅ Document saved: {inbox_id}")


async def handle_contact(
    contact: TelegramContact,
    message_id: int,
    pool: AsyncConnectionPool,
    sender_chat_id: Optional[int] = None,
):
    """
    Обработка контакта → спрашиваем сохранить
    """
    logger.info(f"👤 Processing contact: {contact.first_name} {contact.phone_number}")

    async with pool.connection() as conn:
        # TODO: Проверить есть ли в БД контактов
        # Пока просто создаём inbox
        inbox_id = await fetchval(
            conn,
            """
            INSERT INTO victor_inbox (
                content_type, content, processing_status, telegram_message_id
            ) VALUES ($1, $2, $3, $4)
            RETURNING id
        """,
            "contact",
            f"{contact.first_name} {contact.last_name or ''} - {contact.phone_number}",
            "pending_clarification",
            message_id,
        )

    await ask_victor(
        f"👤 Новый контакт:\n<b>{contact.first_name} {contact.last_name or ''}</b>\n📞 {contact.phone_number}\n\nСохранить?",
        chat_id=sender_chat_id,
        options=["да", "нет"],
        inbox_id=inbox_id,
    )

    logger.info(f"✅ Contact saved: {inbox_id}")


async def handle_location(
    location: TelegramLocation,
    message_id: int,
    pool: AsyncConnectionPool,
    sender_chat_id: Optional[int] = None,
):
    """
    Обработка геолокации → автоматически в observation
    """
    logger.info(f"📍 Processing location: {location.latitude}, {location.longitude}")

    async with pool.connection() as conn:
        observation_id = await fetchval(
            conn,
            """
            INSERT INTO victor_observations (
                type, content, location, timestamp, source
            ) VALUES ($1, $2, $3, $4, $5)
            RETURNING id
        """,
            "location",
            f"Локация: {location.latitude}, {location.longitude}",
            {"latitude": location.latitude, "longitude": location.longitude},
            datetime.now(),
            "telegram",
        )

        await execute(
            conn,
            """
            INSERT INTO victor_inbox (
                content_type, processing_status, telegram_message_id,
                linked_observation_id, is_processed
            ) VALUES ($1, $2, $3, $4, $5)
        """,
            "location",
            "done",
            message_id,
            observation_id,
            True,
        )

    await send_to_telegram("📍 Локация сохранена", sender_chat_id)
    logger.info(f"✅ Location saved")


# ============================================================================
# API ROUTER
# ============================================================================

router = APIRouter(prefix="/api", tags=["Victor Bot"])


@router.post("/telegram/webhook")
async def telegram_webhook(update: TelegramUpdate, background_tasks: BackgroundTasks):
    """
    🎯 ГЛАВНЫЙ ENDPOINT - Единое окно для всех входящих данных от Виктора
    """
    if not update.message:
        return {"ok": True, "message": "No message in update"}

    message = update.message
    logger.info(f"📥 Received update: {update.update_id}, message_id: {message.message_id}")

    # Получить DB pool (не критично - используем REST API fallback)
    pool = None
    try:
        pool = await get_db_pool()
        logger.info("✅ DB pool obtained successfully")
    except Exception as e:
        logger.error(f"❌ DB pool failed: {e}")
        logger.info(f"📝 Using REST API fallback mode")

    # Получить chat_id отправителя для ответов
    sender_chat_id = message.from_.id

    try:
        # 1️⃣ ОПРЕДЕЛЯЕМ ТИП И ОБРАБАТЫВАЕМ
        if message.text:
            # ТЗ-001: Обработка команд
            if message.text == "/add":
                await handle_add_command(sender_chat_id)
            elif message.text == "/files":
                await handle_files_command(sender_chat_id)
            elif message.text == "/analyze":
                await handle_analyze_command(sender_chat_id, pool)
            elif message.text == "/clear":
                await handle_clear_command(sender_chat_id)
            else:
                # Обычный текст
                await handle_text(message.text, message.message_id, pool, sender_chat_id)

        elif message.photo:
            await handle_photo(
                message.photo, message.caption, message.message_id, pool, sender_chat_id
            )

        elif message.video:
            await handle_video(
                message.video, message.caption, message.message_id, pool, sender_chat_id
            )

        elif message.audio:
            await handle_audio(
                message.audio, message.caption, message.message_id, pool, sender_chat_id
            )

        elif message.voice:
            await handle_voice(
                message.voice, message.caption, message.message_id, pool, sender_chat_id
            )

        elif message.document:
            await handle_document(
                message.document, message.caption, message.message_id, pool, sender_chat_id
            )

        elif message.contact:
            await handle_contact(message.contact, message.message_id, pool, sender_chat_id)

        elif message.location:
            await handle_location(message.location, message.message_id, pool, sender_chat_id)

        else:
            # Неизвестный тип
            logger.warning(f"⚠️ Unknown message type: {message}")
            await ask_victor(
                "❓ Что это? Опиши:", chat_id=sender_chat_id, inbox_id=None, needs_text=True
            )

        return {"ok": True, "status": "processed"}

    except Exception as e:
        logger.error(f"❌ Error processing message: {e}", exc_info=True)
        # НЕ отправляем ошибку Виктору, чтобы не спамить
        # await send_to_telegram(f"❌ Ошибка обработки сообщения: {str(e)}")
        return {"ok": True, "error": str(e)}  # Возвращаем 200 OK чтобы Telegram не ретраил


@router.post("/inbox/{inbox_id}/clarify")
async def clarify_inbox(inbox_id: UUID, request: ClarifyRequest):
    """
    ✅ Получить ответ Виктора на уточнение

    Example:
    POST /api/inbox/abc-123/clarify
    {
      "answer": "receipt",
      "metadata": {"date": "2025-12-14", "total": 450.50}
    }
    """
    logger.info(f"📝 Clarifying inbox {inbox_id}: {request.answer}")

    pool = await get_db_pool()

    try:
        async with pool.connection() as conn:
            # Получить inbox
            inbox = await fetchrow(
                conn,
                """
                SELECT * FROM victor_inbox WHERE id = $1
            """,
                inbox_id,
            )

            if not inbox:
                raise HTTPException(status_code=404, detail="Inbox not found")

            # Обновить категорию файла
            if inbox["content_type"] == "file" and inbox["file_id"]:
                await execute(
                    conn,
                    """
                    UPDATE victor_files
                    SET category = $1,
                        processing_queue = $2
                    WHERE id = $3
                """,
                    request.answer,
                    f"pending_ocr",
                    inbox["file_id"],
                )

                # Добавить в очередь обработки
                await execute(
                    conn,
                    """
                    INSERT INTO victor_processing_queue (
                        file_id, processing_type, priority, status
                    ) VALUES ($1, $2, $3, $4)
                """,
                    inbox["file_id"],
                    "ocr_russian",
                    6,
                    "pending",
                )

            # Обновить inbox
            await execute(
                """
                UPDATE victor_inbox
                SET processing_status = $1,
                    metadata = $2
                WHERE id = $3
            """,
                "processing",
                request.metadata or {},
                inbox_id,
            )

        await send_to_telegram(
            f"✅ Сохранено как '<b>{request.answer}</b>' в систему", VICTOR_CHAT_ID
        )

        return {"status": "saved", "message": f"✅ Сохранено как '{request.answer}' в систему"}

    finally:
        await pool.close()


@router.get("/inbox")
async def list_inbox(
    status: Optional[str] = None, content_type: Optional[str] = None, limit: int = 50
):
    """
    📋 Список элементов inbox

    Example:
    GET /api/inbox?status=pending_clarification
    """
    pool = await get_db_pool()

    try:
        async with pool.connection() as conn:
            query = """
                SELECT 
                    i.*,
                    f.original_file_name,
                    f.category as file_category
                FROM victor_inbox i
                LEFT JOIN victor_files f ON i.file_id = f.id
                WHERE 1=1
            """
            params = []

            if status:
                params.append(status)
                query += f" AND i.processing_status = ${len(params)}"

            if content_type:
                params.append(content_type)
                query += f" AND i.content_type = ${len(params)}"

            params.append(limit)
            query += f" ORDER BY i.created_at DESC LIMIT ${len(params)}"

            rows = await fetch(conn, query, *params)

            items = [dict(row) for row in rows]

            return {"items": items, "count": len(items)}

    finally:
        await pool.close()


@router.get("/health")
async def health_check():
    """Проверка работоспособности API"""
    return {
        "status": "ok",
        "service": "Victor Bot v2.0 API",
        "timestamp": datetime.now().isoformat(),
    }
