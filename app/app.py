import asyncio
import logging

from .core.logging_app import setup_logging
from .core import initialization_settings
from .core.settings import TEST_MODE, settings

try:
    setup_logging()
    initialization_settings()
except ValueError as e:
    from .tools.create_config import create_config_files

    create_config_files()

from .db import db_session_manager
from .core.settings import get_db_url

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

def run_bot():
    """
    Launch the bot, ensuring parsing availability first.

    :return: None
    """
    try:
        if settings.IS_TELEGRAM_BOT_TOKEN:
            from .bot_telegram import running_bot
            logging.info("Bot is starting...")
            asyncio.run(running_bot())
            logging.info("Bot started successfully. Ready to run tasks.")
        else:
            logging.error('Telegram bot token is missing. Bot will not start.')
    except Exception as e:
        logging.error(f"An error occurred while starting the bot: {e}", exc_info=True)
        raise
