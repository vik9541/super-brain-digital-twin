"""Phase 3: Error Handler
Handles errors, logging, user notifications, and admin alerts
"""

import os
import logging
import traceback
from datetime import datetime
from typing import Dict, Optional, Any
import httpx
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8326941950:AAHxjtILMo9qgPjm1Ii8CSsIZMLSp3B2oVE")
ADMIN_TELEGRAM_ID = os.getenv("ADMIN_TELEGRAM_ID", "123456789")  # Replace with actual admin ID
TELEGRAM_API_BASE = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


class ErrorHandler:
    """Handles errors and notifications"""
    
    def __init__(self):
        self.error_history: Dict[str, Dict] = {}
        self.retry_attempts = {}
        self.max_retries = 3
    
    async def handle_error(self, error: Exception, context: Dict[str, Any]):
        """
        Main error handling method
        Logs error, notifies user, and alerts admin if critical
        """
        try:
            error_id = self._generate_error_id()
            error_data = {
                "error_id": error_id,
                "type": type(error).__name__,
                "message": str(error),
                "traceback": traceback.format_exc(),
                "context": context,
                "timestamp": datetime.now().isoformat()
            }
            
            # Log error
            logger.error(
                f"Error {error_id}: {error_data['type']} - {error_data['message']}",
                extra=context
            )
            
            # Store in history
            self.error_history[error_id] = error_data
            
            # Notify user if chat_id is available
            if "chat_id" in context:
                await self.notify_user_error(
                    context["chat_id"],
                    error,
                    error_id
                )
            
            # Alert admin if critical
            if self._is_critical(error):
                await self.notify_admin(error_data)
            
            return error_id
            
        except Exception as e:
            logger.critical(f"Error in error handler: {e}")
            return None
    
    async def notify_user_error(self, chat_id: int, error: Exception, error_id: str):
        """
        Send user-friendly error message to Telegram user
        """
        try:
            # Create user-friendly message
            error_message = f"🚨 Произошла ошибка\n\nОшибка: {self._get_user_friendly_message(error)}\n\nID ошибки: {error_id}\n\nПожалуйста, попробуйте позже или свяжитесь с поддержкой."
            
            await self._send_telegram_message(chat_id, error_message)
            logger.info(f"User notified about error {error_id}")
            
        except Exception as e:
            logger.error(f"Failed to notify user: {e}")
    
    async def notify_admin(self, error_data: Dict):
        """
        Send detailed error report to admin
        """
        try:
            admin_message = f"""⚠️ CRITICAL ERROR ALERT

Error ID: {error_data['error_id']}
Type: {error_data['type']}
Message: {error_data['message']}
Timestamp: {error_data['timestamp']}

Context:
{self._format_context(error_data['context'])}

Traceback (first 500 chars):
{error_data['traceback'][:500]}
"""
            
            await self._send_telegram_message(
                int(ADMIN_TELEGRAM_ID),
                admin_message
            )
            logger.info(f"Admin notified about error {error_data['error_id']}")
            
        except Exception as e:
            logger.error(f"Failed to notify admin: {e}")
    
    async def retry_failed_request(self, request_id: str, retry_func, max_retries: int = 3):
        """
        Retry failed request with exponential backoff
        """
        attempt = 0
        last_error = None
        
        while attempt < max_retries:
            try:
                logger.info(f"Retry attempt {attempt + 1}/{max_retries} for request {request_id}")
                result = await retry_func()
                logger.info(f"Retry successful for request {request_id}")
                return result
                
            except Exception as e:
                last_error = e
                attempt += 1
                
                if attempt < max_retries:
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    logger.warning(f"Retry failed, waiting {wait_time}s before next attempt")
                    await asyncio.sleep(wait_time)
        
        # All retries failed
        logger.error(f"All {max_retries} retries failed for request {request_id}")
        return {"error": f"Max retries exceeded: {str(last_error)}"}
    
    async def save_error_log(self, error: Exception, context: Dict):
        """
        Save error to database or persistent storage
        For now, just logs it
        """
        error_id = self._generate_error_id()
        logger.error(
            f"Error logged: {error_id}",
            extra={
                "error_type": type(error).__name__,
                "error_message": str(error),
                "context": context
            }
        )
        # TODO: Implement database storage
        return error_id
    
    def _generate_error_id(self) -> str:
        """Generate unique error ID"""
        import uuid
        return f"ERR-{uuid.uuid4().hex[:8].upper()}"
    
    def _is_critical(self, error: Exception) -> bool:
        """Determine if error is critical"""
        critical_types = [
            'DatabaseError',
            'ConnectionError',
            'TimeoutError',
            'AuthenticationError'
        ]
        return type(error).__name__ in critical_types
    
    def _get_user_friendly_message(self, error: Exception) -> str:
        """Convert technical error to user-friendly message"""
        error_type = type(error).__name__
        
        friendly_messages = {
            'TimeoutError': 'Превышено время ожидания ответа',
            'ConnectionError': 'Ошибка соединения с сервером',
            'HTTPException': 'Ошибка обработки запроса',
            'ValueError': 'Некорректные данные',
            'KeyError': 'Отсутствуют необходимые данные'
        }
        
        return friendly_messages.get(error_type, 'Неизвестная ошибка')
    
    def _format_context(self, context: Dict) -> str:
        """Format context for display"""
        lines = []
        for key, value in context.items():
            lines.append(f"  {key}: {value}")
        return "\n".join(lines)
    
    async def _send_telegram_message(self, chat_id: int, text: str) -> bool:
        """Send message via Telegram API"""
        try:
            url = f"{TELEGRAM_API_BASE}/sendMessage"
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    url,
                    json={"chat_id": chat_id, "text": text}
                )
                response.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
    
    def get_error_stats(self) -> Dict:
        """Get error statistics"""
        total = len(self.error_history)
        by_type = {}
        
        for error_data in self.error_history.values():
            error_type = error_data['type']
            by_type[error_type] = by_type.get(error_type, 0) + 1
        
        return {
            "total_errors": total,
            "errors_by_type": by_type,
            "latest_error": list(self.error_history.values())[-1] if total > 0 else None
        }


class ErrorNotifier:
    """Manages error notifications"""
    
    def __init__(self):
        self.notification_queue = []
    
    async def queue_notification(self, notification: Dict):
        """Add notification to queue"""
        self.notification_queue.append(notification)
        logger.info(f"Notification queued: {notification.get('type')}")
    
    async def process_queue(self):
        """Process notification queue"""
        while self.notification_queue:
            notification = self.notification_queue.pop(0)
            await self._send_notification(notification)
    
    async def _send_notification(self, notification: Dict):
        """Send individual notification"""
        # Implement notification sending logic
        logger.info(f"Notification sent: {notification}")


# Global instances
error_handler = ErrorHandler()
error_notifier = ErrorNotifier()


def get_error_handler() -> ErrorHandler:
    """Get global error handler instance"""
    return error_handler


def get_error_notifier() -> ErrorNotifier:
    """Get global error notifier instance"""
    return error_notifier
