from .bot import bot, dp

async def message() -> None:
    pass

async def running_bot() -> None:
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
