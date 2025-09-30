"""
Главный файл запуска Ryabot Island
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import os
from dotenv import load_dotenv

# Импортируем роутеры обработчиков
from handlers.start import router as start_router
from handlers.town import router as town_router
from handlers.academy import router as academy_router
from database.models import _connection_pool


# Будем добавлять по мере создания:
# from handlers.farm import router as farm_router
# from handlers.town import router as town_router
# и так далее...

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)

# Загружаем переменные окружения
load_dotenv()


async def main():
    # Создаем бота и диспетчер
    bot = Bot(token=os.getenv('BOT_TOKEN'))
    dp = Dispatcher(storage=MemoryStorage())

    # Подключаем роутеры
    dp.include_router(start_router)
    # dp.include_router(farm_router)
    dp.include_router(town_router)
    dp.include_router(academy_router)

    # Запускаем бота
    try:
        print("🌟 Ryabot Island запущен!")
        await dp.start_polling(bot)
    finally:
        # Закрываем пул соединений при выключении
        await _connection_pool.close_all()
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
