from functools import wraps
from functools import wraps
import logging
from typing import Any, Callable, Dict, List
from typing import Any, Callable, Dict, List
from aiogram import types, Router
from aiogram.filters import Command
from app.db.db_session import with_session
from app.db.models.users import Teacher, UserRole
from app.services.teacher import first_parser_data
from app.services.users import get_teacher
from app.services.users import get_teacher
import asyncio

from app.services.visiting import pars_visiting


def is_teacher(func: Callable):
    """Decorator to inject database session into function."""
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        telegram_id = args[0].from_user.id
        if user:= await get_teacher(telegram_id=telegram_id):
            return await func(*args, **kwargs)
    return wrapper


class DataParsingService:
            
    @classmethod
    async def parse_teacher_data(cls,telegram_id:int) -> None:
        """
        Orchestrate the parsing of teacher-related data with progress tracking.

        Args:
            auth_data: Authentication data for the teacher.
        """

        try:
            await first_parser_data(telegram_id)
        except Exception as e:
            logging.error(f"Data parsing error: {e}")
            raise

    @staticmethod
    async def _fetch_groups(id_telegram:int) -> List[Dict]:
        """Fetch groups for a teacher."""
        teacher: Teacher | List[Teacher] | None = await get_teacher(telegram_id=id_telegram)
        if teacher:
            return [{"id": group.id, "name": group.name} for group in teacher.curated_groups]
        return []

    @staticmethod
    async def _fetch_students(id_telegram:int) -> List[Dict]:
        """Fetch students for given groups."""
        teacher: Teacher | List[Teacher] | None = await get_teacher(telegram_id=id_telegram)
        if teacher:
            students = []
            for group in teacher.curated_groups:
                students.extend({"name": student.full_name} for student in group.students)
            return students
        return []




teacher_router = Router()


@teacher_router.message(Command(commands=["groups"]))
@is_teacher
async def list_groups(message: types.Message) -> None:
    """List teacher's groups."""
    id_telegram: int = message.from_user.id
    groups = await DataParsingService._fetch_groups(id_telegram)
    if groups:
        await message.answer(f"Ваши группы:\n{chr(10).join(group['name'] for group in groups)}")
    else:
        await message.answer("У вас нет групп.")


@teacher_router.message(Command(commands=["absences"]))
@is_teacher
async def list_absences(message: types.Message) -> None:
    """List student absences."""
    id_telegram: int = message.from_user.id
    students = await DataParsingService._fetch_students([])
    absences = "\n".join([f"{student['name']}: 1 пропуск" for student in students])
    absences = "\n".join([f"{student['name']}: 1 пропуск" for student in students])
    await message.reply(f"Пропуски студентов:\n{absences}")

@teacher_router.message(Command(commands=["test"]))

async def parse_data(message: types.Message) -> None:
    """Initiate data parsing process."""
    try:
        id_telegram: int = message.from_user.id
        await message.answer("Начинаем парсинг данных...")
        await DataParsingService.parse_teacher_data(telegram_id=id_telegram)
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
        res = await pars_visiting()
        print(res)
        await message.answer("Парсинг данных успешно завершён.")
    except Exception as e:
        logging.error(f"Parsing error: {e}")
        await message.answer("Произошла ошибка при парсинге данных.")