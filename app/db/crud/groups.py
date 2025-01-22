import logging
from typing import List, Optional
from async_lru import alru_cache
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.db_session import with_session
from app.db.models.groups import Group
from sqlalchemy.orm import selectinload

@with_session
async def get_group(db_session: AsyncSession,id_group: int) -> Optional[Group]:
    """Retrieves a group by _id_group."""
    group_query = select(Group).filter_by(_id_group=id_group)
    return (await db_session.execute(group_query)).unique().scalar_one_or_none()


@with_session
async def create_group(
    db_session: AsyncSession, id_curator: int, _id_group: int, name: str
) -> Optional[Group]:
    """Creates a new group."""
    try:
        group = Group(id_curator=id_curator, _id_group=_id_group, name=name)
        db_session.add(group)
        await db_session.commit()
        await db_session.refresh(group)
        print(group)
        return group
    except Exception as e:
        logging.error(f"Error creating group: {e}")
        await db_session.rollback()
        return None

@with_session
async def get_or_create_group(db_session: AsyncSession,
    _id_group: int, id_curator: int, name: str
) -> Optional[Group]:
    """Retrieves a group by ID or creates it if it doesn't exist."""
    return await get_group(db_session=db_session,id_group= _id_group) or await create_group(
            db_session=db_session, id_curator=id_curator,_id_group= _id_group,name= name
        )

