import logging
import os
import random
import pandas as pd
import xlsxwriter

from datetime import date, timedelta, datetime
from aiogram import types, Router, Bot
from aiogram.filters import Command, CommandObject
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from app.bot.handlers.common import back_to_menu
from app.core.settings import DIR_DATA, tz
from app.services.teacher import TeacherDataService
from app.services.visiting import parse_visiting_of_pair
from app.bot.keyboards import teacher_menu_keyboard, period_keyboard,absences_format_keyboard
from .support import is_teacher, is_teacher_of_data

teacher_router = Router()


class PeriodSelection(StatesGroup):
    waiting_for_period = State()
    waiting_for_custom_period = State()
    
class AbsencesFormat(StatesGroup):
    waiting_for_format = State()



async def _get_dates_from_period(period: str, today: date) -> tuple[date, date]:
    if period== "За сегодня":
        return today,today
    elif period == "Последние 7 дней":
        return today - timedelta(days=7), today
    elif period == "Последние 30 дней":
        return today - timedelta(days=30), today
    else:
        raise ValueError("Invalid period")

async def _process_visiting(message: types.Message, start_date: date, end_date: date) -> None:
    try:
        await message.answer("Начинаем парсинг данных о посещениях...", reply_markup=teacher_menu_keyboard)
        await parse_visiting_of_pair(teacher_telegram_id=message.from_user.id, start_date=start_date, end_date=end_date)
        await message.answer("Парсинг данных о посещениях успешно завершён.")
    except Exception as e:
        logging.error(f"Parsing error: {e}")
        await message.answer(f"Произошла ошибка при парсинге данных о посещениях: {e}")


async def _process_absences(message: types.Message, start_date: date, end_date: date, to_file: bool = False) -> None:
    """
    Processes student absences for a given date range and sends results as a message or file.
    """
    absences_data = await TeacherDataService.fetch_student_absences(message.from_user.id, start_date, end_date)

    if not absences_data:
        await message.reply("Пропусков нет.", reply_markup=teacher_menu_keyboard)
        return

    if to_file:
        await _generate_absences_file(message, absences_data)
    else:
        await _send_absences_summary(message, absences_data)


async def _generate_absences_file(message: types.Message, absences_data: dict) -> None:
    """
    Generates an Excel file with absence details and sends it to the user.
    """
    filename = f"{DIR_DATA}/files_telegram/absences_{message.from_user.id}_{random.randint(100000, 999999)}.xlsx"
    os.makedirs(os.path.dirname(filename), exist_ok=True) 
    workbook = xlsxwriter.Workbook(filename)

    for group_name, group_data in absences_data.items():
        worksheet = _create_group_worksheet(workbook, group_name, group_data)

    workbook.close()

    with open(filename, "rb") as file:
        await message.answer_document(
            types.BufferedInputFile(file.read(), filename=filename),
            reply_markup=teacher_menu_keyboard,
        )


def _create_group_worksheet(workbook, group_name: str, group_data: dict):# -> Any:
    """
    Creates a worksheet for a specific group in the Excel file.
    """
    worksheet = workbook.add_worksheet(group_name)
    date_format = workbook.add_format({'num_format': 'yyyy-mm-dd'})
    students = group_data["data"]

    dates = sorted(
        {date_str for student_data in students.values()
         for date_str in student_data['dates']}
    )

    worksheet.write_row(0, 1, dates, date_format)
    worksheet.write(0, 0, "Имя студента")
    worksheet.write(0, len(dates) + 1, "Total")

    for row, (student_id, data) in enumerate(students.items(), start=1):
        worksheet.write(row, 0, data['name'])
        total_absences = 0

        for col, date_str in enumerate(dates, start=1):
            count = data['dates'].count(date_str)
            worksheet.write(row, col, count)
            total_absences += count

        worksheet.write(row, len(dates) + 1, total_absences)

    last_row = len(students) + 1
    worksheet.write(last_row, 0, "Grand Total")
    for col, date_str in enumerate(dates, start=1):
        column_sum = sum(students[student_id]['dates'].count(
            date_str) for student_id in students)
        worksheet.write(last_row, col, column_sum)
    worksheet.write(last_row, len(
        dates) + 1, sum(len(students[student_id]['dates']) for student_id in students))

    return worksheet


async def _send_absences_summary(message: types.Message, absences_data: dict) -> None:
    """
    Sends a text summary of absences for each group.
    """
    for group_name, group_data in absences_data.items():
        group = group_data["group"]
        last_parsed_at = group.attendance_logs[0].last_parsed_at if group.attendance_logs else "Никогда"
        formatted_last_parsed = last_parsed_at.strftime('%d-%m-%Y %H:%M')
        caption = f"{group_name} (данные обновлялись {formatted_last_parsed}):"

        absences_text = f"{caption}\n"
        students = group_data["data"]

        if students:
            absences_text += "\n".join(
                f"  - {student_data['name']
                       }: {len(student_data['dates'])} пропусков"
                for student_data in students.values()
            )
        else:
            absences_text += "  Пропусков нет."

        await message.reply(absences_text, reply_markup=teacher_menu_keyboard)


