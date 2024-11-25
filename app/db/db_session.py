import contextlib
import logging
from typing import AsyncIterator, Optional

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.settings import IS_POSTGRESQL

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SqlAlchemyBase = declarative_base()


class DatabaseSessionManager:
	def __init__(self):
		self._session_factory: Optional[sessionmaker] = None
		self._engine: Optional[AsyncEngine] = None

	def initialize(self, database_url: str, pool_size: int = 20, max_overflow: int = 80) -> None:
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

		if not database_url or not database_url.strip():
			raise ValueError("Database connection parameters must be provided.")

		if IS_POSTGRESQL:
			logger.info(f"Connecting to PostgreSQL database at {database_url}...")
		else:
			logger.info(f"Connecting to SqlLite database at {database_url}...")

		try:
			self._engine = create_async_engine(
				database_url,
				echo=False,
				pool_size=pool_size,
				max_overflow=max_overflow
			)
			self._session_factory = async_sessionmaker(
				bind=self._engine, class_=AsyncSession, expire_on_commit=False
			)
			if IS_POSTGRESQL:
				logger.info("PostgreSQL database initialization complete.")
			else:
				logger.info("SqlLite database initialization complete.")

		except Exception as e:
			logger.error(f"Error initializing database: {e}")
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

	@contextlib.asynccontextmanager
	async def session(self) -> AsyncIterator[AsyncSession]:
		"""
        Provides an asynchronous context manager for database sessions.

        Rolls back the transaction in case of an exception and closes the session afterwards.
        """
		if self._session_factory is None:
			raise IOError("DatabaseSessionManager is not initialized")

		async with self._session_factory() as session:
			try:
				yield session
			except Exception as e:
				logger.error(f"Session error, rolling back: {e}")
				await session.rollback()
				raise
			finally:
				await session.close()

	def get_base(self) -> SqlAlchemyBase:
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
				logger.error(f"Error during database shutdown: {e}")
				raise


db_session_manager = DatabaseSessionManager()


async def get_session() -> AsyncIterator[AsyncSession]:
	"""
    A generator that provides an asynchronous session to be used in database operations.
    Ensures proper resource management using the session context manager.
    """
	async with db_session_manager.session() as session:
		yield session
