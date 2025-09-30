from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery
from typing import Callable, Dict, Any, Awaitable
import time


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: float = 0.5):
        self.rate_limit = rate_limit
        self.user_timings = {}

    async def __call__(
            self,
            handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        current_time = time.time()

        if user_id in self.user_timings:
            if current_time - self.user_timings[user_id] < self.rate_limit:
                try:
                    await event.answer("⏱️ Слишком быстро!", show_alert=False)
                except:
                    pass
                return None

        self.user_timings[user_id] = current_time
        return await handler(event, data)
