import asyncio
import logging
from .core import initialization_settings
from .core.logging import setup_logging
from .db import db_session_manager, get_db_url
from .tools.create_config import create_env
from .bot_telegram.app import create_bot



initialization_settings()




def db_init_models():
	"""
	Initialization of database models.

	:raises ValueError: If the database path is not specified in the configuration file.
	:return: None
	"""
	db_path = get_db_url()

	if not db_path:
		logging.error("Database path must be specified in the configuration file.")
		raise

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
		create_env(secret_key=settings_crypto.SECRET_KEY, db_user="dbuser", db_password="dbpassword",
		           db_host="localhost", db_name="mydatabase", )
		logging.info("Env configuration file created successfully.")
	except Exception as e:
		logging.error(f"Error creating configuration files: {e}", exc_info=True)
		raise


def run_bot():
	"""
	Launch of the bot.

	:return: None
	"""
	logging.info("Bot is starting...")
	create_bot('1685141690:AAHB1bO3D96_kHcCxvdCSyN2rLjmsvu3TTE').run_polling()
	logging.info("Bot started successfully. Ready to run tasks.")
