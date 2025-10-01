"""
Модели данных для работы с Supabase
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from database.supabase_client import supabase_manager

logger = logging.getLogger(__name__)


class User:
    def __init__(self, data: dict = None):
        if data:
            self.user_id = data.get('user_id', 0)
            self.username = data.get('username')
            self.language = data.get('language', 'ru')
            self.level = data.get('level', 1)
            self.experience = data.get('experience', 0)
            self.energy = data.get('energy', 100)
            self.ryabucks = data.get('ryabucks', 1000)
            self.rbtc = float(data.get('rbtc', 0.0))
            self.golden_shards = data.get('golden_shards', 0)
            self.quantum_keys = data.get('quantum_keys', 0)
            self.land_plots = data.get('land_plots', 1)
            self.tutorial_completed = bool(data.get('tutorial_completed', False))
            self.current_state = data.get('current_state')
            self.activity_data = data.get('activity_data')
            self.created_at = data.get('created_at')
            self.last_active = data.get('last_active')


# === USER FUNCTIONS ===

async def get_user(user_id: int) -> Optional[User]:
    """Получение пользователя из Supabase"""
    try:
        result = await supabase_manager.execute_query(
            table="users",
            operation="select",
            filters={"user_id": user_id}
        )

        if result.data:
            return User(result.data[0])
        return None
    except Exception as e:
        logger.error(f"Ошибка получения пользователя {user_id}: {e}")
        return None


async def create_user(user_id: int, username: str = None) -> Optional[User]:
    """Создание нового пользователя"""
    try:
        user_data = {
            "user_id": user_id,
            "username": username,
            "created_at": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat()
        }

        result = await supabase_manager.execute_query(
            table="users",
            operation="insert",
            data=user_data
        )

        if result.data:
            return User(result.data[0])
        return None
    except Exception as e:
        logger.error(f"Ошибка создания пользователя {user_id}: {e}")
        return None


async def update_user_resources(user_id: int, **resources):
    """Обновление ресурсов пользователя"""
    try:
        # Получаем текущие данные пользователя
        user = await get_user(user_id)
        if not user:
            return False

        # Подготавливаем обновления
        updates = {"last_active": datetime.now().isoformat()}

        for resource, amount in resources.items():
            if hasattr(user, resource):
                current_value = getattr(user, resource)
                updates[resource] = current_value + amount

        result = await supabase_manager.execute_query(
            table="users",
            operation="update",
            data=updates,
            filters={"user_id": user_id}
        )

        return result.data is not None
    except Exception as e:
        logger.error(f"Ошибка обновления ресурсов пользователя {user_id}: {e}")
        return False


# === ACADEMY FUNCTIONS ===

async def get_hired_workers_count(user_id: int) -> dict:
    """Получение количества нанятых рабочих"""
    try:
        result = await supabase_manager.execute_query(
            table="hired_workers",
            operation="select",
            select="worker_type, count(*)",
            filters={"user_id": user_id}
        )

        # Здесь нужно будет использовать RPC функцию для GROUP BY
        # Пока возвращаем общее количество
        if result.data:
            return {"laborer": len([w for w in result.data if w.get("status") != "consumed"])}
        return {"laborer": 0}
    except Exception as e:
        logger.error(f"Ошибка получения рабочих {user_id}: {e}")
        return {}


async def hire_worker(user_id: int) -> tuple[bool, str]:
    """Найм рабочего через Supabase"""
    try:
        # Проверяем возможность найма
        can_hire, reason, remaining = await can_hire_worker(user_id)
        if not can_hire:
            return False, f"Не можете нанять: {reason}"

        # Проверяем баланс
        user = await get_user(user_id)
        if not user:
            return False, "Пользователь не найден"

        workers_count = await get_hired_workers_count(user_id)
        total_workers = sum(workers_count.values())
        hire_cost = 30 + (5 * total_workers)

        if user.ryabucks < hire_cost:
            return False, f"Недостаточно рябаксов! Нужно: {hire_cost}💵"

        # Нанимаем рабочего
        worker_data = {
            "user_id": user_id,
            "worker_type": "laborer",
            "status": "idle",
            "hired_at": datetime.now().isoformat(),
            "next_available_at": (datetime.now() + timedelta(hours=24)).isoformat()
        }

        result = await supabase_manager.execute_query(
            table="hired_workers",
            operation="insert",
            data=worker_data
        )

        if result.data:
            # Списываем деньги
            await update_user_resources(user_id, ryabucks=-hire_cost)
            return True, f"Рабочий нанят! Потрачено: {hire_cost}💵"

        return False, "Ошибка найма рабочего"
    except Exception as e:
        logger.error(f"Ошибка найма рабочего {user_id}: {e}")
        return False, "Произошла ошибка при найме"


# === ISLAND STATS ===

async def get_island_stats() -> dict:
    """Получение статистики острова"""
    try:
        # Общее количество игроков
        total_result = await supabase_manager.execute_query(
            table="users",
            operation="select",
            select="count(*)"
        )

        # Активные игроки сегодня (нужна RPC функция)
        active_result = await supabase_manager.execute_query(
            table="users",
            operation="select",
            select="count(*)"
            # Здесь нужен фильтр по дате
        )

        return {
            'total_players': len(total_result.data) if total_result.data else 42,
            'online_players': 12,  # Заглушка
            'daily_rbtc': 15.67,  # Заглушка
            'active_expeditions': 8  # Заглушка
        }
    except Exception as e:
        logger.error(f"Ошибка получения статистики: {e}")
        return {
            'total_players': 42,
            'online_players': 12,
            'daily_rbtc': 15.67,
            'active_expeditions': 8
        }


# Функция инициализации
async def initialize_supabase():
    """Инициализация Supabase клиента"""
    supabase_manager.initialize()
    logger.info("✅ Supabase модели инициализированы")
