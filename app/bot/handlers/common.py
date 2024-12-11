from aiogram import Dispatcher, types, Router
from aiogram.filters import Command

common_router:Router  = Router()

@common_router.message(Command(commands=["start"]))
async def send_welcome(message: types.Message):
        await message.reply("Привет! Я бот. Напишите /help для списка доступных команд.")

@common_router.message(Command(commands=["help"]))
async def send_help(message: types.Message):
        help_text = """
        Доступные команды:
        /start - Начать работу с ботом
        /help - Получить список доступных команд
        /profile - Просмотреть ваш профиль
        """
        await message.reply(help_text)

