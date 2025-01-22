import datetime
import logging
from typing import Any, List, Optional
from async_lru import alru_cache
import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.db_session import with_session
from app.db.models.pairs import Pair


@with_session
async def get_pair(db_session: AsyncSession, id_pair: int) -> Optional[Pair]:
    """Retrieves a Pair by ID."""
    result = await db_session.execute(select(Pair).where(Pair.id == id_pair))
    return result.scalar_one_or_none()


@with_session
async def get_pair_by_key_pair(db_session: AsyncSession, key_pair: int) -> Optional[Pair]:
    """Retrieves a Pair by key_pair."""
    result = await db_session.execute(select(Pair).where(Pair.key_pair == key_pair))
    return result.scalar_one_or_none()


@with_session
async def create_pair(db_session: AsyncSession, key_pair: int, date: datetime.date, pair_number: int, discipline: str) -> Optional[Pair]:
    """Creates a new Pair."""
    pair = Pair(key_pair=key_pair, date=date,
                pair_number=pair_number, discipline=discipline)
    db_session.add(pair)
    await db_session.commit()
    await db_session.refresh(pair)
    return pair


@with_session
async def get_or_create_pair(
    db_session: AsyncSession,
    id_pair: Optional[int] = None,
    key_pair: Optional[int] = None,
    date: Optional[datetime.date] = None,
    pair_number: Optional[int] = None,
    discipline: Optional[str] = None,
) -> Optional[Pair]:
    """Retrieves or creates a Pair object."""

    if id_pair:
        pair = await get_pair(db_session=db_session, id_pair=id_pair)
        if pair:
            return pair

    if key_pair:
        pair = await get_pair_by_key_pair(db_session=db_session, key_pair=key_pair)
        if pair:
            return pair

    if date and pair_number and discipline and key_pair:
        return await create_pair(db_session=db_session, key_pair=key_pair, date=date, pair_number=pair_number, discipline=discipline)

    return None
