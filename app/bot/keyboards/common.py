from aiogram import Router
from aiogram.types import (
    ReplyKeyboardRemove, 
    ReplyKeyboardMarkup,
    KeyboardButton, 
    InlineKeyboardMarkup,
    InlineKeyboardButton
    )

kb_common_router = Router()  


registration_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Регистрация",callback_data="/registration")]],
    resize_keyboard=True,
    one_time_keyboard=True 
)


