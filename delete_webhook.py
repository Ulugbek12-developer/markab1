import asyncio
from bot_setup import bot

async def main():
    print("Deleting webhook...")
    await bot.delete_webhook(drop_pending_updates=True)
    print("Webhook deleted successfully! You can now use 'python main.py' for polling.")

if __name__ == "__main__":
    asyncio.run(main())
