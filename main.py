"""
Главный файл запуска Ryabot Island с полной поддержкой Supabase
Версия 2.0 - Полный переход на Supabase Python SDK
"""
import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import os
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)

# Загружаем переменные окружения
load_dotenv()

# Проверка обязательных переменных для Supabase
REQUIRED_ENV_VARS = {
    "BOT_TOKEN": "Токен Telegram бота",
    "SUPABASE_URL": "URL проекта Supabase",
    "SUPABASE_ANON_KEY": "Публичный ключ Supabase"
}

def check_environment():
    """Проверяет наличие всех необходимых переменных окружения"""
    missing_vars = []

    for var, description in REQUIRED_ENV_VARS.items():
        if not os.getenv(var):
            missing_vars.append(f"{var} ({description})")

    if missing_vars:
        logger.error("❌ Отсутствуют обязательные переменные окружения:")
        for var in missing_vars:
            logger.error(f"   - {var}")
        logger.error("\n💡 Добавьте эти переменные в ваш .env файл:")
        logger.error("   SUPABASE_URL=https://your-project.supabase.co")
        logger.error("   SUPABASE_ANON_KEY=your-anon-key")
        logger.error("   BOT_TOKEN=your-bot-token")
        sys.exit(1)

async def init_supabase():
    """Инициализация подключения к Supabase"""
    logger.info("🔌 Инициализация Supabase...")

    try:
        from database.supabase_client import supabase_manager

        # Инициализируем клиент
        supabase_manager.initialize()

        # Проверяем подключение простым запросом
        test_result = await supabase_manager.execute_query(
            table="users",
            operation="count"
        )

        logger.info("✅ Supabase подключение работает")
        logger.info(f"📊 Пользователей в БД: {test_result or 0}")

        return True

    except Exception as e:
        logger.error(f"❌ Ошибка подключения к Supabase: {e}")
        logger.error("💡 Проверьте:")
        logger.error("   1. Правильность SUPABASE_URL и SUPABASE_ANON_KEY")
        logger.error("   2. Доступность интернета")
        logger.error("   3. Статус проекта в Supabase Dashboard")
        return False

async def setup_bot():
    """Настройка и создание бота с middleware"""
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher(storage=MemoryStorage())

    # Подключаем middleware для защиты от спама
    from middlewares.throttling import ThrottlingMiddleware
    dp.callback_query.middleware(ThrottlingMiddleware(rate_limit=0.3))

    # В функции setup_bot() добавьте после throttling middleware:

    from middlewares.energy_middleware import EnergyMiddleware

    # Подключаем энергетический middleware
    energy_middleware = EnergyMiddleware()
    dp.message.middleware(energy_middleware)
    dp.callback_query.middleware(energy_middleware)

    # Подключаем роутеры - ИСПРАВЛЕННАЯ ВЕРСИЯ
    logger.info("🔧 Подключение модулей...")

    try:
        # Список модулей с проверкой наличия router
        modules_to_load = [
            ('handlers.start', 'start'),
            ('handlers.academy', 'academy'),
            ('handlers.town', 'town'),
            ('handlers.farm', 'farm'),
            ('handlers.work', 'work'),
            ('handlers.citizen', 'citizen'),
            ('handlers.storage', 'storage'),
            ('handlers.rankings', 'rankings'),
            ('handlers.referral', 'referral'),
            ('handlers.about', 'about'),
            ('handlers.admin', 'admin')
        ]

        loaded_count = 0
        for module_path, module_name in modules_to_load:
            try:
                # Динамический импорт модуля
                module = __import__(module_path, fromlist=['router'])

                # Проверяем наличие router
                if hasattr(module, 'router'):
                    dp.include_router(module.router)
                    logger.info(f"   ✅ {module_name.capitalize()} модуль")
                    loaded_count += 1
                else:
                    logger.warning(f"   ⚠️ {module_name.capitalize()} модуль - router отсутствует")

            except ImportError as e:
                logger.warning(f"   ⚠️ {module_name.capitalize()} модуль - ошибка импорта: {e}")
            except Exception as e:
                logger.error(f"   ❌ {module_name.capitalize()} модуль - критическая ошибка: {e}")

        logger.info(f"📦 Загружено модулей: {loaded_count}/{len(modules_to_load)}")

        if loaded_count == 0:
            raise Exception("Не загружен ни один модуль!")

    except Exception as e:
        logger.error(f"❌ Критическая ошибка загрузки модулей: {e}")
        raise

    return bot, dp

