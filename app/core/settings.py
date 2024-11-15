import logging

from pydantic_settings import BaseSettings

IS_POSTGRESQL: bool = True
TEST_MODE: bool = True

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = 'HS256'
    TELEGRAM_BOT_TOKEN: str

    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int = 5432
    DB_NAME: str

    class Config:
        env_file = ".env"


try:
    settings = Settings()
    logging.info("Configuration loaded successfully")
except Exception as e:
    logging.error(f"Error loading configuration: {e}", exc_info=True)



def get_db_url() -> str:
    """
    Generate a URL to connect to the database depending on the settings
    """
    if settings.IS_POSTGRESQL:
        return f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    else:
        return "sqlite:///./app/db.sqlite3"


if __name__ == "__main__":
    logging.info(f"Secret Key: {settings.SECRET_KEY[:5]}... (hidden for security)")
    logging.info(f"Algorithm: {settings.ALGORITHM}")
    logging.info(f"Telegram Bot Token: {settings.TELEGRAM_BOT_TOKEN[:5]}... (hidden for security)")
    db_url = get_db_url()
    logging.info(f"Database URL: {db_url}")
