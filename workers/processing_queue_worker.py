"""
VICTOR BOT v2.0 - Background Processing Queue Worker
Фоновая обработка: OCR, транскрипция, анализ изображений
"""

import asyncio
import io
import logging
import os
from datetime import datetime
from typing import Any, Dict

import asyncpg
import httpx
import pytesseract
from PIL import Image

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

DATABASE_URL = os.getenv("DATABASE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
VICTOR_CHAT_ID = int(os.getenv("VICTOR_CHAT_ID", "0"))
TESSERACT_PATH = os.getenv("TESSERACT_PATH", "/usr/bin/tesseract")

# Настроить Tesseract
if os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

# ============================================================================
# NOTIFICATION HELPERS
# ============================================================================


async def send_telegram_notification(message: str):
    """Отправить уведомление Виктору в Telegram"""
    if not TELEGRAM_BOT_TOKEN or not VICTOR_CHAT_ID:
        logger.warning("Telegram notifications not configured")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    async with httpx.AsyncClient() as client:
        try:
            await client.post(
                url,
                json={"chat_id": VICTOR_CHAT_ID, "text": message, "parse_mode": "HTML"},
                timeout=10.0,
            )
            logger.info(f"✅ Notification sent: {message[:50]}...")
        except Exception as e:
            logger.error(f"❌ Failed to send notification: {e}")


# ============================================================================
# PROCESSING FUNCTIONS
# ============================================================================


async def run_ocr_russian(file_url: str, file_path: str) -> Dict[str, Any]:
    """
    Запустить OCR для распознавания русского текста
    """
    logger.info(f"🔍 Running OCR (Russian) on {file_path}")

    try:
        # Загрузить изображение
        if file_url.startswith("http"):
            async with httpx.AsyncClient() as client:
                response = await client.get(file_url)
                image_bytes = response.content
        else:
            # Локальный файл
            with open(file_path, "rb") as f:
                image_bytes = f.read()

        # Открыть изображение
        image = Image.open(io.BytesIO(image_bytes))

        # Запустить Tesseract OCR
        text = pytesseract.image_to_string(image, lang="rus")

        # Получить confidence
        data = pytesseract.image_to_data(image, lang="rus", output_type=pytesseract.Output.DICT)
        confidences = [int(conf) for conf in data["conf"] if conf != "-1"]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0

        logger.info(f"✅ OCR completed: {len(text)} chars, confidence: {avg_confidence:.1f}%")

        return {
            "text": text.strip(),
            "confidence": avg_confidence / 100,
            "word_count": len(text.split()),
            "char_count": len(text),
            "language": "russian",
        }

    except Exception as e:
        logger.error(f"❌ OCR failed: {e}")
        raise


async def run_ocr_english(file_url: str, file_path: str) -> Dict[str, Any]:
    """OCR для английского текста"""
    logger.info(f"🔍 Running OCR (English) on {file_path}")

    try:
        if file_url.startswith("http"):
            async with httpx.AsyncClient() as client:
                response = await client.get(file_url)
                image_bytes = response.content
        else:
            with open(file_path, "rb") as f:
                image_bytes = f.read()

        image = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(image, lang="eng")

        data = pytesseract.image_to_data(image, lang="eng", output_type=pytesseract.Output.DICT)
        confidences = [int(conf) for conf in data["conf"] if conf != "-1"]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0

        return {
            "text": text.strip(),
            "confidence": avg_confidence / 100,
            "word_count": len(text.split()),
            "language": "english",
        }

    except Exception as e:
        logger.error(f"❌ OCR failed: {e}")
        raise


async def run_transcription(file_url: str, file_path: str) -> Dict[str, Any]:
    """
    Транскрибировать аудио/голос используя OpenAI Whisper
    """
    logger.info(f"🎙️ Running transcription on {file_path}")

    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not configured")

    try:
        # Загрузить файл
        if file_url.startswith("http"):
            async with httpx.AsyncClient() as client:
                response = await client.get(file_url)
                audio_bytes = response.content
        else:
            with open(file_path, "rb") as f:
                audio_bytes = f.read()

        # Вызвать OpenAI Whisper API
        async with httpx.AsyncClient() as client:
            files = {
                "file": ("audio.ogg", audio_bytes, "audio/ogg"),
            }
            data = {"model": "whisper-1", "language": "ru"}

            response = await client.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                files=files,
                data=data,
                timeout=60.0,
            )
            response.raise_for_status()
            result = response.json()

        text = result.get("text", "")

        logger.info(f"✅ Transcription completed: {len(text)} chars")

        return {
            "text": text,
            "language": "russian",
            "duration": result.get("duration"),
            "confidence": 0.95,  # Whisper обычно очень точный
        }

    except Exception as e:
        logger.error(f"❌ Transcription failed: {e}")
        raise