async def get_bot_info(bot):
    """Получение информации о боте"""
    try:
        bot_info = await bot.get_me()
        logger.info(f"🤖 Бот: @{bot_info.username} ({bot_info.first_name})")
        logger.info(f"🆔 ID: {bot_info.id}")
        return bot_info
    except Exception as e:
        logger.error(f"❌ Ошибка получения информации о боте: {e}")
        raise

async def get_game_statistics():
    """Получение игровой статистики"""
    try:
        from database.models import get_island_stats
        stats = await get_island_stats()

        logger.info("📊 Статистика Ryabot Island:")
        logger.info(f"   👥 Всего игроков: {stats.get('total_players', 0)}")
        logger.info(f"   🟢 Активных: {stats.get('online_players', 0)}")
        logger.info(f"   💠 RBTC сегодня: {stats.get('daily_rbtc', 0):.2f}")
        logger.info(f"   🗺️ Активных экспедиций: {stats.get('active_expeditions', 0)}")

        return stats
    except Exception as e:
        logger.warning(f"⚠️ Не удалось получить статистику: {e}")
        return None

async def main():
    """Основная функция запуска бота"""

    # Приветствие
    logger.info("=" * 60)
    logger.info("🏝️  RYABOT ISLAND - ЗАПУСК СЕРВЕРА")
    logger.info("🔄  Версия 2.0 - Полный переход на Supabase")
    logger.info("=" * 60)

    # 1. Проверка окружения
    logger.info("1️⃣ Проверка переменных окружения...")
    check_environment()
    logger.info("✅ Все переменные найдены")

    # 2. Инициализация Supabase
    logger.info("2️⃣ Подключение к Supabase...")
    if not await init_supabase():
        logger.error("❌ Не удалось подключиться к Supabase")
        sys.exit(1)

    # 3. Создание и настройка бота
    logger.info("3️⃣ Создание бота...")
    try:
        bot, dp = await setup_bot()
    except Exception as e:
        logger.error(f"❌ Ошибка создания бота: {e}")
        sys.exit(1)

    # 4. Получение информации о боте
    logger.info("4️⃣ Проверка бота...")
    try:
        await get_bot_info(bot)
    except Exception as e:
        logger.error(f"❌ Проблемы с ботом: {e}")
        sys.exit(1)

    # 5. Получение игровой статистики
    logger.info("5️⃣ Загрузка игровой статистики...")
    await get_game_statistics()

    # 6. Запуск бота
    logger.info("=" * 60)
    logger.info("🚀 ЗАПУСК RYABOT ISLAND")
    logger.info("=" * 60)

    try:
        # Удаляем возможный webhook
        await bot.delete_webhook(drop_pending_updates=True)

        # Запускаем polling
        logger.info("🔄 Режим: Long Polling")
        logger.info("✨ Остров готов к приключениям!")
        logger.info("🛑 Для остановки используйте Ctrl+C")

        await dp.start_polling(
            bot,
            drop_pending_updates=True,
            allowed_updates=["message", "callback_query"]
        )

    except KeyboardInterrupt:
        logger.info("⏹️ Получен сигнал остановки (Ctrl+C)")

    except Exception as e:
        logger.error(f"❌ Критическая ошибка во время работы: {e}")

    finally:
        # Корректное завершение
        logger.info("=" * 60)
        logger.info("🧹 ЗАВЕРШЕНИЕ РАБОТЫ")
        logger.info("=" * 60)

        # Закрываем сессию бота
        try:
            await bot.session.close()
            logger.info("✅ Сессия бота закрыта")
        except Exception as e:
            logger.error(f"❌ Ошибка при закрытии бота: {e}")

        logger.info("✅ Supabase соединения освобождены")
        logger.info("👋 Ryabot Island остановлен. До встречи!")

def run():
    """Точка входа с обработкой исключений"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 До свидания!")
    except Exception as e:
        print(f"\n💥 Критическая ошибка запуска: {e}")
        print("💡 Проверьте .env файл и переменные окружения")
        sys.exit(1)

if __name__ == '__main__':
    run()
