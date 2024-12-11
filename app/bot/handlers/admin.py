from aiogram import types, Router, F
from aiogram.filters import Command

admin_router: Router = Router()

@admin_router.message(Command(commands=["admin"]))
async def admin_panel(message: types.Message):
    await message.reply("Добро пожаловать в панель администратора.")

