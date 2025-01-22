from __future__ import annotations
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message
import time
import asyncio


def rate_limit(limit: int, key=None) -> Callable:
    """
    Decorator for configuring rate limits and keys for handlers.
    """
    def decorator(func: Callable) -> Callable:
        setattr(func, "throttling_rate_limit", limit)
        if key:
            setattr(func, "throttling_key", key)
        return func

    return decorator


class ThrottlingMiddleware(BaseMiddleware):
    """Throttling middleware without Redis."""

    def __init__(self, limit: float = 0.5, key_prefix: str = "antiflood_"):
        super().__init__()
        self.rate_limit = limit
        self.prefix = key_prefix
        self.cache = {}

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        handler_data = data['handler'].callback
        limit = getattr(handler_data, 'throttling_rate_limit', self.rate_limit)
        key = getattr(handler_data, 'throttling_key', f"{self.prefix}_message")
        unique_key = f"{key}_{event.from_user.id}_{event.chat.id}"

        if unique_key not in self.cache:
            self.cache[unique_key] = {"last_call": time.time(), "exceeded_count": 0}
            return await handler(event, data)

        bucket = self.cache[unique_key]
        now = time.time()
        delta = now - bucket["last_call"]
        if delta >= limit:
            bucket["last_call"] = now
            bucket["exceeded_count"] = 0
            return await handler(event, data)
        else:
            bucket["exceeded_count"] += 1
            if bucket["exceeded_count"] <= 2:
                await event.answer(f"Слишком много запросов. Пожалуйста, повторите попытку через {limit - delta:.2f} секунды.")
                return 
                


class CancelHandler(Exception):
    """Custom exception to cancel handler execution."""
    pass

