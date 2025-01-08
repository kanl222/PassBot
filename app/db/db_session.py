from ast import For
import contextlib
import logging
import traceback
from typing import Any, AsyncIterator, Optional, Callable
from functools import wraps

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.settings import IS_POSTGRESQL
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO)
logger: logging.Logger = logging.getLogger(__name__)

SqlAlchemyBase = declarative_base()

from . import __all_models


class DatabaseSessionManager:
    def __init__(self) -> None:
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker | None = None

    def initialize(
        self, database_url: str, pool_size: int = 20, max_overflow: int = 80
    ) -> None:
        """
        Initialize the database connection and session factory.

        :param database_url: URL of the database connection (e.g., 'postgresql+asyncpg://user:password@localhost/dbname').
        :param pool_size: Size of the connection pool (default: 10).
        :param max_overflow: Number of overflow connections (default: 20).
        :raises ValueError: If connection parameters are not provided.
        """
        if self._session_factory:
            logger.warning("Database is already initialized.")
            return

        if not database_url:
            raise ValueError("Database connection parameters must be provided.")

        logger.info(
            f"Connecting to {
                    'PostgreSQL' if IS_POSTGRESQL else 'SQLite'} database"
        )

        try:
            self._engine = create_async_engine(
                database_url,
                echo=False,
            )
            self._session_factory = async_sessionmaker(
                bind=self._engine, class_=AsyncSession, expire_on_commit=False
            )
            if IS_POSTGRESQL:
                logger.info("PostgreSQL database initialization complete.")
            else:
                logger.info("SQLite database initialization complete.")

        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            raise

    async def init_models(self, drop_existing: bool = False) -> None:
        """
        Initialize models asynchronously by creating or dropping tables using AsyncEngine.

        :param drop_existing: If True, drop all existing tables before creating new ones.
        """
        if self._engine is None:
            raise ValueError("Engine is not initialized. Call initialize() first.")

        logger.info("Initializing database models...")
        try:
            async with self._engine.begin() as conn:
                if drop_existing:
                    logger.info("Dropping all existing tables...")
                    await conn.run_sync(SqlAlchemyBase.metadata.drop_all)
                logger.info("Creating all tables...")
                await conn.run_sync(SqlAlchemyBase.metadata.create_all)

            logger.info("Database models initialized successfully.")
        except Exception as e:
            logger.error(f"Error initializing models: {e}")
            raise

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        """Provide a transactional session context."""
        if not self._session_factory:
            raise RuntimeError("Database not configured")

        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"Session error: {e}")
                traceback.print_exc()
                raise
            finally:
                await session.close()

    def get_base(self) -> SqlAlchemyBase:  # type: ignore
        """
        Return the declarative base for model definitions.
        """
        return SqlAlchemyBase

    async def shutdown(self) -> None:
        """
        Cleanly shut down the database engine when the application is closing.
        """
        if self._engine:
            try:
                await self._engine.dispose()
                logger.info("Database connection closed.")
            except Exception as e:
                logger.error(f"Shutdown error: {e}")


db_session_manager = DatabaseSessionManager()


@asynccontextmanager
async def get_session() -> AsyncIterator[AsyncSession]:
    """Simplified session context manager."""
    async with db_session_manager.session() as session:
        yield session


def with_session(func: Callable):
    """Decorator to inject database session into function."""

    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        if "db_session" in kwargs and isinstance(kwargs["db_session"], AsyncSession):
            return await func(*args, **kwargs)
        
        async with get_session() as session:
            kwargs["db_session"] = session
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logging.error(f"Error in {func.__name__}: {e}")
                raise

    return wrapper


