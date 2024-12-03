import logging
import os
from pathlib import Path
from dotenv import load_dotenv

ENV_FILE_PATH: Path = Path(os.path.dirname(os.path.abspath(__file__))) / ".." / ".env"
IS_POSTGRESQL: bool = True
TEST_MODE: bool = True

if ENV_FILE_PATH.exists():
    logging.info(f"Loaded environment variables from {ENV_FILE_PATH}")
    load_dotenv(dotenv_path=ENV_FILE_PATH)
else:
    logging.error(f".env file not found at {ENV_FILE_PATH}")
    raise FileNotFoundError(f".env file not found at {ENV_FILE_PATH}")


class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    TELEGRAM_BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")

    DB_USER: str = os.getenv("DB_USER", "")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_HOST: str = os.getenv("DB_HOST", "")
    DB_PORT: int = int(os.getenv("DB_PORT", 5432))
    DB_NAME: str = os.getenv("DB_NAME", "")

    IS_TELEGRAM_BOT_TOKEN:bool = bool(TELEGRAM_BOT_TOKEN)

    def validate(self):
        """Validate the required settings."""
        if not self.SECRET_KEY:
            from .security import SettingsCrypto
            SettingsCrypto()
        if not self.IS_TELEGRAM_BOT_TOKEN:
            raise ValueError("BOT_TOKEN is required but not set.")
        if IS_POSTGRESQL and not all([self.DB_USER, self.DB_PASSWORD, self.DB_HOST, self.DB_NAME]):
            raise ValueError("Database configuration is incomplete.")

try:
    settings = Settings()
    settings.validate()
    logging.info("Configuration loaded successfully.")
except Exception as e:
    logging.error(f"Error loading configuration: {e}", exc_info=True)
    raise

def get_db_url() -> str:
    """
    Generate a URL to connect to the database depending on the settings.
    """
    if IS_POSTGRESQL:
        return f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    else:
        return "sqlite:///./app/db.sqlite3"

if __name__ == "__main__":
    logging.info(f"Secret Key: {settings.SECRET_KEY[:5]}... (hidden for security)")
    logging.info(f"Algorithm: {settings.ALGORITHM}")
    logging.info(f"Telegram Bot Token: {settings.TELEGRAM_BOT_TOKEN[:5]}... (hidden for security)")
    db_url = get_db_url()
    logging.info(f"Database URL: {db_url}")
