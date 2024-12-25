import asyncio
from typing import Dict, Any, Callable
from functools import wraps
from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.bot.handlers.teacher import DataParsingService
from app.db.models.users import User
from app.services.auth import authenticated_users
import logging

from app.services.users import get_user_instance


auth_router: Router = Router()


class AuthStates(StatesGroup):
    awaiting_login = State()
    awaiting_password = State()


def validate_input(error_message: str) -> Callable:
    """Decorator to validate user input."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(message: types.Message, state: FSMContext) -> None:
            text = message.text.strip() if message.text else ''
            if not text:
                await message.answer(error_message)
                return
            await func(message, state, text)
        return wrapper
    return decorator


async def handle_auth_response(message: types.Message, auth_response: Dict[str, Any]) -> None:
    """Centralized authentication response handling."""
    response_handlers = {
        "success": lambda r: f"Добро пожаловать, {r['user']}! Вы успешно авторизованы как {r['role']}.",
        "exists": lambda r: f"Вы уже зарегистрированы как {r['role']}. Добро пожаловать обратно, {r['user']}!",
        "no_group": lambda _: "Вы успешно зарегистрированы, но ваша группа еще не назначена. Пожалуйста, свяжитесь с вашим куратором.",
        "error": lambda _: "Аутентификация не удалась. Проверьте ваш логин и пароль."
    }

    message_text = response_handlers.get(
        auth_response.get("status", "error"),
        lambda _: "Неизвестный статус аутентификации."
    )(auth_response)

    await message.answer(message_text)


@auth_router.message(Command(commands=["start"]))
async def start_auth(message: types.Message, state: FSMContext) -> None:
    try:

        user: User | None = await get_user_instance(telegram_id=message.from_user.id)
        if user:
            if user:= user[0]:
                await message.answer(
                    f"Добро пожаловать обратно, {
                        user.full_name}! Вы зарегистрированы как {user.role}."
                )
                return

        await message.answer("Пожалуйста, введите свой логин:")
        await state.set_state(AuthStates.awaiting_login)

    except Exception as e:
        logging.error(f"Error during authentication process: {e}")
        await message.answer(
            "Произошла ошибка при проверке вашей учетной записи. Попробуйте позже."
        )


@auth_router.message(AuthStates.awaiting_login)
@validate_input("Логин не может быть пустым. Пожалуйста, введите ваш логин:")
async def handle_login(message: types.Message, state: FSMContext, login: str) -> None:
    await state.update_data(login=login)
    await message.answer("Отлично! Теперь введите свой пароль:")
    await state.set_state(AuthStates.awaiting_password)


@auth_router.message(AuthStates.awaiting_password)
@validate_input("Пароль не может быть пустым. Пожалуйста, введите ваш пароль:")
async def handle_password(message: types.Message, state: FSMContext, password: str) -> None:
    user_data: Dict[str, Any] = await state.get_data()
    login: str = user_data.get('login')

    if not login:
        await message.answer("Логин не найден. Пожалуйста, начните процесс заново с /start.")
        await state.clear()
        return

    auth_payload = {
        'id_user_telegram': message.from_user.id,
        'password': password,
        'login': login
    }

    try:
        auth_response = await authenticated_users(auth_payload)
        await handle_auth_response(message, auth_response)
        if auth_response.get('role',None) == 'teacher':
            asyncio.create_task(
                DataParsingService.parse_teacher_data(message, auth_payload)
            )

    except Exception as e:
        logging.error(f"Error during authentication: {e}")
        await message.answer("Произошла ошибка при аутентификации. Пожалуйста, попробуйте позже.")
    finally:
        await state.clear()
