from aiogram import Bot, Dispatcher, types
from aiogram.types import BotCommand

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

async def hello(message: types.Message):
	await message.reply(f"Hello {message.from_user.first_name}")


async def echo(message: types.Message):
	await message.reply(message.text)


async def unknown_command(message: types.Message):
	await message.reply("Sorry, I didn't understand that command.")


async def error_handler(update, exception):
	if update.message:
		await update.message.reply("An error occurred while processing your request.")
	return True


async def main(API_TOKEN: str):

	# Регистрация обработчиков
	dp.register_message_handler(hello, commands=['hello'])
	dp.register_message_handler(echo, Text())
	dp.register_message_handler(unknown_command, lambda message: message.text.startswith('/'))

	# Регистрация обработчика ошибок
	dp.register_errors_handler(error_handler)

	# Установка команд
	await set_commands(bot)


# Запуск поллинга

# Функция установки команд бота
async def set_commands(bot: Bot):
	commands = [
		BotCommand(command="/hello", description="Приветствие от бота"),
	]
	await bot.set_my_commands(commands)