async def run_face_recognition(file_url: str, file_path: str) -> Dict[str, Any]:
    """
    Распознать лица на изображении

    TODO: Implement using face_recognition library or cloud API
    """
    logger.info(f"👤 Running face recognition on {file_path}")

    # Placeholder - будет реализовано позже
    return {"faces_detected": 0, "faces": [], "note": "Face recognition not implemented yet"}


async def run_extract_table(file_url: str, file_path: str) -> Dict[str, Any]:
    """
    Извлечь таблицы из изображения/PDF

    TODO: Implement using tabula-py or similar
    """
    logger.info(f"📊 Extracting tables from {file_path}")

    # Placeholder
    return {"tables_found": 0, "tables": [], "note": "Table extraction not implemented yet"}


async def run_analyze_image(file_url: str, file_path: str) -> Dict[str, Any]:
    """
    Анализировать изображение с помощью GPT-4 Vision
    """
    logger.info(f"🖼️ Analyzing image {file_path}")

    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not configured")

    try:
        # Загрузить изображение
        if file_url.startswith("http"):
            image_url = file_url
        else:
            # Для локальных файлов нужно конвертировать в base64
            import base64

            with open(file_path, "rb") as f:
                image_bytes = f.read()

            image_base64 = base64.b64encode(image_bytes).decode("utf-8")
            image_url = f"data:image/jpeg;base64,{image_base64}"

        # Вызвать GPT-4 Vision
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "gpt-4-vision-preview",
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Опиши подробно что изображено на этом изображении. Если это документ - извлеки текст и структуру.",
                                },
                                {"type": "image_url", "image_url": {"url": image_url}},
                            ],
                        }
                    ],
                    "max_tokens": 1000,
                },
                timeout=60.0,
            )
            response.raise_for_status()
            result = response.json()

        description = result["choices"][0]["message"]["content"]

        logger.info(f"✅ Image analysis completed: {len(description)} chars")

        return {
            "description": description,
            "model": "gpt-4-vision-preview",
            "tokens_used": result.get("usage", {}).get("total_tokens", 0),
        }

    except Exception as e:
        logger.error(f"❌ Image analysis failed: {e}")
        raise


# ============================================================================
# MAIN PROCESSING LOOP
# ============================================================================


