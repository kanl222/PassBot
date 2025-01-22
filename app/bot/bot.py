
from os import getenv
from aiogram import Bot, Dispatcher
from .storage import SQLStorage

from .handlers import __all_routes
from .keyboards.handler import router_handler_command
from ..core.settings import settings
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

storage = SQLStorage('BotStorage.db')
bot = Bot(token=settings.telegram_bot_token,default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=storage)
dp.include_routers(__all_routes)
dp.include_routers(router_handler_command)
__all__: list[str] = ['dp', 'bot']


