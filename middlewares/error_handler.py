import logging
from aiogram import BaseMiddleware
from aiogram.types import Update, ErrorEvent
from typing import Callable, Dict, Any, Awaitable

logger = logging.getLogger(__name__)

class ErrorHandlerMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        try:
            return await handler(event, data)
        except Exception as e:
            logger.error(f"Ошибка при обработке update {event.update_id}: {e}", exc_info=True)
            # Можно отправить уведомление админу или в Sentry
            return None
