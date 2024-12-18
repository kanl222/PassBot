import asyncio
import logging

from .core.logging_app import setup_logging
from .core import initialization_settings

try:
    from .core.settings import TEST_MODE, settings

    setup_logging()
    initialization_settings()
except FileNotFoundError as e:
    from .tools.create_config import create_config_files
    create_config_files()
except Exception as e:
    logging.error(f'{e}')
    raise

from .core.settings import get_db_url
from .db import db_session_manager
try:
    db_path: str = get_db_url()

    if not db_path:
        logging.error("Database path must be specified in the configuration file.")

    logging.info(f"Initializing database with path: {db_path}")
    db_session_manager.initialize(db_path)
except Exception as e:
    print(e)



def db_init_models() -> None:
    """
    Asynchronous initialization of database models.

    :return: None
    """
    try:
        asyncio.run(db_session_manager.init_models())
    except Exception as e:
        logging.error(f"Error initializing database models: {e}", exc_info=True)
        raise

def run_bot() -> None:
    """
    Launch the bot, ensuring parsing availability first.

    :return: None
    """
    try:
        if settings.IS_TELEGRAM_BOT_TOKEN:
            from .bot.run_bot import running_bot
            logging.info("Bot is starting...")
            asyncio.run(running_bot())
            logging.info("Bot started successfully. Ready to run tasks.")
        else:
            logging.error('Telegram bot token is missing. Bot will not start.')
    except Exception as e:
        logging.error(f"An error occurred while starting the bot: {e}", exc_info=True)
        raise