async def _process_period_selection(message: types.Message, state: FSMContext, command: str) -> None:
    today = date.today()
    now = datetime.now(tz) 
    end_of_day = now.replace(hour=20, minute=0, second=0, microsecond=0)
    if now < end_of_day: 
                tomorrow = today - timedelta(days=1)
                end_date = tomorrow
    try:
        if message.text == "Указать период":
            await message.reply("Пожалуйста, укажите период в формате ГГГГ-ММ-ДД - ГГГГ-ММ-ДД", reply_markup=ReplyKeyboardRemove())
            await state.set_state(PeriodSelection.waiting_for_custom_period)
            await state.update_data(command=command)
        elif message.text == 'Назад':
            await back_to_menu(message, state)
        else:
            start_date, end_date = await _get_dates_from_period(message.text, today)

            if command == "visiting":
                await _process_visiting(message, start_date, end_date)
            elif command in {"absences", "absencesfile"}:
                await _process_absences(message, start_date, end_date, to_file=(command == "absencesfile"))
            await state.clear()

    except ValueError:
        await message.reply("Неверный выбор периода.")
        return await state.clear()
    
@teacher_router.message(Command(commands=["groups"]))
@is_teacher_of_data
async def list_groups(message: types.Message) -> None:
    """List teacher's groups."""
    groups = await TeacherDataService.fetch_groups(message.from_user.id)
    if groups:
        group_names = "\n".join(group["name"] for group in groups)
        await message.answer(f"Ваши группы:\n{group_names}")
    else:
        await message.answer("У вас нет групп.")


@teacher_router.message(Command(commands=["parse"]))
@is_teacher
async def parse_data(message: types.Message) -> None:
    """Initiate data parsing process."""
    try:
        await message.answer("Начинаем парсинг данных...",reply_markup=teacher_menu_keyboard)
        await TeacherDataService.parse_and_update_teacher_data(telegram_id=message.from_user.id)
        await message.answer("Парсинг данных успешно завершён.")
    except Exception as e:
        logging.error(f"Parsing error: {e}")
        await message.answer(f"Произошла ошибка при парсинге данных: {e}")


@teacher_router.message(Command(commands=["students"]))
@is_teacher_of_data
async def students_for_message(message: types.Message) -> str:
        """Fetches students curated by a teacher and formats them for a Telegram message."""
        teacher_id = message.from_user.id
        students_data = await TeacherDataService.fetch_students(teacher_id)
        if not students_data:
            return "У вас нет студентов."

        absences_text = "Список ваших студентов:\n"
        for group_name, students in students_data.items():
            absences_text += f"\nГруппа: {group_name}\n"
            if students:
                for row,student in enumerate(students,start=1):
                    absences_text += f"\t{row}) {student.full_name}\n"
            else:
                absences_text += "  В этой группе нет студентов.\n"

        await message.reply(absences_text,reply_markup=teacher_menu_keyboard)


@teacher_router.message(Command(commands=["visiting"]))
@is_teacher_of_data
async def cmd_visiting(message: types.Message, state: FSMContext, command: CommandObject):
    await message.reply("Выберите период для парсинга посещений:", reply_markup=period_keyboard)
    await state.set_state(PeriodSelection.waiting_for_period)
    if isinstance(command, CommandObject):
        await state.update_data(command=command.command)
    else:
        await state.update_data(command=command)


@teacher_router.message(PeriodSelection.waiting_for_period)
async def process_visiting_period(message: types.Message, state: FSMContext):
    data = await state.get_data()
    command = data.get("command")
    await _process_period_selection(message, state, command)


@teacher_router.message(PeriodSelection.waiting_for_custom_period)
async def process_custom_period(message: types.Message, state: FSMContext):
    try:
        start_str, end_str = message.text.split(" - ")
        start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_str, "%Y-%m-%d").date()

        command = (await state.get_data()).get("command")
        if command == "visiting":
            await _process_visiting(message, start_date, end_date)
        elif command in ("absences", "absencesfile"):
            await _process_absences(message, start_date, end_date, to_file=(command == "absencesfile"))
        await state.clear()
    except ValueError:
        await message.reply("Неверный формат даты. Пожалуйста, используйте формат ГГГГ-ММ-ДД - ГГГГ-ММ-ДД.")


@teacher_router.message(Command(commands=["absences", "absencesfile"]))
@is_teacher_of_data
async def cmd_absences(message: types.Message, state: FSMContext, command: CommandObject):
    await message.reply("Выберите период:", reply_markup=period_keyboard)
    await state.set_state(PeriodSelection.waiting_for_period)
    if isinstance(command, CommandObject):
        await state.update_data(command=command.command)
    else:
        await state.update_data(command=command)


@teacher_router.message(PeriodSelection.waiting_for_period)
async def process_absences_period(message: types.Message, state: FSMContext):
    data = await state.get_data()
    command = data.get("command")
    await _process_period_selection(message, state, command)


@is_teacher
async def cmd_form_absences(message: types.Message, state: FSMContext):
    await message.reply("Выберите формат отчета о пропусках:", reply_markup=absences_format_keyboard)
    await state.set_state(AbsencesFormat.waiting_for_format)


@teacher_router.message(AbsencesFormat.waiting_for_format)
async def process_absences_format(message: types.Message, state: FSMContext):
    if message.text == "Файлом":
        await state.update_data(command='absencesfile')
        await message.reply("Вы выбрали формат: Файлом", reply_markup=period_keyboard)
        await state.set_state(PeriodSelection.waiting_for_period)
    elif message.text == "Сообщением":
        await state.update_data(command='absences')
        await message.reply("Вы выбрали формат: Сообщением", reply_markup=period_keyboard)
        await state.set_state(PeriodSelection.waiting_for_period)
    elif message.text == "Назад":
        await back_to_menu(message, state)
    else:
        await message.reply("Неверный выбор формата.")
