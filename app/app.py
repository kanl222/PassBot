import asyncio
import logging

from .core.logging import setup_logging
from .db import db_session_manager, get_db_url
from .tools.create_config import create_crypto_config, create_db_config

setup_logging()


def db_init_models():
	"""
	Initialization of database models.

	:raises ValueError: If the database path is not specified in the configuration file.
	:return: None
	"""
	db_path = get_db_url()

	if not db_path:
		logging.error("Database path must be specified in the configuration file.")
		raise ValueError("Путь к базе данных должен быть указан в конфигурационном файле.")

	logging.info(f"Initializing database with path: {db_path}")
	db_session_manager.initialize(db_path)

	asyncio.run(_async_init_models())


async def _async_init_models():
	"""
	Asynchronous initialization of database models.

	:return: None
	"""
	try:
		await db_session_manager.init_models()
		logging.info("Database models initialized successfully.")
	except Exception as e:
		logging.error(f"Error initializing database models: {e}", exc_info=True)
		raise


def init_user(user_login, user_password):
	"""
	Initializing the user for parsing.

	:return: None
	"""
	from .core.security import encode_data
	user_data = {
		'login': user_login,
		'password': user_password
	}

	try:
		user_crypt_data = encode_data(user_data)
		logging.info(f"User data encoded successfully for user: {user_login}")
	except Exception as e:
		logging.error(f"Error encoding user data: {e}", exc_info=True)
		raise


def create_config_files() -> None:
	"""
	Create configuration files for crypto and database settings.

	:return: None
	"""
	from .core.security import settings_crypto
	try:
		create_crypto_config(secret_key=settings_crypto.SECRET_KEY)
		logging.info("Crypto configuration file created successfully.")

		create_db_config(db_user="dbuser", db_password="dbpassword", db_host="localhost", db_name="mydatabase",
		                 is_postgresql=True)
		logging.info("Database configuration file created successfully.")
	except Exception as e:
		logging.error(f"Error creating configuration files: {e}", exc_info=True)
		raise


def run_bot():
	"""
	Launch of the bot.

	:return: None
	"""
	logging.info("Bot is starting...")
	# Bot logic would be placed here in the future
	# For now, we just log the start action.
	logging.info("Bot started successfully. Ready to run tasks.")
