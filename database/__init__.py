"""
Инициализация модуля базы данных для Ryabot Island
Версия 2.0 - Полный переход на Supabase
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Флаг инициализации для предотвращения повторных инициализаций
_db_initialized = False


async def initialize_database() -> bool:
    """
    Инициализация подключения к Supabase
    Заменяет старые функции initialize_db_pool() и init_database()

    Returns:
        bool: True если инициализация прошла успешно
    """
    global _db_initialized

    if _db_initialized:
        logger.info("✅ База данных уже инициализирована")
        return True

    try:
        # Инициализируем Supabase клиент
        from .supabase_client import supabase_manager
        supabase_manager.initialize()

        # Проверяем подключение простым запросом
        test_result = await supabase_manager.execute_query(
            table="users",
            operation="count"
        )

        logger.info(f"✅ Supabase подключение активно. Пользователей: {test_result or 0}")

        _db_initialized = True
        return True

    except Exception as e:
        logger.error(f"❌ Ошибка инициализации Supabase: {e}")
        return False


async def close_database():
    """
    Закрытие подключения к базе данных
    Для Supabase это заглушка - подключения закрываются автоматически
    """
    global _db_initialized

    logger.info("✅ Supabase подключения освобождены")
    _db_initialized = False


# Экспорт основных функций из models для удобства импорта
try:
    from .models import (
        # Пользователи
        get_user,
        create_user,
        get_user_language,
        update_user_language,
        update_user_resources,
        complete_tutorial,
        set_user_state,
        clear_user_state,

        # Академия
        get_hired_workers_count,
        can_hire_worker,
        hire_worker,
        get_training_slots_info,
        start_training,
        get_active_trainings,
        complete_trainings,
        get_specialists_count,

        # Статистика
        get_island_stats,

        # Служебные
        initialize_db_pool,  # Алиас для совместимости
        close_connection_pool,  # Алиас для совместимости
        init_database,  # Алиас для совместимости
        create_academy_tables  # Алиас для совместимости
    )

    logger.info("✅ Database models импортированы успешно")

except ImportError as e:
    logger.error(f"❌ Ошибка импорта models: {e}")


    # Создаем заглушки для критичных функций
    async def get_user(user_id: int):
        logger.error("get_user не доступен из-за ошибки импорта")
        return None


    async def create_user(user_id: int, username: str = None):
        logger.error("create_user не доступен из-за ошибки импорта")
        return None

# Экспорт Supabase клиента
try:
    from .supabase_client import supabase_manager, get_supabase_client

    logger.info("✅ Supabase client импортирован успешно")
except ImportError as e:
    logger.error(f"❌ Ошибка импорта supabase_client: {e}")
    supabase_manager = None
    get_supabase_client = None


# Алиасы для обратной совместимости со старым кодом
async def initialize_db_pool():
    """Алиас для совместимости. Использует новую функцию initialize_database()"""
    return await initialize_database()


async def close_connection_pool():
    """Алиас для совместимости. Использует новую функцию close_database()"""
    await close_database()


async def init_database():
    """Алиас для совместимости. Таблицы должны быть созданы в Supabase Dashboard"""
    logger.info("✅ Таблицы должны быть созданы через Supabase Dashboard (SQL Editor)")
    return True


async def create_academy_tables():
    """Алиас для совместимости. Таблицы должны быть созданы в Supabase Dashboard"""
    logger.info("✅ Таблицы академии должны быть созданы через Supabase Dashboard")
    return True


# Проверка целостности модуля
def check_database_module() -> tuple[bool, list[str]]:
    """
    Проверяет целостность модуля базы данных и готовность к работе

    Returns:
        tuple: (success: bool, errors: list[str])
    """
    errors = []

    # Проверяем наличие критичных компонентов
    if supabase_manager is None:
        errors.append("Supabase manager не инициализирован")

    if get_supabase_client is None:
        errors.append("Supabase client недоступен")

    # Проверяем переменные окружения
    import os
    if not os.getenv("SUPABASE_URL"):
        errors.append("SUPABASE_URL не установлен")

    if not os.getenv("SUPABASE_ANON_KEY"):
        errors.append("SUPABASE_ANON_KEY не установлен")

    return len(errors) == 0, errors


# Информация о модуле
__version__ = "2.0.0"
__database__ = "Supabase"
__compatibility__ = "PostgreSQL asyncpg -> Supabase Python SDK"

logger.info(f"🏝️ Ryabot Island Database Module v{__version__} ({__database__})")
