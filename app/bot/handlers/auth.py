import asyncio
from typing import Dict, Any, Callable
from functools import wraps
from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.services.auth import AuthService
from aiogram.types import ReplyKeyboardRemove
from app.bot.keyboards import teacher_menu_keyboard
import logging

from app.services.teacher import TeacherDataService


auth_router: Router = Router()




class AuthStates(StatesGroup):
    awaiting_login = State()
    awaiting_password = State()


def validate_input(error_message: str) -> Callable:
    """Decorator to validate user input."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(message: types.Message, state: FSMContext) -> None:
            text = message.text.strip() if message.text else ""
            if not text:
                await message.answer(error_message)
                return
            await func(message, state, text)

        return wrapper

    return decorator


async def handle_auth_response(
    message: types.Message, auth_response: Dict[str, Any]
) -> None:
    """Handles authentication responses and provides user feedback."""

    status = auth_response.get("status")
    user = auth_response.get("user")
    role = auth_response.get("role")
    details = auth_response.get("details") 

    if status == "success":
        if role:
            await message.answer(f"Добро пожаловать, {user}! Вы успешно авторизованы как студент.", reply_markup=ReplyKeyboardRemove())
        else:
            await message.answer(f"Добро пожаловать, {user}! Вы успешно авторизованы как преподаватель.",reply_markup=teacher_menu_keyboard)
    elif status == "updated":
        await message.answer(f"Добро пожаловать, {user}! Ваши данные обновлены. Вы авторизованы как студент.",reply_markup=ReplyKeyboardRemove())
    elif status == "exists":
        await message.answer(f"Вы уже зарегистрированы как {role}. Добро пожаловать обратно, {user}!")
    elif status == "no_group":
        await message.answer("Вы успешно зарегистрированы, но ваша группа еще не назначена. Пожалуйста, свяжитесь с вашим куратором.")
    elif status == "error":
        if details:  
            error_message = "Аутентификация не удалась."
            await message.answer(error_message)
    else:
        await message.answer("Неизвестный статус аутентификации.")


@auth_router.message(AuthStates.awaiting_login)
@validate_input("Логин не может быть пустым. Пожалуйста, введите ваш логин:")
async def handle_login(message: types.Message, state: FSMContext, login: str) -> None:
    await state.update_data(login=login)
    await message.answer("Отлично! Теперь введите свой пароль:")
    await state.set_state(AuthStates.awaiting_password)


@auth_router.message(AuthStates.awaiting_password)
@validate_input("Пароль не может быть пустым. Пожалуйста, введите ваш пароль:")
async def handle_password(
    message: types.Message, state: FSMContext, password: str
) -> None:
    user_data: Dict[str, Any] = await state.get_data()
    login: str = user_data.get("login")

    if not login:
        await message.answer(
            "Логин не найден. Пожалуйста, начните процесс заново с /start."
        )
        await state.clear()
        return

    auth_payload = {
        "id_user_telegram": message.from_user.id,
        "password": password,
        "login": login,
    }

    try:
        auth_response = await AuthService.authenticate_user(auth_payload)
        await handle_auth_response(message, auth_response)
        if auth_response.get("role", None) == "teacher":
            asyncio.create_task(
                TeacherDataService.parse_teacher_data(telegram_id=message.from_user.id)
            )

    except Exception as e:
        logging.error(f"Error during authentication: {e}")
        await message.answer(
            "Произошла ошибка при аутентификации. Пожалуйста, попробуйте позже."
        )
    finally:
        await state.clear()
