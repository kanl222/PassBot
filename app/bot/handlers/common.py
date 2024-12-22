
from aiogram import types, Router
from aiogram.filters import Command
common_router = Router()  

@common_router.message(Command(commands=["help"]))
async def send_help(message: types.Message) -> None:
    help_text = """
    Доступные команды:
    /start - Начать процесс аутентификации
    /help - Получить список доступных команд
    /profile - Просмотреть ваш профиль
    """
    await message.reply(help_text)
