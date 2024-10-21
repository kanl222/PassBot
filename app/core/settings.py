import logging
import os

from pydantic_settings import BaseSettings, SettingsConfigDict

IS_TEST_MODE: str = True
IS_POSTGRESQL: bool = False


class SettingsDatabase(BaseSettings):
	DB_USER: str = None
	DB_PASSWORD: str = None
	DB_HOST: str = None
	DB_PORT: int = 5432
	DB_NAME: str = None

	IS_POSTGRESQL: bool = False

	model_config = SettingsConfigDict(
		env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".config_db")
	)

	def get_db_url(self) -> str:
		if not self.IS_POSTGRESQL:
			return "sqlite+aiosqlite:///app/db/DataBase.db?check_same_thread=False"
		else:
			return (
				f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@"
				f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
			)


class User(BaseSettings):
	LOGIN: str = None
	PASSWORD: str = None


try:
	settings_db = SettingsDatabase()
except Exception as e:
	logging.error(e)


def get_db_url():
	return settings_db.get_db_url()
