from .core.logging import setup_logging
from .db import get_db_url, db_session_manager
from .core.sittings import settings
from .core.security import decode_data,encode_data
import logging
import asyncio

setup_logging()


def db_init_models():
    """
    Команда для инициализации моделей базы данных.

    :return: None
    """

    db_path = get_db_url()
    if not db_path:
        raise ValueError("Путь к базе данных должен быть указан в конфигурационном файле.")

    db_session_manager.initialize(db_path)
    logging.info("Инициализации моделей...")
    asyncio.get_event_loop().run_until_complete(db_session_manager.init_models())
    logging.info("Таблицы базы данных успешно созданы.")


def init_user():
    """
    Иницилизация пользователя для парсинга
    :return: None
    """
    logging.info('Иницилизация пользвоателя:')

    user_login = input().strip()
    user_password = input().strip()

    user_data = {
        'login': user_login,
        'password': user_password
    }

    user_crypt_data = encode_data(user_data)







async def run_():
    pass
