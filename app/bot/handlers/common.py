from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.services.auth import authenticated_users
import logging

# Initialize a router for common commands
common_router: Router = Router()

class AuthStates(StatesGroup):
    """
    Defines states for user authentication workflow.
    """
    awaiting_login = State()
    awaiting_password = State()

@common_router.message(Command(commands=["start"]))
async def start_auth(message: types.Message, state: FSMContext) -> None:
    """
    Entry point for user authentication.
    Prompts the user to enter their login.

    Args:
        message: The incoming message object from the user.
        state: FSMContext for managing the current state.
    """
    await message.answer("Добро пожаловать! Пожалуйста, введите свой логин, чтобы продолжить:")
    await state.set_state(AuthStates.awaiting_login)

@common_router.message(AuthStates.awaiting_login)
async def handle_login(message: types.Message, state: FSMContext) -> None:
    """
    Handles the user's login input and prompts for the password.

    Args:
        message: The incoming message object containing the login.
        state: FSMContext for managing the current state.
    """
    login: str = message.text.strip()
    if not login:
        await message.answer("Логин не может быть пустым. Введите логин:")
        return

    await state.update_data(login=login)
    await message.answer("Отлично! Теперь введите свой пароль:")
    await state.set_state(AuthStates.awaiting_password)

@common_router.message(AuthStates.awaiting_password)
async def handle_password(message: types.Message, state: FSMContext) -> None:
    """
    Handles the user's password input, completes authentication, 
    and provides feedback based on the result.

Args:
 Йб       message: The incoming message object containing the password.
        state: FSMContext for managing the current state.
    """
    password = message.text.strip()
    if not password:
        await message.answer("Пароль не может быть пустым. Введите пароль:")
        return

    user_data = await state.get_data()
    login = user_data.get('login')

    if not login:
        await message.answer("Отсутствует логин. Пожалуйста, запустите процесс снова с помощью /start.")
        await state.clear()
        return

    telegram_id = message.from_user.id
    auth_payload = {
        'id_user_telegram': telegram_id,
        'password': password,
        'login': login
    }

    try:
        auth_response = await authenticated_users(auth_payload)

        if auth_response.get("status") == "success":
            await message.answer(
                    f"Добро пожаловать, {auth_response.get('user')}! Вы успешно аутентифицированы как {auth_response.get('role')}."            )
        elif auth_response.get("status") == "exists":
            await message.answer(
                f"Добро пожаловать обратно, {auth_response.get('user')}! Вы уже зарегистрированы как {auth_response.get('role')}."
            )
        elif auth_response.get("status") == "no_group":
            await message.answer(
                f"Здравствуйте {login}, вы успешно зарегистрированы, но ваша группа еще не назначена. Пожалуйста, свяжитесь с вашим куратором."
            )
        else:
            await message.answer(
                "Аутентификация не удалась. Проверьте логин и пароль и попробуйте еще раз."
            )

    except Exception as e:
        logging.error(f"Error during authentication: {e}")
        await message.answer(
            "Во время аутентификации произошла непредвиденная ошибка. Повторите попытку позже."
        )
    
    # Clear the FSM state
    await state.clear()

@common_router.message(Command(commands=["help"]))
async def send_help(message: types.Message) -> None:
    """
    Provides a list of available commands to the user.

    Args:
        message: The incoming message object from the user.
    """
    help_text = """
    Available Commands:
    /start - Start authentication process
    /help - Get the list of available commands
    /profile - View your profile
    """
    await message.reply(help_text)
