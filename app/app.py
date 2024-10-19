import asyncio
import logging

from .core.logging import setup_logging
from .core.security import encode_data
from .db import db_session_manager, get_db_url

setup_logging()


def db_init_models():
    """
    Initialization of database models.

    :return: None
    """
    db_path = get_db_url()
    if not db_path:
        raise ValueError("Путь к базе данных должен быть указан в конфигурационном файле.")

    db_session_manager.initialize(db_path)
    asyncio.get_event_loop().run_until_complete(db_session_manager.init_models())


def init_user(user_login, user_password):
    """
    Initializing the user for parsing.

    :return: None
    """
    user_data = {
        'login': user_login,
        'password': user_password
    }

    user_crypt_data = encode_data(user_data)


def run_bot():
    """
    Launch of the bot.

    :return: None
    """
    pass
