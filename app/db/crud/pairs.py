import datetime
import logging
from typing import Any, List, Optional
from async_lru import alru_cache
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.db_session import with_session
from app.db.models.pairs import Pair


@with_session
@alru_cache(100)
async def get_pair(db_session: AsyncSession, id_pair: int) -> Optional[Pair]:
    """
    Retrieves a Pair by ID.
    """
    try:
        result = await db_session.execute(select(Pair).where(Pair.id == id_pair))
        return result.scalar_one_or_none()
    except Exception as e:
        logging.error(f"Error retrieving Pair with id={id_pair}: {e}")
        return None


@with_session
async def get_pair_by_kwargs(
    db_session: AsyncSession,
    date: Optional[datetime.date] = None,
    pair_number: Optional[int] = None,
    discipline: Optional[str] = None,
) -> Optional[Pair]:
    """
    Retrieves a Pair by specified kwargs.
    """
    try:
        filters = []
        if date:
            filters.append(Pair.date == date)
        if pair_number:
            filters.append(Pair.pair_number == pair_number)
        if discipline:
            filters.append(Pair.discipline == discipline)

        query = select(Pair).where(*filters)
        result = await db_session.execute(query)
        return result.scalar_one_or_none()
    except Exception as e:
        logging.error(
            f"Error retrieving Pair with date={date}, pair_number={pair_number}, discipline={discipline}: {e}"
        )
        return None


@with_session
async def create_pair(
    db_session: AsyncSession, date: datetime.date, pair_number: int, discipline: str
) -> Optional[Pair]:
    """
    Creates a new Pair.
    """
    try:
        pair = Pair(date=date, pair_number=pair_number, discipline=discipline)
        db_session.add(pair)
        await db_session.commit()
        logging.info(
            f"Created Pair: date={date}, pair_number={pair_number}, discipline={discipline}"
        )
        return pair
    except Exception as e:
        logging.error(
            f"Error creating Pair with date={date}, pair_number={pair_number}, discipline={discipline}: {e}"
        )
        await db_session.rollback()
        return None


@with_session
async def get_or_create_pair(
    db_session: AsyncSession ,
    id_pair: Optional[int] = None,
    date: Optional[datetime.date] = None,
    pair_number: Optional[int] = None,
    discipline: Optional[str] = None,
) -> Optional[Pair]:
    """
    Retrieves or creates a Pair object.
    """
    try:
        if id_pair:
            pair = await get_pair( db_session=db_session,id_pair= id_pair)
            if pair:
                return pair
            logging.info(f"Pair with id={id_pair} not found, proceeding to creation.")

        if date and pair_number and discipline:
            pair = await get_pair_by_kwargs(
                db_session=db_session,
                date=date,
                pair_number=pair_number,
                discipline=discipline,
            )
            if pair:
                return pair

            return await create_pair( db_session=db_session, date=date, pair_number= pair_number, discipline=discipline)

        logging.warning(
            f"Invalid parameters for get_or_create_pair: id_pair={id_pair}, date={date}, pair_number={pair_number}, discipline={discipline}"
        )
        return None
    except Exception as e:
        logging.error(
            f"Error in get_or_create_pair: id_pair={id_pair}, date={date}, pair_number={pair_number}, discipline={discipline}: {e}"
        )
        return None
