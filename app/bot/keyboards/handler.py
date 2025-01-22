from mailbox import Message
from aiogram import F, Bot, Router
from aiogram.fsm.context import FSMContext

from app.bot.handlers.common import back_to_menu, start_registration
from app.bot.handlers.teacher import list_groups,cmd_absences,cmd_visiting,parse_data, cmd_form_absences, students_for_message
from app.bot.keyboards.teacher import update_data_keyboard

router_handler_command = Router()

@router_handler_command.message(F.text == "Регистрация")
async def handle_registration(message: Message, state: FSMContext,):
    """Handle 'Регистрация' button click."""
    await state.clear()
    return await start_registration(message, state)


@router_handler_command.message(F.text == "Группы")
async def handle_list_groups(message: Message, state: FSMContext,):
    """Handle 'Группы' button click."""
    await state.clear()
    return await list_groups(message)

@router_handler_command.message(F.text == "Студенты")
async def get_period(message: Message,state: FSMContext):
    await state.clear()
    return await students_for_message(message)

@router_handler_command.message(F.text == "Пропуски")
async def handle_absences(message: Message, state: FSMContext,):
    """Handle 'Пропуски' button click."""
    await state.clear()
    return await cmd_form_absences(message, state)


@router_handler_command.message(F.text == "Студенты и группы")
async def handle_parsing(message: Message, state: FSMContext):
    """Handle 'Парсинг' button click."""
    await state.clear()
    return await parse_data(message)


@router_handler_command.message(F.text == "Посещения")
async def handle_visiting(message: Message, state: FSMContext):
    """Handle 'Посещения' button click."""
    await state.clear()
    return await cmd_visiting(message, state,'visiting')


@router_handler_command.message(F.text == "Назад")
async def handle_back(message: Message, state: FSMContext):
    """Handle 'Посещения' button click."""
    await state.clear()
    return await back_to_menu(message, state)


@router_handler_command.message(F.text == "Обновить данные")
async def handle_update_data(message: Message, state: FSMContext):
    """Handles 'Обновить данные' button click."""
    await state.clear()
    await message.answer(
        "Выберите тип данных для обновления:", reply_markup=update_data_keyboard
    )