from functools import wraps
from typing import Any, Callable
from app.core.settings import ID_ADMIN
from app.db.crud.users import get_teacher
from aiogram.types import Message

def is_teacher(func: Callable):
    """Decorator to inject database session into function."""
    @wraps(func)
    async def wrapper(message: Message,*args, **kwargs) -> Any:
        if await get_teacher(telegram_id=message.from_user.id):
            return await func(message,*args, **kwargs)
    return wrapper

def is_teacher_of_data(func: Callable):
    """Decorator to inject database session into function."""
    @wraps(func)
    async def wrapper(message: Message,*args, **kwargs) -> Any:
        if teacher:=await get_teacher(telegram_id=message.from_user.id):
            if teacher.is_data_parsed:
                return await func(message,*args, **kwargs)
            else:
                return await message.reply("Пожалуйста, сначала обновите данные о студентах и группах.")
    return wrapper

def is_admin(func):
    @wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        """Checks if the user is an admin before executing the handler."""
        if message.from_user.id == ID_ADMIN:
            return await func(message, *args, **kwargs)
        await message.reply("У вас нет прав администратора.")
        return None
    return wrapper