import asyncio
import logging

from .core.logging_app import setup_logging
from .core import initialization_settings
from .core.settings import TEST_MODE

try:
    setup_logging()
    initialization_settings()
except ValueError as e:
    from .tools.create_config import create_config_files

    create_config_files()

from .db import db_session_manager, get_db_url
from app.session.session_manager import main_session_manager


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


def run_bot():
    """
    Launch the bot, ensuring parsing availability first.

    :return: None
    """
    try:
        if not TEST_MODE:
            logging.info("Initializing session manager...")
            main_session_manager()

        from .bot_telegram import running_bot
        logging.info("Bot is starting...")
        asyncio.get_event_loop().run_until_complete(running_bot())
        logging.info("Bot started successfully. Ready to run tasks.")
    except Exception as e:
        logging.error(f"An error occurred while starting the bot: {e}", exc_info=True)
        raise
