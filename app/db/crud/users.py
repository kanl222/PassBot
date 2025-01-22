import logging
from typing import Optional, List, Tuple, Type, TypeVar, Union

from async_lru import alru_cache
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select, delete, select
from sqlalchemy.orm import selectinload
from app.db.db_session import get_session, with_session
from app.db.models.users import Student, Teacher, User, UserRole
from app.db.queries import UniversalQueryService
from app.tools.support import timeit


@with_session
@timeit
async def get_user_of_telegram_id(db_session: AsyncSession, telegram_id: Optional[int]) -> Optional[User]:
    """Retrieve user by Telegram ID."""
    result = await db_session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    return result.scalars().first()


@with_session
async def get_teacher(db_session: AsyncSession, telegram_id: Optional[int], relationship: bool = False) -> Optional[Teacher]:
    """Retrieve teacher by Telegram ID."""
    query = select(Teacher).where(Teacher.telegram_id == telegram_id)
    result = await db_session.execute(query)
    return result.scalars().first()


@with_session
async def get_student(
        db_session: AsyncSession,
        id: Optional[int] = None,
        full_name: Optional[str] = None,
        telegram_id: Optional[str] = None,
        id_group: Optional[int] = None,

) -> Optional[Student]:
    """Retrieve student by various filters."""
    query = select(Student)
    if id:
        query = query.where(Student.id == id)
    if telegram_id:
        query = query.where(Student.telegram_id == telegram_id)
    if full_name:
        query = query.where(Student.full_name == full_name)
    if id_group:
        query: Select[Tuple[Student]] = query.where(
            Student.group_id == id_group)
    result = await db_session.execute(query)
    return result.scalars().first()


async def get_all_teachers() -> List[Teacher]:
    """Retrieve all teachers."""
    return await UniversalQueryService.get_entities(Teacher)


async def create_user(
    session: AsyncSession,
    full_name: str,
    telegram_id: Optional[int] = None,
    role: UserRole = UserRole.GUEST,
    **kwargs,
) -> User:
    """Creates a new user."""
    user_cls = Student if role == UserRole.STUDENT else Teacher
    user = user_cls(full_name=full_name,
                    telegram_id=telegram_id, role=role, **kwargs)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

@with_session
async def get_user(db_session: AsyncSession,user_id: int) -> Optional[User]:
    """Retrieves a user by ID."""
    async with get_session() as session:
        return await session.get(User, user_id)

@with_session
async def update_user(db_session: AsyncSession, user_id: int, **kwargs) -> Optional[User]:
    """Updates an existing user."""
    user = await get_user(db_session, user_id)
    if user:
        for key, value in kwargs.items():
            setattr(user, key, value)
        await db_sessionn.commit()
        return user
    return None

@with_session
async def delete_user(db_session: AsyncSession, user_id: int) -> bool:
    """Deletes a user."""
    result = await db_session.execute(delete(User).where(User.id == user_id))
    await db_session.commit()
    return result.rowcount > 0


async def get_all_users(db_session: AsyncSession, role: Optional[UserRole] = None) -> List[User]:
    """Retrieves all users, optionally filtered by role."""
    query = select(User)
    if role:
        query = query.where(User.role == role)
    result = await db_session.execute(query)
    return result.scalars().all()
