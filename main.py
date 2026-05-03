import asyncio
import logging
import sys
from bot_setup import bot, dp
from database import init_db

async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    
    # Initialize database
    await init_db()
    
    # Set WebApp Menu Button (O'zingizning havolangizni shu yerga yozing)
    from aiogram.types import MenuButtonWebApp, WebAppInfo
    WEBAPP_URL = "https://markabstore.pythonanywhere.com/" # <-- Yangi havola
    
    await bot.set_chat_menu_button(
        menu_button=MenuButtonWebApp(
            text="🌐 Mini App",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )
    )
    
    # Delete webhook to prevent conflicts with polling
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Start polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped")
