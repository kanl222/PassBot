import contextlib
import logging
from typing import AsyncIterator, Optional

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SqlAlchemyBase = declarative_base()


class DatabaseSessionManager:
    def __init__(self):
        self._session_factory: Optional[sessionmaker] = None
        self._engine: Optional[AsyncEngine] = None

    def initialize(self, database_url: str) -> None:
        """
        Initialize the database connection and session factory.

        :param database_url: URL of the database connection (e.g., 'postgresql+asyncpg://user:password@localhost/dbname').
        :raises ValueError: If connection parameters are not provided.
        """
        if self._session_factory:
            logger.info("Database is already initialized.")
            return

        if not database_url or not database_url.strip():
            raise ValueError("Database connection parameters must be provided.")

        logger.info(f"Connecting to PostgreSQL database at {database_url}...")

        # Create the async engine and session factory
        self._engine = create_async_engine(database_url, echo=False)
        self._session_factory = async_sessionmaker(
            bind=self._engine, class_=AsyncSession, expire_on_commit=False
        )

        logger.info("PostgreSQL database initialization complete.")

    async def init_models(self) -> None:
        """
        Initialize models asynchronously by creating or dropping tables using AsyncEngine.
        """
        if self._engine is None:
            raise ValueError("Engine is not initialized. Call initialize() first.")

        logger.info("Initializing database models...")

        async with self._engine.begin() as conn:
            await conn.run_sync(SqlAlchemyBase.metadata.drop_all)
            await conn.run_sync(SqlAlchemyBase.metadata.create_all)

        logger.info("Database models initialized successfully.")

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._session_factory is None:
            raise IOError("DatabaseSessionManager is not initialized")
        async with self._session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

    def get_base(self):
        """
        Return the declarative base for model definitions.
        """
        return SqlAlchemyBase

    async def shutdown(self) -> None:
        """
        Cleanly shut down the database engine when the application is closing.
        """
        if self._engine:
            await self._engine.dispose()
            logger.info("Database connection closed.")


db_session_manager = DatabaseSessionManager()


async def get_session() -> AsyncSession:
    async with db_session_manager.session() as session:
        yield session
