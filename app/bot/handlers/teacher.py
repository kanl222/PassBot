import logging
from aiogram import types, Router
from aiogram.filters import Command
from app.parsers import teacher_parser
from app.services.teacher import TeacherDataService
from app.services.visiting import parse_visiting_of_pair
from .support import is_teacher


teacher_router = Router()

@teacher_router.message(Command(commands=["groups"]))
@is_teacher
async def list_groups(message: types.Message) -> None:
    """List teacher's groups."""
    id_telegram: int = message.from_user.id
    groups = await TeacherDataService._fetch_groups(id_telegram)
    if groups:
        await message.answer(f"Ваши группы:\n{chr(10).join(group['name'] for group in groups)}")
    else:
        await message.answer("У вас нет групп.")


@teacher_router.message(Command(commands=["absences"]))
@is_teacher
async def list_absences(message: types.Message) -> None:
    """List student absences."""
    id_telegram: int = message.from_user.id
    students = await TeacherDataService._fetch_students([])
    absences = "\n".join([f"{student['name']}: 1 пропуск" for student in students])
    absences = "\n".join([f"{student['name']}: 1 пропуск" for student in students])
    await message.reply(f"Пропуски студентов:\n{absences}")

@teacher_router.message(Command(commands=["test"]))
@is_teacher
async def parse_data(message: types.Message) -> None:
    """Initiate data parsing process."""
    try:
        id_telegram: int = message.from_user.id
        await message.answer("Начинаем парсинг данных...")
        await TeacherDataService.parse_and_update_teacher_data(telegram_id=id_telegram)
        await message.answer("Парсинг данных успешно завершён.")
    except Exception as e:
        logging.error(f"Parsing error: {e}")
        await message.answer("Произошла ошибка при парсинге данных.")

@teacher_router.message(Command(commands=["visiting"]))

async def parse_visiting(message: types.Message) -> None:
    """Initiate data parsing process."""
    try:
        id_telegram: int = message.from_user.id
        await message.answer("Начинаем парсинг данных...")
        res = await parse_visiting_of_pair()
        await message.answer("Парсинг данных успешно завершён.")
    except Exception as e:
        logging.error(f"Parsing error: {e}")
        await message.answer("Произошла ошибка при парсинге данных.")