import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
import pytz

TEST_MODE = True
ID_ADMIN= 1018178535
ENV_FILE_PATH: Path = Path(os.path.dirname(os.path.abspath(__file__))) / ".." / ".env"
IS_POSTGRESQL = False
tz = pytz.timezone('Asia/Yekaterinburg')
DIR_DATA = 'data'
ENV_PATH = ".env"

@dataclass
class DatabaseConfig:
    user: str = ""
    password: str = ""
    host: str = ""
    port: int = 5432
    name: str = ""

@dataclass
class Settings:
    secret_key: str = ""
    algorithm: str = "HS256"
    telegram_bot_token: str = ""
    is_postgresql: bool = False
    database: DatabaseConfig = field(default_factory=DatabaseConfig)

    @classmethod
    def load(cls, env_file_path: Optional[Path] = None) -> 'Settings':
        """
        Load configuration from environment variables with optional .env file.
        
        Args:
            env_file_path: Optional path to .env file. Defaults to project root.
        
        Returns:
            Configured Settings instance.
        
        Raises:
            FileNotFoundError: If specified .env file does not exist.
            ValueError: If required configuration is missing.
        """
        if env_file_path is None:
            env_file_path = Path(__file__).parent.parent / ".env"

        if env_file_path.exists():
            logging.info(f"Loading environment variables from {env_file_path}")
            load_dotenv(dotenv_path=env_file_path)
        else:
            logging.warning(f"No .env file found at {env_file_path}")

        settings: Self = cls(
            secret_key=os.getenv("SECRET_KEY", ""),
            algorithm=os.getenv("ALGORITHM", "HS256"),
            telegram_bot_token=os.getenv("BOT_TOKEN", ""),
            is_postgresql=os.getenv("IS_POSTGRESQL", "false").lower() == "true",
            database=DatabaseConfig(
                user=os.getenv("DB_USER", ""),
                password=os.getenv("DB_PASSWORD", ""),
                host=os.getenv("DB_HOST", ""),
                port=int(os.getenv("DB_PORT", "5432")),
                name=os.getenv("DB_NAME", "")
            )
        )

        # Validate configuration
        settings.validate()
        return settings

    def validate(self) -> None:
        """Validate required configuration settings."""
        if not self.secret_key:
            from .security import DataCrypto
            DataCrypto()

        if not self.telegram_bot_token:
            raise ValueError("Telegram Bot Token is required.")

        if self.is_postgresql and not all([
            self.database.user, 
            self.database.password, 
            self.database.host, 
            self.database.name
        ]):
            raise ValueError("PostgreSQL configuration is incomplete.")

    def get_database_url(self) -> str:
        if self.is_postgresql:
            return (
                f"postgresql+asyncpg://"
                f"{self.database.user}:{self.database.password}@"
                f"{self.database.host}:{self.database.port}/"
                f"{self.database.name}"
            )
        
        db_path: Path = Path("./DataBase.db").resolve()
        return f"sqlite+aiosqlite:///{db_path}"


try:
    settings: Settings = Settings.load(ENV_FILE_PATH)
    logging.info("Configuration loaded successfully.")
except Exception as e:
    logging.error(f"Configuration error: {e}", exc_info=True)
    raise

if __name__ == "__main__":
    logging.info(f"Secret Key: {settings.secret_key[:5]}... (hidden)")
    logging.info(f"Algorithm: {settings.algorithm}")
    logging.info(f"Telegram Bot Token: {settings.telegram_bot_token[:5]}... (hidden)")
    logging.info(f"Database URL: {settings.get_database_url()}")
