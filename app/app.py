import asyncio
import logging
import contextlib
import os

from .core.logging_app import setup_logging
from .core import initialization_settings

async def test_procedure():
    from app.core.settings import TEST_MODE
    if TEST_MODE:

        pass

async def initialize_application(is_models: bool = True) -> bool:
    """
    Comprehensive async application initialization.
    
    Consolidates logging, settings, and database initialization.
    """
    try:
        setup_logging()
        initialization_settings()

        from .core.settings import settings, DIR_DATA
        from .db import db_session_manager

        db_path = settings.get_database_url()
        if not db_path:
            logging.error("Database path must be specified in the configuration file.")
            return False

        logging.info(f"Initializing database with path: {db_path}")
        db_session_manager.initialize(db_path)
        if is_models:
            await db_session_manager.init_models()
        
        if DIR_DATA: 
            os.makedirs(os.path.dirname(f'{DIR_DATA}/'), exist_ok=True)    
        
        await test_procedure()
        if settings.telegram_bot_token:
            from .bot.run_bot import running_bot
            logging.info("Bot is starting...")
            await running_bot()
            logging.info("Bot started successfully. Ready to run tasks.")
        else:
            logging.error('Telegram bot token is missing. Bot will not start.')
            return False

        return True

    except FileNotFoundError:
        from .tools.create_config import create_config_files
        create_config_files()
        logging.warning("Configuration files created. Please restart the application.")
        return False
    except Exception as e:
        logging.error(f"Application initialization error: {e}", exc_info=True)
        return False

def main():
    """
    Entry point for application startup with graceful error handling.
    """
    with contextlib.suppress(KeyboardInterrupt, SystemExit):  
        try:
            asyncio.run(initialize_application())
        except Exception as e:  
            logging.critical(f"Unhandled exception: {e}", exc_info=True)

if __name__ == "__main__":
    main()
