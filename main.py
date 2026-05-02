import asyncio
import logging
import sys
from bot_setup import bot, dp
from database import init_db

async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    
    # Initialize DB (creates tables if they don't exist)
    await init_db()

    print(f"Polling started for bot...")
    
    # Start polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped")
