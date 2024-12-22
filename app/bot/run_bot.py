import logging
import asyncio
from contextlib import asynccontextmanager
from .bot import bot, dp

@asynccontextmanager
async def bot_session():
    """
    Async context manager for managing bot lifecycle.
    
    Handles bot initialization, polling, and graceful shutdown.
    """
    try:
        logging.info("Initializing bot...")
        await bot.delete_webhook(drop_pending_updates=True)
        yield
    except Exception as e:
        logging.error(f"Bot initialization error: {e}")
        raise
    finally:
        logging.info("Shutting down bot...")
        await bot.session.close()

async def running_bot() -> None:
    """
    Run the Telegram bot with comprehensive error handling.
    """
    try:
        async with bot_session():
            await dp.start_polling(bot)
    except Exception as e:
        logging.critical(f"Critical bot error: {e}")
        raise
