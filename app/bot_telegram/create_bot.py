from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode

from ..core.settings import settings

token = settings.TELEGRAM_BOT_TOKEN
bot: Bot = Bot(token=token)
dp: Dispatcher = Dispatcher(storage=MemoryStorage())
__all__ = ['dp', 'bot']
