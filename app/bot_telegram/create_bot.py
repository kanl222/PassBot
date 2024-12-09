import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram_sqlite_storage.sqlitestore import SQLStorage

from ..core.logging_app import COLORS
from ..core.settings import settings
from .handlers import __all_handlers
storage: SQLStorage = SQLStorage('BotStorage.db', serializing_method='pickle')

token: str = settings.TELEGRAM_BOT_TOKEN
dp: Dispatcher = Dispatcher(storage=storage)


async def init_bot() -> Bot:
    """
    Initialize the bot, fetch its information, and display it in the logs.
    """
    _bot: Bot = Bot(token=token)
    bot_info = await _bot.get_me()
    logging.info(
        f"\n{COLORS['INFO']}Bot successfully launched!\n"
        f"{COLORS['DEBUG']}Bot Name: {bot_info.full_name}\n"
        f"Bot Username: @{bot_info.username}\n"
        f"Bot ID: {bot_info.id}\n"
    )

    return _bot


bot: Bot = asyncio.get_event_loop().run_until_complete(init_bot())
dp.include_router(__all_handlers)

__all__ = ['dp', 'bot']
