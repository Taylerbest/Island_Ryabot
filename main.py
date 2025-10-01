"""
Главный файл запуска Ryabot Island (только для polling разработки)
Поддержка только PostgreSQL/Supabase
"""
import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import os
from dotenv import load_dotenv

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)

# Загружаем переменные окружения
load_dotenv()

# Проверка обязательных переменных
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    logging.error("❌ BOT_TOKEN не найден в .env файле!")
    sys.exit(1)

# Импорт обработчиков (после проверки переменных)
from handlers import (
    start, academy, town, farm, work,
    citizen, storage, rankings, referral, about, admin
)

# Импорт middleware
from middlewares.throttling import ThrottlingMiddleware

async def main():
    """Основная функция запуска бота"""

    # Создаем бота и диспетчер
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Подключаем middleware для защиты от спама
    dp.callback_query.middleware(ThrottlingMiddleware(rate_limit=0.3))

    # Инициализация базы данных Supabase
    logging.info("🔌 Инициализация подключения к Supabase...")
    try:
        from database.models import initialize_db_pool, init_database, create_academy_tables

        # Инициализация пула соединений
        await initialize_db_pool()
        logging.info("✅ Пул соединений PostgreSQL инициализирован")

        # Создание таблиц
        await init_database()
        logging.info("✅ Основные таблицы созданы")

        await create_academy_tables()
        logging.info("✅ Таблицы академии созданы")

    except Exception as e:
        logging.error(f"❌ Ошибка инициализации базы данных: {e}")
        sys.exit(1)

    # Подключаем все роутеры
    routers = [
        start.router,      # Старт и туториал
        academy.router,    # Академия и наём специалистов
        town.router,       # Город и постройки
        farm.router,       # Ферма и животные
        work.router,       # Работа и заработок
        citizen.router,    # Личный кабинет жителя
        storage.router,    # Склад и инвентарь
        rankings.router,   # Рейтинги и достижения
        referral.router,   # Реферальная система
        about.router,      # Информация об игре
        admin.router       # Админские команды
    ]

    for i, router in enumerate(routers, 1):
        dp.include_router(router)
        logging.info(f"✅ Роутер {i}/{len(routers)} подключен")

    # Запускаем бота
    logging.info("🚀 Запуск Ryabot Island...")
    try:
        # Удаляем webhook (если был установлен)
        await bot.delete_webhook(drop_pending_updates=True)

        # Получаем информацию о боте
        bot_info = await bot.get_me()
        logging.info(f"🤖 Бот @{bot_info.username} запущен в режиме polling")

        # Статистика острова
        try:
            from database.models import get_island_stats
            stats = await get_island_stats()
            logging.info(f"🏝️ Статистика: {stats['total_players']} игроков, {stats['active_expeditions']} экспедиций")
        except Exception as e:
            logging.warning(f"⚠️ Не удалось получить статистику: {e}")

        # Запускаем polling
        await dp.start_polling(
            bot,
            drop_pending_updates=True,
            allowed_updates=["message", "callback_query"]
        )

    except KeyboardInterrupt:
        logging.info("⏹️ Получен сигнал остановки")

    except Exception as e:
        logging.error(f"❌ Критическая ошибка: {e}")

    finally:
        # Корректное закрытие
        logging.info("🧹 Завершение работы...")

        # Закрываем пул соединений с БД
        try:
            from database.models import close_connection_pool
            await close_connection_pool()
            logging.info("✅ Пул соединений закрыт")
        except Exception as e:
            logging.error(f"❌ Ошибка закрытия БД: {e}")

        # Закрываем сессию бота
        try:
            await bot.session.close()
            logging.info("✅ Сессия бота закрыта")
        except Exception as e:
            logging.error(f"❌ Ошибка закрытия бота: {e}")


if __name__ == '__main__':
    """Точка входа в приложение"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 До свидания!")
    except Exception as e:
        print(f"💥 Критическая ошибка запуска: {e}")
        sys.exit(1)
