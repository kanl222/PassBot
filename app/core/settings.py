import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    IS_TEST_MODE: str = True
    IS_POSTGRESQL:bool = False

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    )

class User(BaseSettings):
    LOGIN: str = None
    PASSWORD: str = None

try:
    settings = Settings()
except Exception as e:
    print(e)

def set_data_user():
    pass


def get_db_url():
    if  not settings.IS_POSTGRESQL:
        return (
            f"sqlite+aiosqlite:///app/db/DataBase.db?check_same_thread=False"
        )
    else:
        return (
            f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@"
            f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
        )


def get_auth_data():
    return {"secret_key": settings.SECRET_KEY, "algorithm": settings.ALGORITHM}
