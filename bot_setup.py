import os
import django
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.session.aiohttp import AiohttpSession
from config import config

# Setup Django before anything else
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
try:
    django.setup()
except Exception:
    pass

# Proxy only for PythonAnywhere Free accounts
if os.environ.get('PYTHONANYWHERE_DOMAIN'):
    from aiogram.client.session.aiohttp import AiohttpSession
    session = AiohttpSession(proxy="http://proxy.server:3128")
    bot = Bot(token=config.BOT_TOKEN.get_secret_value(), session=session)
else:
    bot = Bot(token=config.BOT_TOKEN.get_secret_value())

dp = Dispatcher(storage=MemoryStorage())

# Include all routers
from handlers import get_handlers_router
dp.include_router(get_handlers_router())
