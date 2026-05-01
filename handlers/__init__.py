from aiogram import Router
from . import common, sell, buy, admin, price

def get_handlers_router() -> Router:
    router = Router()
    router.include_router(common.router)
    router.include_router(sell.router)
    router.include_router(buy.router)
    router.include_router(admin.router)
    router.include_router(price.router)
    return router
