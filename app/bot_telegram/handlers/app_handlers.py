from aiogram import Router,types
from typing import List, Tuple

from aiogram import types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

main_route = Router('main')

@main_route.message(Command(commands=['start']))
async def start_command(message: types.Message, state: FSMContext):
    pass