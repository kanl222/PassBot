from aiogram import types, Router
from aiogram.filters import Command
from app.bot.handlers.support import is_admin
from app.db.tools import clear_database, test_visiting
from app.services.visiting import parse_visiting_of_pair
import logging

logger = logging.getLogger(__name__)



admin_router: Router = Router()

@admin_router.message(Command(commands=["admin"]))
@is_admin
async def admin_panel(message: types.Message) -> None:
    """Admin panel entry point."""
    await message.reply("Добро пожаловать в панель администратора.")

@admin_router.message(Command(commands=["clearbd"]))
@is_admin
async def clear_db_command(message: types.Message) -> None:
    """Clear the database."""
    try:
        await clear_database()
        await message.reply("База данных успешно очищена.")
    except Exception as e:
        logger.error(f"Error clearing the database: {e}")
        await message.reply("Произошла ошибка при очистке базы данных.")

@admin_router.message(Command(commands=["clearvis"]))
@is_admin
async def clear_visiting_command(message: types.Message) -> None:
    """Test visiting data."""
    try:
        await test_visiting()
        await message.reply("Данные посещений успешно очищены.")
    except Exception as e:
        logger.error(f"Error testing visiting data: {e}")
        await message.reply("Произошла ошибка при очистке данных посещений.")

@admin_router.message(Command(commands=["all-visiting"]))
@is_admin
async def parse_visiting_command(message: types.Message) -> None:
    """Initiate visiting data parsing process."""
    try:
        await message.answer("Начинаем парсинг данных о посещениях...")
        await parse_visiting_of_pair()
        await message.answer("Парсинг данных о посещениях успешно завершён.")
    except Exception as e:
        logger.error(f"Parsing error: {e}")
        await message.answer("Произошла ошибка при парсинге данных о посещениях.")
