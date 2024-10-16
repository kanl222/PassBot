import asyncio
import logging

from .core.logging import setup_logging
from .core.security import encode_data
from .db import db_session_manager, get_db_url

setup_logging()


def db_init_models():
	"""
    Команда для инициализации моделей базы данных.

    :return: None
    """
	try:
		db_path = get_db_url()
		if not db_path:
			raise ValueError("Путь к базе данных должен быть указан в конфигурационном файле.")

		db_session_manager.initialize(db_path)
		logging.info("Инициализация моделей базы данных...")
		asyncio.get_event_loop().run_until_complete(db_session_manager.init_models())
		logging.info("Таблицы базы данных успешно созданы.")
	except Exception as e:
		logging.error(f"Ошибка инициализации моделей: {e}")
		raise


def init_user(user_login,user_password):
	"""
    Инициализация пользователя для парсинга.

    :return: None
    """
	user_data = {
			'login': user_login,
			'password': user_password
		}

	user_crypt_data = encode_data(user_data)
	logging.info(f"Пользователь {user_login} успешно инициализирован.")



def run_bot():
	"""
    Асинхронный запуск бота.

    :return: None
    """
	try:
		logging.info("Запуск бота...")
		logging.info("Бот успешно запущен.")
	except Exception as e:
		logging.error(f"Ошибка при запуске бота: {e}")
		raise
