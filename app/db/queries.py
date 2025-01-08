import logging
from typing import Optional, List, Tuple, Type, TypeVar, Union

from sqlalchemy import Result, Select, Sequence, select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from async_lru import alru_cache

from app.db.db_session import get_session


ModelType = TypeVar("ModelType")


class UniversalQueryService:
    @classmethod
    @alru_cache(maxsize=1000)
    async def get_entities(
        cls, model: Type[ModelType], id: Optional[int] = None, **filters
    )  -> Sequence[ModelType] | None | list:
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

                query = query.options(selectinload("*"))

                result = await db_session.execute(query)
                return result.scalars().all() 
        except Exception as e:
            logging.error(f"{model.__name__} retrieval error: {e}")
            return None if id is not None else []
