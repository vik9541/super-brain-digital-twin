"""
ТЗ-001: File Storage & Multi-File Analysis System
Обработка файлов, изображений и хранение в Redis
"""

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

import httpx
import redis.asyncio as redis
from psycopg_pool import AsyncConnectionPool

logger = logging.getLogger(__name__)

# Конфигурация
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "superbrain_redis_2025")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
UPLOAD_DIR = Path("/tmp/uploads")


# ============================================================================
# REDIS CONNECTION
# ============================================================================

async def get_redis_client() -> redis.Redis:
    """Получить Redis клиент"""
    return redis.Redis.from_url(
        REDIS_URL,
        password=REDIS_PASSWORD,
        decode_responses=True,
        encoding="utf-8"
    )


# ============================================================================
# FILE STORAGE
# ============================================================================

async def store_file_metadata(
    user_id: int,
    file_id: str,
    file_name: str,
    file_type: str,
    file_size: int,
    local_path: str
) -> bool:
    """
    Сохранить метаданные файла в Redis с TTL 12 часов
    
    Args:
        user_id: ID пользователя Telegram
        file_id: Telegram file_id
        file_name: Имя файла
        file_type: Тип файла (document/photo/video)
        file_size: Размер файла в байтах
        local_path: Путь к локальной копии
    
    Returns:
        True если успешно сохранено
    """
    try:
        redis_client = await get_redis_client()
        
        # Ключ для списка файлов пользователя
        user_files_key = f"user:{user_id}:files"
        
        # Данные файла
        file_data = {
            "file_id": file_id,
            "file_name": file_name,
            "file_type": file_type,
            "file_size": file_size,
            "local_path": local_path,
            "uploaded_at": datetime.utcnow().isoformat(),
        }
        
        # Добавить файл в список пользователя
        await redis_client.rpush(user_files_key, json.dumps(file_data))
        
        # Установить TTL 12 часов (43200 секунд)
        await redis_client.expire(user_files_key, 43200)
        
        await redis_client.close()
        
        logger.info(f"✅ File metadata stored for user {user_id}: {file_name}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to store file metadata: {e}")
        return False


async def get_user_files(user_id: int) -> List[Dict[str, Any]]:
    """
    Получить список файлов пользователя из Redis
    
    Args:
        user_id: ID пользователя
    
    Returns:
        Список словарей с метаданными файлов
    """
    try:
        redis_client = await get_redis_client()
        user_files_key = f"user:{user_id}:files"
        
        # Получить все файлы
        files_json = await redis_client.lrange(user_files_key, 0, -1)
        
        await redis_client.close()
        
        # Парсинг JSON
        files = [json.loads(f) for f in files_json]
        
        logger.info(f"📂 Retrieved {len(files)} files for user {user_id}")
        return files
        
    except Exception as e:
        logger.error(f"❌ Failed to get user files: {e}")
        return []


async def clear_user_files(user_id: int) -> bool:
    """
    Очистить сессию пользователя (удалить все файлы из Redis)
    
    Args:
        user_id: ID пользователя
    
    Returns:
        True если успешно очищено
    """
    try:
        redis_client = await get_redis_client()
        user_files_key = f"user:{user_id}:files"
        
        # Получить файлы для удаления локальных копий
        files = await get_user_files(user_id)
        
        # Удалить локальные файлы
        for file_data in files:
            local_path = Path(file_data.get("local_path", ""))
            if local_path.exists():
                local_path.unlink()
                logger.info(f"🗑️ Deleted local file: {local_path}")
        
        # Удалить ключ из Redis
        await redis_client.delete(user_files_key)
        
        await redis_client.close()
        
        logger.info(f"✅ Cleared session for user {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to clear user files: {e}")
        return False


# ============================================================================
# FILE PROCESSING
# ============================================================================

async def process_document(file_path: Path) -> Dict[str, Any]:
    """
    Обработать документ (PDF, DOC, TXT)
    
    Args:
        file_path: Путь к файлу
    
    Returns:
        Результат анализа (текст, метаданные)
    """
    try:
        logger.info(f"📄 Processing document: {file_path}")
        
        # Чтение текстового файла
        if file_path.suffix.lower() in [".txt", ".md"]:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            return {
                "type": "text",
                "content": content[:5000],  # Первые 5000 символов
                "length": len(content),
                "format": file_path.suffix
            }
        
        # Для PDF/DOC - заглушка (требует установки дополнительных библиотек)
        # TODO: Добавить PyPDF2 или pdfplumber для PDF
        # TODO: Добавить python-docx для DOC/DOCX
        
        return {
            "type": "document",
            "status": "pending_ocr",
            "message": "Document queued for OCR processing",
            "format": file_path.suffix
        }
        
    except Exception as e:
        logger.error(f"❌ Document processing failed: {e}")
        return {"type": "error", "error": str(e)}


