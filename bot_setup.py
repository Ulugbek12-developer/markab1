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

# Session with Proxy for PythonAnywhere
session = AiohttpSession(proxy="http://proxy.server:3128")

bot = Bot(token=config.BOT_TOKEN.get_secret_value(), session=session)
dp = Dispatcher(storage=MemoryStorage())

# Include all routers
from handlers import get_handlers_router
dp.include_router(get_handlers_router())
