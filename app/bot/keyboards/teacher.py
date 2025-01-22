from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
teacher_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Группы"),
            KeyboardButton(text="Студенты"),
        ],
        [
            KeyboardButton(text="Пропуски"),
        ],
        [KeyboardButton(text="Обновить данные")],
    ],
    resize_keyboard=True,
)
update_data_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Студенты и группы")],
        [KeyboardButton(text="Посещения")],
        [KeyboardButton(text="Назад")],
    ],
    resize_keyboard=True,
)

period_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="За сегодня")],
            [KeyboardButton(text="Последние 7 дней")],
            [KeyboardButton(text="Последние 30 дней")],
            [KeyboardButton(text="Указать период")],
            [KeyboardButton(text="Назад")],
        ],
        resize_keyboard=True,
    )

absences_format_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Файлом"), KeyboardButton(text="Сообщением")],
        [KeyboardButton(text="Назад")], 
    ],
    resize_keyboard=True,
    one_time_keyboard=True, 
)