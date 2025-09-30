from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from aiogram.fsm.storage.memory import MemoryStorage
import os
from dotenv import load_dotenv
import logging
import asyncio
from middlewares.throttling import ThrottlingMiddleware
from handlers.admin import router as admin_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

app = FastAPI()
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
dp.callback_query.middleware(ThrottlingMiddleware(rate_limit=0.3))
dp.include_router(admin_router)

# Регистрация всех роутеров
from handlers.start import router as start_router
from handlers.academy import router as academy_router
from handlers.town import router as town_router
from handlers.farm import router as farm_router
from handlers.work import router as work_router
from handlers.citizen import router as citizen_router
from handlers.storage import router as storage_router
from handlers.rankings import router as rankings_router
from handlers.referral import router as referral_router
from handlers.about import router as about_router

dp.include_router(start_router)
dp.include_router(academy_router)
dp.include_router(town_router)
dp.include_router(farm_router)
dp.include_router(work_router)
dp.include_router(citizen_router)
dp.include_router(storage_router)
dp.include_router(rankings_router)
dp.include_router(referral_router)
dp.include_router(about_router)


@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update(**data)
    await dp.feed_update(bot=bot, update=update)
    return {"ok": True}


@app.get("/health")
async def health_check():
    return {"status": "ok", "bot": "Ryabot Island", "version": "1.0.0"}


@app.on_event("startup")
async def on_startup():
    from database.models import init_database, create_academy_tables

    # Инициализация базы данных
    await init_database()
    await create_academy_tables()

    webhook_url = os.getenv("WEBHOOK_URL")

    try:
        # Проверяем текущий webhook
        webhook_info = await bot.get_webhook_info()

        if webhook_info.url == webhook_url:
            print(f"✅ Webhook уже установлен: {webhook_url}")
        else:
            # Удаляем старый и устанавливаем новый
            await bot.delete_webhook(drop_pending_updates=True)
            await asyncio.sleep(1)
            await bot.set_webhook(webhook_url, drop_pending_updates=True)
            print(f"✅ Webhook установлен: {webhook_url}")

    except Exception as e:
        print(f"❌ Ошибка установки webhook: {e}")


@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()
    await bot.session.close()
