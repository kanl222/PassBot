from datetime import datetime, timezone, timedelta
from multiprocessing.managers import Token
from typing import Optional
from secrets import choice
from string import digits, ascii_letters
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from .sittings import settings
from ..db.db_session import get_session

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM


def encode_data(data: dict) -> str:
    new_data: dict = data.copy()
    return jwt.encode(new_data, key=SECRET_KEY, algorithm=ALGORITHM)    


def decode_data(token: str) -> dict:
    return jwt.decode(token, key=SECRET_KEY, algorithms=ALGORITHM)


def generate_new_secret_key() -> None:
    secret_key = ascii_letters + digits + '-+)(*?><{}!@#$%^'
    return ''.join([choice(secret_key) for i in range(64)])


def import_crypt_user() -> dict:
    pass


def change_secret_key() -> None:
    settings.model_config.update('SECRET_KEY', generate_new_secret_key)
