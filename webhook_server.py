"""
FastAPI webhook сервер для Ryabot Island (только Supabase)
"""
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from aiogram.fsm.storage.memory import MemoryStorage
import os
from dotenv import load_dotenv
import logging
import asyncio

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

load_dotenv()

# Создание приложения
app = FastAPI(title="Ryabot Island", version="1.0.0")
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher(storage=MemoryStorage())

# Middleware
from middlewares.throttling import ThrottlingMiddleware

dp.callback_query.middleware(ThrottlingMiddleware(rate_limit=0.3))

# Все роутеры в одном блоке
from handlers import (
    start, academy, town, farm, work,
    citizen, storage, rankings, referral, about, admin
)

routers = [
    start.router, academy.router, town.router, farm.router,
    work.router, citizen.router, storage.router,
    rankings.router, referral.router, about.router, admin.router
]

for router in routers:
    dp.include_router(router)


# ================== ENDPOINTS ==================

@app.post("/webhook")
async def telegram_webhook(request: Request):
    """Обработка webhook от Telegram"""
    data = await request.json()
    update = Update(**data)
    await dp.feed_update(bot=bot, update=update)
    return {"ok": True}


@app.get("/health")
async def health_check():
    """Проверка работоспособности"""
    return {
        "status": "ok",
        "bot": "Ryabot Island",
        "version": "1.0.0",
        "database": "PostgreSQL/Supabase"
    }


# ================== LIFECYCLE EVENTS ==================

@app.on_event("startup")
async def on_startup():
    """Инициализация при запуске"""
    from database.models import (
        initialize_db_pool,
        init_database,
        create_academy_tables
    )

    # Инициализация PostgreSQL
    await initialize_db_pool()
    await init_database()
    await create_academy_tables()

    # Установка webhook
    webhook_url = os.getenv("WEBHOOK_URL")
    if not webhook_url:
        logging.error("❌ WEBHOOK_URL not set in environment variables")
        return

    try:
        webhook_info = await bot.get_webhook_info()

        if webhook_info.url == webhook_url:
            logging.info(f"✅ Webhook уже установлен: {webhook_url}")
        else:
            await bot.delete_webhook(drop_pending_updates=True)
            await asyncio.sleep(1)
            await bot.set_webhook(webhook_url, drop_pending_updates=True)
            logging.info(f"✅ Webhook установлен: {webhook_url}")

    except Exception as e:
        logging.error(f"❌ Ошибка установки webhook: {e}")


@app.on_event("shutdown")
async def on_shutdown():
    """Очистка при остановке"""
    from database.models import close_connection_pool

    await bot.delete_webhook()
    await bot.session.close()
    await close_connection_pool()

    logging.info("✅ Приложение остановлено")
