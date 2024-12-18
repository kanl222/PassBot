from typing import Dict, Any
from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.services.auth import authenticated_users, check_user_in_db
import logging

# Initialize a router for handling common commands and authentication
common_router: Router = Router()

class AuthStates(StatesGroup):
    """
    States for the user authentication workflow.
    """
    awaiting_login = State()
    awaiting_password = State()

@common_router.message(Command(commands=["start"]))
async def start_auth(message: types.Message, state: FSMContext) -> None:
    """
    Initiates the user authentication process.
    If the user already exists in the database, greets them and skips authentication.

    Args:
        message (types.Message): The message object from the user.
        state (FSMContext): Finite State Machine context for handling the current state.
    """
    try:
        user = await check_user_in_db(telegram_id=message.from_user.id)

        if user.get("status") == "exists":
            await message.answer(
                f"Добро пожаловать обратно, {user['user']}! Вы зарегистрированы как {user['role']}."
            )
            return

        await message.answer("Пожалуйста, введите свой логин:")
        await state.set_state(AuthStates.awaiting_login)

    except Exception as e:
        logging.error(f"Error during authentication process: {e}")
        await message.answer(
            "Произошла ошибка при проверке вашей учетной записи. Попробуйте позже."
        )

@common_router.message(AuthStates.awaiting_login)
async def handle_login(message: types.Message, state: FSMContext) -> None:
    """
    Handles the user's login input and transitions to the password input state.

    Args:
        message (types.Message): The message object containing the login.
        state (FSMContext): Finite State Machine context for handling the current state.
    """
    login: str = message.text.strip()

    if not login:
        await message.answer("Логин не может быть пустым. Пожалуйста, введите ваш логин:")
        return

    await state.update_data(login=login)
    await message.answer("Отлично! Теперь введите свой пароль:")
    await state.set_state(AuthStates.awaiting_password)

@common_router.message(AuthStates.awaiting_password)
async def handle_password(message: types.Message, state: FSMContext) -> None:
    """
    Handles the user's password input, completes the authentication process, 
    and provides feedback based on the result.

    Args:
        message (types.Message): The message object containing the password.
        state (FSMContext): Finite State Machine context for handling the current state.
    """
    password: str = message.text.strip()

    if not password:
        await message.answer("Пароль не может быть пустым. Пожалуйста, введите ваш пароль:")
        return

    user_data: Dict[str, Any] = await state.get_data()
    login: str = user_data.get('login')

    if not login:
        await message.answer("Логин не найден. Пожалуйста, начните процесс заново с /start.")
        await state.clear()
        return

    telegram_id: int = message.from_user.id
    auth_payload = {
        'id_user_telegram': telegram_id,
        'password': password,
        'login': login
    }

    try:
        auth_response = await authenticated_users(auth_payload)

        if auth_response.get("status") == "success":
            await message.answer(
                f"Добро пожаловать, {auth_response['user']}! Вы успешно авторизованы как {auth_response['role']}."
            )
        elif auth_response.get("status") == "exists":
            await message.answer(
                f"Вы уже зарегистрированы как {auth_response['role']}. Добро пожаловать обратно, {auth_response['user']}!"
            )
        elif auth_response.get("status") == "no_group":
            await message.answer(
                "Вы успешно зарегистрированы, но ваша группа еще не назначена. Пожалуйста, свяжитесь с вашим куратором."
            )
        else:
            await message.answer("Аутентификация не удалась. Проверьте ваш логин и пароль.")
    except Exception as e:
        logging.error(f"Error during authentication: {e}")
        await message.answer("Произошла ошибка при аутентификации. Пожалуйста, попробуйте позже.")
    finally:
        await state.clear()

@common_router.message(Command(commands=["help"]))
async def send_help(message: types.Message) -> None:
    """
    Provides the user with a list of available bot commands.

    Args:
        message (types.Message): The message object from the user.
    """
    help_text = """
    Доступные команды:
    /start - Начать процесс аутентификации
    /help - Получить список доступных команд
    /profile - Просмотреть ваш профиль
    """
    await message.reply(help_text)
