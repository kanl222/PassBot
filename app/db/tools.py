import logging
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from app.db.db_session import with_session
from .__all_models import *
@with_session
async def clear_database(db_session: AsyncSession, preserve_user_id: int = 1):
    """Clears all database tables except for the specified user."""

    try:
        

        await db_session.execute(delete(Visiting))
        await db_session.execute(
            delete(group_pair_association)
        )  
        await db_session.execute(delete(Pair))
        await db_session.execute(delete(Student).where(Student.id != preserve_user_id))
        await db_session.execute(delete(Teacher).where(Teacher.id != preserve_user_id))
        await db_session.execute(delete(Group))  
        await db_session.execute(delete(User).where(User.id != preserve_user_id))

        await db_session.commit()
        logging.info("Database cleared successfully (except for preserved user).")

    except Exception as e:
        logging.error(f"Error clearing database: {e}")
        await db_session.rollback()

@with_session
async def test_visiting(db_session: AsyncSession, preserve_user_id: int = 1):
    """Clears all database tables except for the specified user."""

    try:
        

        await db_session.execute(delete(Visiting))
        await db_session.execute(
            delete(group_pair_association)
        )  
        await db_session.execute(delete(Pair))

        await db_session.commit()
        logging.info("Database cleared successfully (except for preserved user).")

    except Exception as e:
        logging.error(f"Error clearing database: {e}")
        await db_session.rollback()