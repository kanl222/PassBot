import asyncio
import logging

from .core.logging import setup_logging
from .db import db_session_manager, get_db_url
from .tools.create_config import create_env
from .core import initialization_settings

setup_logging()
initialization_settings()

from .parser.create_session import SessionManager


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
	from .tools.json_local import create_to_json_is_crypto
	user_data = {
		'login': user_login,
		'pwd': user_password
	}
	create_to_json_is_crypto('user', user_data)
	try:
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
		logging.info("Database configuration file created successfully.")
	except Exception as e:
		logging.error(f"Error creating configuration files: {e}", exc_info=True)
		raise

def check_parsing_availability() -> bool:
	"""
	Check if parsing is available by initializing a session and testing data retrieval.

	:return: bool - True if parsing is available, False otherwise.
	"""
	logging.info("Checking parsing availability...")
	session_manager = SessionManager()  # Initialize session
	if not session_manager.initialize_session():
		logging.error("Parsing check failed: Unable to establish a session.")
		return False

	# Attempt a test request to check if parsing is functional
	test_url = "https://www.osu.ru/iss/lks/?page=progress"  # Replace with a real parsing URL
	response = session_manager.get(test_url)
	if response and response.status_code == 200:
		logging.info("Parsing check successful. Parsing is available.")
		return True
	else:
		logging.error("Parsing check failed: Unable to retrieve test data.")
		return False

def run_bot():
	"""
	Launch of the bot, ensuring parsing availability first.

	:return: None
	"""
	if not check_parsing_availability():
		logging.error("Bot launch aborted: Parsing not available.")
		return

	from .bot_telegram import running_bot
	logging.info("Bot is starting...")
	asyncio.get_event_loop().run_until_complete(running_bot())
	logging.info("Bot started successfully. Ready to run tasks.")
