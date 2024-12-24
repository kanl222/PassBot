import logging
from typing import Optional, Union, List, Type, TypeVar
from unittest.mock import Base
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.db_session import get_session
from app.db.models.users import Student, Teacher, User
from app.services.tools import async_lru_cache

ModelType = TypeVar('ModelType', bound=Base)


class UniversalQueryService:
    @classmethod
    @async_lru_cache(1000)
    async def get_entities(
        cls,
        model: Type[ModelType],
        id: Optional[int] = None,
        **filters
    ) -> Union[ModelType, List[ModelType], None]:
        """
        Unified, efficient query method for retrieving database entities.

        Args:
            model: SQLAlchemy model class to query
            id: Optional specific entity ID
            **filters: Additional filtering conditions

        Returns:
            Single entity, list of entities, or None
        """
        try:
            async with get_session() as db_session:
                query = select(model)

                if id is not None:
                    query = query.filter(model.id == id)

                # Apply  filters
                for key, value in filters.items():
                    query = query.filter(getattr(model, key) == value)

                query = query.options(selectinload('*'))

                result = await db_session.execute(query)
                entities = result.scalars().all()

                return entities[0] if id is not None and entities else entities

        except Exception as e:
            logging.error(f"{model.__name__} retrieval error: {e}")
            return None if id is not None else []


class UserLookupService:
    @classmethod
    async def get_user_of_telegram_id(cls, telegram_id: int) -> Optional[User]:
        """Retrieve user by Telegram ID with optimized querying."""
        return await UniversalQueryService.get_entities(
            User,
            telegram_id=telegram_id
        )

    @classmethod
    async def get_teacher(cls, id: Optional[int] = None) -> Union[Teacher, List[Teacher], None]:
        """Retrieve teachers with flexible filtering."""
        return await UniversalQueryService.get_entities(Teacher, id=id)

    @classmethod
    async def get_student(
        cls,
        id: Optional[int] = None,
        full_name: Optional[str] = None,
        id_group: Optional[int] = None
    ) -> Union[Student, List[Student], None]:
        """Retrieve students with flexible filtering."""
        return await UniversalQueryService.get_entities(
            Student,
            id=id,
            full_name=full_name,
            group_id=id_group
        )


async def get_user_instance(telegram_id: int) -> Optional[User]:
    return await UserLookupService.get_user_of_telegram_id(telegram_id)


async def get_teacher(id: Optional[int] = None) -> Union[Teacher, List[Teacher], None]:
    return await UserLookupService.get_teacher(id)


async def get_student(
    id: Optional[int] = None,
    full_name: Optional[str] = None,
    id_group: Optional[int] = None
) -> Union[Student, List[Student], None]:
    return await UserLookupService.get_student(id, full_name, id_group)
