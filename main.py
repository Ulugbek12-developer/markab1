import asyncio
import logging
import sys
import os
import django
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import config
from handlers import get_handlers_router
from database import init_db

async def main():
    # Setup Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    django.setup()

    # Initialize DB
    await init_db()

    # Initialize Bot and Dispatcher
    bot = Bot(token=config.BOT_TOKEN.get_secret_value())
    dp = Dispatcher(storage=MemoryStorage())

    me = await bot.get_me()
    print(f"Bot started: @{me.username}")

    # Include Routers
    dp.include_router(get_handlers_router())

    # Start Polling
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped")
