from aiogram import types, Router
from aiogram.filters import Command

student_router: Router = Router()

@student_router.message(Command(commands=["progress"]))
async def show_progress(message: types.Message) -> None:
    # Здесь можно получить данные из БД о прогрессе студента
    await message.reply("Ваш прогресс:\n1. Математика: 80%\n2. Физика: 70%")

@student_router.message(Command(commands=["profile"]))
async def show_profile(message: types.Message) -> None:
    # Пример профиля студента
    await message.reply("Ваш профиль:\nИмя: Иван Иванов\nГруппа: 101")
