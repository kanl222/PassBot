from aiogram import types, Router, F
from aiogram.filters import Command

from app.db.tools import clear_database, test_visiting

admin_router: Router = Router()

@admin_router.message(Command(commands=["admin"]))
async def admin_panel(message: types.Message) -> None:
    await message.reply("Добро пожаловать в панель администратора.")


@admin_router.message(Command(commands=["clearbd"]))
async def admin_panel(message: types.Message) -> None:
    await clear_database()
    await message.reply("Добро пожаловать в панель администратора.")

@admin_router.message(Command(commands=["clearvis"]))
async def admin_panel(message: types.Message) -> None:
    await test_visiting()
    await message.reply("Добро пожаловать в панель администратора.")