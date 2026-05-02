import asyncio
import logging
from bot_setup import bot

async def main():
    # Replace with your actual domain
    WEBHOOK_URL = "https://markab2.pythonanywhere.com/webhook/telegram/"
    
    print(f"Setting webhook to: {WEBHOOK_URL}")
    
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(url=WEBHOOK_URL)
    
    info = await bot.get_webhook_info()
    print(f"Webhook set successfully!")
    print(f"Current Status: {info}")

if __name__ == "__main__":
    asyncio.run(main())
