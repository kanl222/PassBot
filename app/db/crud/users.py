import logging
from typing import Optional, List, Type, TypeVar, Union

from async_lru import alru_cache
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.db_session import get_session
from app.db.models.users import Student, Teacher, User
from app.db.queries import UniversalQueryService


@alru_cache(100)
async def get_user_of_telegram_id(telegram_id: Optional[int]) -> Optional[User]:
        """Retrieve user by Telegram ID."""
        async with get_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            return result.scalars().first()

@alru_cache(100)
async def get_teacher(telegram_id: Optional[int] ,relationship:bool=False) -> Optional[Teacher]:
        """Retrieve teacher by Telegram ID."""
        async with get_session() as session:
            query = select(Teacher)
            if telegram_id:
                query = query.where(Teacher.telegram_id == telegram_id)
            
            if relationship:
                query = query.options(selectinload(Teacher.curated_groups))
            result = await session.execute(query)
            return result.scalars().first()

@alru_cache(100)
async def get_student(
        id: Optional[int] = None,
        full_name: Optional[str] = None,
        telegram_id: Optional[str] = None,
        id_group: Optional[int] = None,
    ) -> Optional[Student]:
        """Retrieve student by various filters."""
        async with get_session() as session:
            query = select(Student)
            if id:
                query = query.where(Student.id == id)
            if telegram_id:
                query = query.where(Student.telegram_id == telegram_id)
            if full_name:
                query = query.where(Student.full_name == full_name)
            if id_group:
                query = query.where(Student.group_id == id_group)
            result = await session.execute(query)
            return result.scalars().first()
@alru_cache(100)
async def get_all_teachers() -> List[Teacher]:
        """Retrieve all teachers."""
        return await UniversalQueryService.get_entities(Teacher)

