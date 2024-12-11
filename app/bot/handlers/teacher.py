from aiogram import types, Router
from aiogram.filters import Command

teacher_router:Router = Router()

@teacher_router.message(Command(commands=["groups"]))
async def list_groups(message: types.Message):
    # Здесь может быть логика получения списка групп из БД
    await message.reply("Ваши группы:\n1. Группа 101\n2. Группа 102")

@teacher_router.message(Command(commands=["absences"]))
async def list_absences(message: types.Message):
    # Здесь можно получить данные о пропусках студентов
    await message.reply("Пропуски студентов:\nИван Иванов: 2 пропуска\nПетр Петров: 1 пропуск")