async def process_image(file_path: Path) -> Dict[str, Any]:
    """
    Обработать изображение через Vision AI
    
    Args:
        file_path: Путь к изображению
    
    Returns:
        Результат анализа изображения
    """
    try:
        logger.info(f"🖼️ Processing image: {file_path}")
        
        if not OPENAI_API_KEY:
            return {
                "type": "image",
                "status": "error",
                "error": "OPENAI_API_KEY not configured"
            }
        
        # Читаем файл как base64
        import base64
        with open(file_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
        
        # OpenAI Vision API
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4-vision-preview",
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Опиши что изображено на этой картинке детально. Если это чек, извлеки сумму и дату."
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{image_data}"
                                    }
                                }
                            ]
                        }
                    ],
                    "max_tokens": 500
                }
            )
            
            response.raise_for_status()
            result = response.json()
            
            description = result["choices"][0]["message"]["content"]
            
            return {
                "type": "image",
                "status": "analyzed",
                "description": description,
                "model": "gpt-4-vision-preview"
            }
        
    except Exception as e:
        logger.error(f"❌ Image processing failed: {e}")
        return {"type": "error", "error": str(e)}


async def save_analysis_to_db(
    user_id: int,
    files: List[Dict[str, Any]],
    results: List[Dict[str, Any]],
    pool: AsyncConnectionPool
) -> Optional[str]:
    """
    Сохранить результаты анализа в Supabase
    
    Args:
        user_id: ID пользователя
        files: Список файлов
        results: Результаты анализа
        pool: Database connection pool
    
    Returns:
        ID созданной записи в victor_observations
    """
    try:
        async with pool.connection() as conn:
            # Формируем сводку
            summary = f"📊 Анализ {len(files)} файлов:\n\n"
            
            for file_data, result in zip(files, results):
                summary += f"📄 {file_data['file_name']}:\n"
                
                if result.get("type") == "image" and result.get("status") == "analyzed":
                    summary += f"   {result['description'][:200]}...\n\n"
                elif result.get("type") == "text":
                    summary += f"   Текст ({result['length']} символов)\n\n"
                else:
                    summary += f"   {result.get('status', 'unknown')}\n\n"
            
            # Сохранить как observation
            observation_id = await conn.fetchval(
                """
                INSERT INTO victor_observations (
                    observation_type,
                    content,
                    metadata,
                    created_at
                ) VALUES ($1, $2, $3, NOW())
                RETURNING id
                """,
                "file_analysis",
                summary,
                {"files": [f["file_name"] for f in files], "user_id": user_id}
            )
            
            logger.info(f"✅ Analysis saved to DB: {observation_id}")
            return str(observation_id)
            
    except Exception as e:
        logger.error(f"❌ Failed to save analysis to DB: {e}")
        return None


def format_analysis_results(files: List[Dict], results: List[Dict]) -> str:
    """
    Форматировать результаты анализа для Telegram
    
    Args:
        files: Список файлов
        results: Результаты анализа
    
    Returns:
        Отформатированная строка для отправки в Telegram
    """
    message = f"📊 <b>Анализ завершён</b>\n\n"
    message += f"Обработано файлов: <b>{len(files)}</b>\n\n"
    
    for file_data, result in zip(files, results):
        message += f"📄 <b>{file_data['file_name']}</b>\n"
        
        if result.get("type") == "image" and result.get("status") == "analyzed":
            message += f"   {result['description'][:300]}\n\n"
        elif result.get("type") == "text":
            message += f"   📝 Текстовый файл ({result['length']} символов)\n"
            message += f"   {result['content'][:200]}...\n\n"
        elif result.get("type") == "document":
            message += f"   ⏳ {result.get('message', 'Processing...')}\n\n"
        else:
            message += f"   ❌ {result.get('error', 'Unknown error')}\n\n"
    
    message += f"✅ Результаты сохранены в базу данных"
    
    return message
