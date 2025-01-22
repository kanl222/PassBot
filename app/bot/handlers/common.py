
import logging
from mailbox import Message
from aiogram import F, types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from app.bot.handlers.auth import AuthStates
from app.bot.middlewares.ThrottlingMiddleware import ThrottlingMiddleware,rate_limit
from app.db.crud.users import get_user_of_telegram_id
from app.bot.keyboards import registration_kb,teacher_menu_keyboard
from aiogram.types import ReplyKeyboardRemove

from app.db.models.users import UserRole
common_router = Router()  
common_router.message.middleware(ThrottlingMiddleware())



@common_router.message(Command(commands=["help"]))
async def send_help(message: types.Message) -> None:
    """Send help message."""
    help_text = """
    Доступные команды:
    /start - Начать работу с ботом
    /register - Начать процесс регистрации
    /help - Получить список доступных команд
    /profile - Просмотреть ваш профиль
    """
    await message.reply(help_text)


@common_router.message(Command(commands=["start"])) 
async def start_bot(message: Message,state: FSMContext) -> None:
    """Handle /start command."""
    user = await get_user_of_telegram_id(telegram_id=message.from_user.id)
    if user:
        if user.role == UserRole.TEACHER:
            await message.answer(f"Добро пожаловать обратно, {user.full_name}! Вы зарегистрированы как преподаватель.")
        elif user.role == UserRole.STUDENT:
            await message.answer(f"Добро пожаловать обратно, {user.full_name}! Вы зарегистрированы как студент.")
        return await back_to_menu(message,state)
    else:
        await message.answer("Вы не зарегистрированы.",reply_markup=registration_kb)

@common_router.message(Command(commands=["menu"]))
async def back_to_menu(message: Message, state: FSMContext):
    if state:
        await state.clear()
    user = await get_user_of_telegram_id(telegram_id=message.from_user.id)
    if user:
        if user.role == UserRole.TEACHER:
            await message.answer("Главное меню:", reply_markup=teacher_menu_keyboard)
        elif user.role == UserRole.STUDENT:
            await message.answer("Главное меню:")



@common_router.message(Command(commands=["registration"])) 
@rate_limit(5)
async def start_registration(message: Message, state: FSMContext) -> None: 
    """Handle /register command and start registration process."""
    try:
        user = await get_user_of_telegram_id(telegram_id=message.from_user.id)
        if user:
            await message.answer("Вы уже зарегистрированы.",reply_markup=ReplyKeyboardRemove())
            await back_to_menu(message, state)
            return 

        await message.answer("Пожалуйста, введите свой логин:")
        await state.set_state(AuthStates.awaiting_login)

    except Exception as e:
        logging.error(f"Error during registration process: {e}")
        await message.answer("Произошла ошибка при регистрации. Попробуйте позже.")
        

