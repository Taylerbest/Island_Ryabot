from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from aiogram.fsm.storage.memory import MemoryStorage
import os
from dotenv import load_dotenv
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

app = FastAPI()
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Регистрируй роутеры из твоих handlers
# Например:
from handlers.start import router as start_router
from handlers.academy import router as academy_router
from handlers.town import router as town_router
# ... импорт других роутеров

dp.include_router(start_router)
dp.include_router(academy_router)
dp.include_router(town_router)
# ... подключить остальные роутеры

@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update(**data)
    await dp.process_update(update)
    return {"ok": True}

@app.on_event("startup")
async def on_startup():
    webhook_url = os.getenv("WEBHOOK_URL")  # публичный ngrok- или другой адрес с /webhook
    await bot.set_webhook(webhook_url)
    print("Webhook установлен:", webhook_url)

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()
    await bot.session.close()