async def process_queue_item(conn: asyncpg.Connection, item: dict):
    """
    Обработать один элемент очереди
    """
    item_id = item["id"]
    processing_type = item["processing_type"]
    file_id = item["file_id"]

    logger.info(f"⚙️ Processing {processing_type} for item {item_id}")

    # Обновить статус
    await conn.execute(
        """
        UPDATE victor_processing_queue
        SET status = 'processing', started_at = $1
        WHERE id = $2
    """,
        datetime.now(),
        item_id,
    )

    try:
        # Получить файл
        file_row = await conn.fetchrow(
            """
            SELECT file_url, file_path FROM victor_files WHERE id = $1
        """,
            file_id,
        )

        if not file_row:
            raise ValueError(f"File not found: {file_id}")

        file_url = file_row["file_url"]
        file_path = file_row["file_path"]

        # Выбрать функцию обработки
        if processing_type == "ocr_russian":
            result = await run_ocr_russian(file_url, file_path)
        elif processing_type == "ocr_english":
            result = await run_ocr_english(file_url, file_path)
        elif processing_type in ("transcribe_audio", "transcribe_voice"):
            result = await run_transcription(file_url, file_path)
        elif processing_type == "identify_face":
            result = await run_face_recognition(file_url, file_path)
        elif processing_type == "extract_table":
            result = await run_extract_table(file_url, file_path)
        elif processing_type == "analyze_image":
            result = await run_analyze_image(file_url, file_path)
        else:
            raise ValueError(f"Unknown processing type: {processing_type}")

        # Вычислить время обработки
        duration_ms = int((datetime.now() - item["started_at"]).total_seconds() * 1000)

        # Сохранить результат
        await conn.execute(
            """
            UPDATE victor_processing_queue
            SET status = 'done',
                result = $1,
                completed_at = $2,
                duration_ms = $3
            WHERE id = $4
        """,
            result,
            datetime.now(),
            duration_ms,
            item_id,
        )

        # Обновить файл
        await conn.execute(
            """
            UPDATE victor_files
            SET extracted_data = $1, is_processed = true
            WHERE id = $2
        """,
            result,
            file_id,
        )

        # Уведомить Виктора
        notification = f"✅ <b>Обработано:</b> {processing_type}\n"
        if "text" in result:
            text_preview = result["text"][:200]
            notification += f"\n<i>{text_preview}</i>{'...' if len(result['text']) > 200 else ''}"

        await send_telegram_notification(notification)

        logger.info(f"✅ Processing completed: {item_id}")

    except Exception as e:
        # Обработать ошибку
        retry_count = item["retry_count"] + 1
        max_retries = item["max_retries"]

        if retry_count >= max_retries:
            # Достигнут лимит повторов
            await conn.execute(
                """
                UPDATE victor_processing_queue
                SET status = 'failed',
                    error_message = $1,
                    error_stack_trace = $2,
                    retry_count = $3,
                    completed_at = $4
                WHERE id = $5
            """,
                str(e),
                str(e.__traceback__),
                retry_count,
                datetime.now(),
                item_id,
            )

            await send_telegram_notification(
                f"❌ <b>Ошибка обработки:</b> {processing_type}\n{str(e)}"
            )

            logger.error(f"❌ Processing failed permanently: {item_id}")
        else:
            # Попробовать ещё раз
            await conn.execute(
                """
                UPDATE victor_processing_queue
                SET status = 'pending',
                    retry_count = $1,
                    error_message = $2
                WHERE id = $3
            """,
                retry_count,
                str(e),
                item_id,
            )

            logger.warning(
                f"⚠️ Processing failed, will retry ({retry_count}/{max_retries}): {item_id}"
            )


async def process_queue():
    """
    Основной цикл обработки очереди
    """
    if not DATABASE_URL:
        logger.error("DATABASE_URL not configured")
        return

    pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=3)

    logger.info("🚀 Processing queue worker started")

    try:
        while True:
            async with pool.acquire() as conn:
                # Взять первый pending элемент из очереди (по приоритету)
                item = await conn.fetchrow(
                    """
                    SELECT *
                    FROM victor_processing_queue
                    WHERE status = 'pending'
                    ORDER BY priority DESC, created_at ASC
                    LIMIT 1
                """
                )

                if item:
                    await process_queue_item(conn, dict(item))
                else:
                    # Нет задач - подождать 5 секунд
                    await asyncio.sleep(5)

    except Exception as e:
        logger.error(f"❌ Queue worker error: {e}", exc_info=True)

    finally:
        await pool.close()
        logger.info("🛑 Processing queue worker stopped")


# ============================================================================
# STARTUP
# ============================================================================


async def start_worker():
    """Запустить background worker"""
    logger.info("🎬 Starting Victor Bot v2.0 Processing Queue Worker...")
    await process_queue()


if __name__ == "__main__":
    # Запуск worker'а напрямую
    asyncio.run(start_worker())
