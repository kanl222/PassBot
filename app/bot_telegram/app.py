import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

logging.getLogger("requests").setLevel(logging.WARNING)

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	await update.message.reply_text(f'Hello {update.effective_user.first_name}')


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	user_message = update.message.text
	await update.message.reply_text(user_message)


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	await update.message.reply_text("Sorry, I didn't understand that command.")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	if update and update.message:
		await update.message.reply_text('An error occurred while processing your request.')


def create_bot(token: str) -> ApplicationBuilder:
	app = ApplicationBuilder().token(token).build()
	app.add_handler(CommandHandler("hello", hello))
	app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
	app.add_handler(MessageHandler(filters.COMMAND, unknown_command))
	app.add_error_handler(error_handler)

	return app


