import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram_sqlite_storage.sqlitestore import SQLStorage

from ..core.logging_app import COLORS
from ..core.settings import settings

storage: SQLStorage = SQLStorage('BotStorage.db', serializing_method='pickle')

token: str = settings.TELEGRAM_BOT_TOKEN
dp: Dispatcher = Dispatcher(storage=storage)


async def init_bot() -> Bot:
    _bot: Bot = Bot(token=token)
    bot_info = await _bot.get_me()
    logging.info(f"\nBot launched:\n{COLORS['DEBUG']}NAME = {bot_info.full_name}]\nID = {bot_info.id}")
    return _bot


bot: Bot = asyncio.get_event_loop().run_until_complete(init_bot())

__all__ = ['dp', 'bot']
