import logging
from typing import Dict, List
from aiogram import types, Router
from aiogram.filters import Command
from app.services.teacher import first_parser_data
import asyncio


class DataParsingService:
    async def send_progress(self, step: str) -> None:
        """Helper method to send progress updates."""
        await self.answer(f"Статус: {step}")
            
    @classmethod
    async def parse_teacher_data(cls, auth_payload: Dict[str, str]) -> None:
        """
        Orchestrate the parsing of teacher-related data with progress tracking.

        Args:
            auth_data: Authentication data for the teacher.
        """


        try:
            await first_parser_data(auth_payload=auth_payload)
        except Exception as e:
            logging.error(f"Data parsing error: {e}")
            raise

    @staticmethod
    async def _fetch_groups(auth_data: Dict[str, str]) -> List[Dict]:
        """Fetch groups for a teacher."""
        await asyncio.sleep(1)
        return [{"id": 1, "name": "Группа 101"}, {"id": 2, "name": "Группа 102"}]

    @staticmethod
    async def _fetch_students(groups: List[Dict]) -> List[Dict]:
        """Fetch students for given groups."""
        await asyncio.sleep(1)
        return [{"name": "Иван Иванов"}, {"name": "Петр Петров"}]

    @staticmethod
    async def _save_parsed_data(groups: List[Dict], students: List[Dict]) -> None:
        """Save parsed data to storage."""
        await asyncio.sleep(1)


teacher_router = Router()


@teacher_router.message(Command(commands=["groups"]))
async def list_groups(cls, message: types.Message) -> None:
    """List teacher's groups."""
    groups = [group['name'] for group in await DataParsingService._fetch_groups({})]
    await message.reply(f"Ваши группы:\n{chr(10).join(groups)}")


@teacher_router.message(Command(commands=["absences"]))
async def list_absences(cls, message: types.Message) -> None:
    """List student absences."""
    students = await DataParsingService._fetch_students([])
    absences = "\n".join(
        [f"{student['name']}: 1 пропуск" for student in students])
    await message.reply(f"Пропуски студентов:\n{absences}")


async def parse_data(cls, message: types.Message,auth_payload:dict) -> None:
    """Initiate data parsing process."""
    try:
        await message.answer("Начинаем парсинг данных...")
        await DataParsingService.parse_teacher_data(auth_payload)
        await message.answer("Парсинг данных успешно завершён.")
    except Exception as e:
        logging.error(f"Parsing error: {e}")
        await message.answer("Произошла ошибка при парсинге данных.")
