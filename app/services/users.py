from typing import Any, Dict, Optional, Tuple
from sqlalchemy import Result
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.db_session import with_session,get_session
from app.db.models.users import User
from functools import cached_property
import logging
from .tools import LookupCache

class UserLookupService:
    @cached_property
    def cache(self) -> LookupCache:
        """Lazily initialized user lookup cache."""
        return LookupCache()

    async def get_user(self, telegram_id: int) -> Optional[User]:
        """
        Retrieve the `User` instance for the given Telegram ID.

        Args:
            telegram_id: Telegram ID of the user to check.
            db_session: SQLAlchemy Async Session for database interaction.

        Returns:
            User instance if found, otherwise None.
        """
        cached_result: Dict[str, Any] | None = self.cache.get(telegram_id)
        if cached_result and "user_instance" in cached_result:
            logging.info(f"Cache hit for Telegram ID {telegram_id}")
            return cached_result["user_instance"]

        try:
            async with get_session() as db_session:
                result: Result[Tuple[User]] = await db_session.execute(
                    select(User).filter(User.telegram_id == telegram_id)
                )
                user: User | None = result.scalar()
                if user:
                    self.cache.set(telegram_id, {"user_instance": user})
                return user
        except Exception as e:
            logging.error(f"Error retrieving user from DB: {e}")
            return None

    def create_user_response(self, user: Optional[User]) -> Dict[str, Any]:
        """
        Create a standardized response for a user lookup.

        Args:
            user: The `User` instance or None if not found.

        Returns:
            A dictionary response.
        """
        if user:
            return {
                "status": "exists",
                "user": user.full_name,
                "role": user.role.value,
                "error_message": None
            }
        return {
            "status": "not_found",
            "user": None,
            "role": None,
            "error_message": None
        }

    async def check_user_in_db(self, telegram_id: int) -> Dict[str, Any]:
        """
        Check user existence and return a response dictionary.

        Args:
            telegram_id: Telegram ID of the user to check.
            db_session: SQLAlchemy Async Session for database interaction.

        Returns:
            A dictionary with user existence information.
        """
        user: User | None = await self.get_user(telegram_id)
        return self.create_user_response(user)

user_lookup_service = UserLookupService()

async def get_user_instance(telegram_id: int) -> Optional[User]:
    """Retrieve the `User` instance for a given Telegram ID."""
    return await user_lookup_service.get_user(telegram_id)

async def get_user_response(telegram_id: int) -> Dict[str, Any]:
    """Retrieve the response dictionary for a given Telegram ID."""
    return await user_lookup_service.check_user_in_db(telegram_id)
