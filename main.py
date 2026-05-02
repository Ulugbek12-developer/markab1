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

    # Initialize Bot and Dispatcher with Proxy for PythonAnywhere Free accounts
    from aiogram.client.session.aiohttp import AiohttpSession
    session = AiohttpSession(proxy="http://proxy.server:3128")
    
    bot = Bot(token=config.BOT_TOKEN.get_secret_value(), session=session)
    dp = Dispatcher(storage=MemoryStorage())

    me = await bot.get_me()
    print(f"Bot started: @{me.username}")

    # Include Routers
    dp.include_router(get_handlers_router())

    # Set WebApp Menu Button
    from aiogram.types import MenuButtonWebApp, WebAppInfo
    await bot.set_chat_menu_button(
        menu_button=MenuButtonWebApp(
            text="🌐 Mini App",
            web_app=WebAppInfo(url="https://markab2.pythonanywhere.com/")
        )
    )

    # Error handler — botni xato bo'lsa ham to'xtatmaslik uchun (aiogram 3.x)
    from aiogram.types import ErrorEvent
    
    @dp.error()
    async def error_handler(event: ErrorEvent):
        import traceback
        exc = event.exception
        print(f"❌ Handler xatosi: {type(exc).__name__}: {exc}")
        traceback.print_exception(type(exc), exc, exc.__traceback__)
        return True  # xatoni ushladik, botni davom ettir

    # Start Polling
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    
    # Auto-restart polling on network errors
    while True:
        try:
            print("Polling boshlanmoqda...")
            await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        except Exception as e:
            import traceback
            print(f"Polling xatosi: {e}")
            traceback.print_exc()
            print("5 soniyadan so'ng qayta urinib ko'ramiz...")
            await asyncio.sleep(5)
            
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped")
    except Exception as e:
        import traceback
        print(f"XATO: {e}")
        traceback.print_exc()
