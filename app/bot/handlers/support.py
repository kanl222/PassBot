from functools import wraps
from typing import Any, Callable
from app.db.crud.users import get_teacher


def is_teacher(func: Callable):
    """Decorator to inject database session into function."""
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        telegram_id = args[0].from_user.id
        if user:= await get_teacher(telegram_id=telegram_id):
            return await func(*args, **kwargs)
    return wrapper


async def _get_teacher(message):
    return await get_teacher(telegram_id=message.from_user.id,relationship=True)