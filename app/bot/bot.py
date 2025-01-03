
from aiogram import Bot, Dispatcher
from aiogram_sqlite_storage.sqlitestore import SQLStorage
from .handlers import __all_routes
from ..core.settings import settings


storage = SQLStorage('BotStorage.db', serializing_method='pickle')
bot = Bot(token=settings.telegram_bot_token)
dp = Dispatcher(storage=storage)

dp.include_routers(__all_routes)
__all__: list[str] = ['dp', 'bot']
