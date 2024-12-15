from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.services.auth import authenticated_users
import logging

common_router:Router  = Router()

class AuthStates(StatesGroup):
    awaiting_login = State()
    awaiting_password = State()

@common_router.message(Command(commands=["start"]))
async def start_auth(message: types.Message, state: FSMContext) -> None:
    """
    Начало процесса аутентификации пользователя.
    """
    await message.answer("Пожалуйста, введите ваш логин:")
    await state.set_state(AuthStates.awaiting_login)

@common_router.message(AuthStates.awaiting_login)
async def handle_login(message: types.Message, state: FSMContext) -> None:
    """
    Обработчик логина пользователя.
    """
    login: str = message.text.strip()
    await state.update_data(login=login)
    await message.answer("Отлично! Теперь введите ваш пароль:")
    await state.set_state(AuthStates.awaiting_password)

@common_router.message(AuthStates.awaiting_password)
async def handle_password(message: types.Message, state: FSMContext) -> None:
    """
    Обработчик пароля пользователя и завершение процесса аутентификации.
    """
    password = message.text.strip()
    user_data = await state.get_data()
    login = user_data.get('login')
    telegram_id = message.from_user.id
    user_data = {
            'id_user_telegram': telegram_id,
            'password':password,
            'login':login
    }
    await authenticated_users(user_data)
    await message.answer(
            "Отлично! Сообщение будет отправлено твоему Тайному Санте."
    )
    await state.clear()



@common_router.message(Command(commands=["help"]))
async def send_help(message: types.Message) -> None:
        help_text = """
        Доступные команды:
        /start - Начать работу с ботом
        /help - Получить список доступных команд
        /profile - Просмотреть ваш профиль
        """
        await message.reply(help_text)

