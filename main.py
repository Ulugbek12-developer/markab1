import asyncio
import logging
import sys
from bot_setup import bot, dp
from database import init_db

async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    
    # Initialize database
    await init_db()
    
    # Set Bot Commands
    from aiogram.types import BotCommand, MenuButtonDefault
    commands = [
        BotCommand(command="start", description="Botni qayta yuklash / Перезагрузить бот"),
        BotCommand(command="branches", description="Bizning filiallar / Наши филиалы"),
        BotCommand(command="help", description="Yordam / Помощь")
    ]
    await bot.set_my_commands(commands)
    
    await bot.set_chat_menu_button(menu_button=MenuButtonDefault())
    
    # Delete webhook to prevent conflicts with polling
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Start polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped")
