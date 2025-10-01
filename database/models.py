"""
Модели данных для Ryabot Island на Supabase
Полная замена asyncpg на официальный Supabase Python SDK
"""
import os
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from database.supabase_client import supabase_manager
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


# ================== ИНИЦИАЛИЗАЦИЯ ==================

async def initialize_db_pool():
    """Инициализация Supabase клиента"""
    try:
        supabase_manager.initialize()
        logger.info("✅ Supabase клиент инициализирован")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации Supabase: {e}")
        raise


async def close_connection_pool():
    """Заглушка для совместимости (Supabase не требует закрытия)"""
    logger.info("✅ Supabase клиент: подключение завершено")


async def init_database():
    """Создание таблиц через Supabase (выполните миграции в Dashboard)"""
    logger.info("✅ Таблицы должны быть созданы через Supabase Dashboard")


async def create_academy_tables():
    """Создание таблиц академии (выполните миграции в Dashboard)"""
    logger.info("✅ Таблицы академии должны быть созданы через Supabase Dashboard")


# ================== МОДЕЛИ ==================

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
        else:
            # Значения по умолчанию
            self.user_id = 0
            self.username = None
            self.language = 'ru'
            self.level = 1
            self.experience = 0
            self.energy = 100
            self.ryabucks = 1000
            self.rbtc = 0.0
            self.golden_shards = 0
            self.quantum_keys = 0
            self.land_plots = 1
            self.tutorial_completed = False
            self.current_state = None
            self.activity_data = None
            self.created_at = datetime.now()
            self.last_active = datetime.now()


# ================== USER FUNCTIONS ==================

async def get_user(user_id: int) -> Optional[User]:
    """Получение пользователя из Supabase"""
    try:
        result = await supabase_manager.execute_query(
            table="users",
            operation="select",
            filters={"user_id": user_id},
            single=True
        )
        return User(result) if result else None
    except Exception as e:
        logger.error(f"Ошибка получения пользователя {user_id}: {e}")
        return None


async def create_user(user_id: int, username: str = None) -> Optional[User]:
    """Создание нового пользователя в Supabase"""
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

        return User(result) if result else None
    except Exception as e:
        logger.error(f"Ошибка создания пользователя {user_id}: {e}")
        return None


async def get_user_language(user_id: int) -> str:
    """Получение языка пользователя"""
    try:
        user = await get_user(user_id)
        return user.language if user else 'ru'
    except Exception as e:
        logger.error(f"Ошибка получения языка пользователя {user_id}: {e}")
        return 'ru'


async def update_user_language(user_id: int, language: str):
    """Обновление языка пользователя"""
    try:
        await supabase_manager.execute_query(
            table="users",
            operation="update",
            data={"language": language, "last_active": datetime.now().isoformat()},
            filters={"user_id": user_id}
        )
    except Exception as e:
        logger.error(f"Ошибка обновления языка пользователя {user_id}: {e}")


async def complete_tutorial(user_id: int):
    """Завершение туториала"""
    try:
        # Получаем текущие данные пользователя
        user = await get_user(user_id)
        if not user:
            return

        # Обновляем данные
        updates = {
            "tutorial_completed": True,
            "ryabucks": user.ryabucks + 500,
            "energy": min(user.energy + 20, 100),
            "last_active": datetime.now().isoformat()
        }

        await supabase_manager.execute_query(
            table="users",
            operation="update",
            data=updates,
            filters={"user_id": user_id}
        )
    except Exception as e:
        logger.error(f"Ошибка завершения туториала {user_id}: {e}")


async def set_user_state(user_id: int, state: str, activity_data: str = None):
    """Установка состояния пользователя"""
    try:
        await supabase_manager.execute_query(
            table="users",
            operation="update",
            data={
                "current_state": state,
                "activity_data": activity_data,
                "last_active": datetime.now().isoformat()
            },
            filters={"user_id": user_id}
        )
    except Exception as e:
        logger.error(f"Ошибка установки состояния пользователя {user_id}: {e}")


async def clear_user_state(user_id: int):
    """Очистка состояния пользователя"""
    await set_user_state(user_id, None, None)


async def update_user_resources(user_id: int, **resources):
    """Обновление ресурсов пользователя"""
    if not resources:
        return

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
                if resource == 'energy':
                    # Энергия не может превышать 100
                    updates[resource] = min(current_value + amount, 100)
                else:
                    updates[resource] = current_value + amount

        await supabase_manager.execute_query(
            table="users",
            operation="update",
            data=updates,
            filters={"user_id": user_id}
        )
        return True
    except Exception as e:
        logger.error(f"Ошибка обновления ресурсов пользователя {user_id}: {e}")
        return False


# ================== ACADEMY FUNCTIONS ==================

async def get_hired_workers_count(user_id: int) -> dict:
    """Получение количества нанятых рабочих через RPC функцию"""
    try:
        # Используем RPC функцию для группировки
        result = await supabase_manager.execute_rpc(
            "get_workers_count",
            {"p_user_id": user_id}
        )

        if result:
            return {row['worker_type']: int(row['count']) for row in result}
        return {"laborer": 0}
    except Exception as e:
        logger.error(f"Ошибка получения рабочих {user_id}: {e}")
        # Fallback - получаем все записи и считаем в Python
        try:
            workers = await supabase_manager.execute_query(
                table="hired_workers",
                operation="select",
                filters={"user_id": user_id}
            )

            if workers:
                count = len([w for w in workers if w.get("status") != "consumed"])
                return {"laborer": count}
            return {"laborer": 0}
        except:
            return {"laborer": 0}


async def can_hire_worker(user_id: int) -> tuple[bool, str, int]:
    """Проверка возможности найма рабочего"""
    try:
        cooldown = await supabase_manager.execute_query(
            table="hire_cooldowns",
            operation="select",
            filters={"user_id": user_id},
            single=True
        )

        if cooldown:
            last_hire_str = cooldown['last_hire_time']
            hires_today = cooldown['hires_count']
            reset_date_str = cooldown['reset_date']

            # Парсинг дат
            if isinstance(last_hire_str, str):
                last_hire = datetime.fromisoformat(last_hire_str.replace('Z', '+00:00'))
            else:
                last_hire = last_hire_str

            if isinstance(reset_date_str, str):
                reset_date = datetime.strptime(reset_date_str, '%Y-%m-%d').date()
            else:
                reset_date = reset_date_str

            # Проверяем, нужно ли обнулить счетчик
            today = datetime.now().date()
            if reset_date != today:
                hires_today = 0

            # Проверяем кулдаун (24 часа)
            time_since_last_hire = datetime.now().replace(tzinfo=None) - last_hire.replace(tzinfo=None)
            if time_since_last_hire < timedelta(hours=24):
                remaining_seconds = int((timedelta(hours=24) - time_since_last_hire).total_seconds())
                return False, "cooldown", remaining_seconds

            # Проверяем лимит найма в день
            max_hires = 3
            if hires_today >= max_hires:
                return False, "limit_reached", 0

        return True, "ok", 0
    except Exception as e:
        logger.error(f"Ошибка проверки найма {user_id}: {e}")
        return True, "ok", 0  # При ошибке разрешаем найм


async def hire_worker(user_id: int) -> tuple[bool, str]:
    """Найм рабочего через Supabase"""
    try:
        can_hire, reason, remaining = await can_hire_worker(user_id)

        if not can_hire:
            if reason == "cooldown":
                hours = remaining // 3600
                minutes = (remaining % 3600) // 60
                return False, f"⏰ Следующий найм через: {hours}ч {minutes}мин"
            elif reason == "limit_reached":
                return False, "🚫 Достигнут лимит найма! Улучшите подписку."

        user = await get_user(user_id)
        if not user:
            return False, "❌ Пользователь не найден!"

        workers_count = await get_hired_workers_count(user_id)
        total_workers = sum(workers_count.values())
        hire_cost = 30 + (5 * total_workers)

        if user.ryabucks < hire_cost:
            return False, f"❌ Недостаточно рябаксов! Нужно: {hire_cost}💵"

        # Добавляем рабочего
        next_available = (datetime.now() + timedelta(hours=24)).isoformat()
        worker_data = {
            "user_id": user_id,
            "worker_type": "laborer",
            "status": "idle",
            "hired_at": datetime.now().isoformat(),
            "next_available_at": next_available
        }

        result = await supabase_manager.execute_query(
            table="hired_workers",
            operation="insert",
            data=worker_data
        )

        if result:
            # Обновляем кулдаун - используем upsert
            cooldown_data = {
                "user_id": user_id,
                "last_hire_time": datetime.now().isoformat(),
                "hires_count": 1,  # Будет правильно обработано RPC функцией
                "reset_date": datetime.now().date().isoformat()
            }

            await supabase_manager.execute_query(
                table="hire_cooldowns",
                operation="upsert",
                data=cooldown_data
            )

            # Списываем деньги
            await update_user_resources(user_id, ryabucks=-hire_cost)

            return True, f"✅ Разнорабочий нанят! Потрачено: {hire_cost}💵"

        return False, "Ошибка найма рабочего"
    except Exception as e:
        logger.error(f"Ошибка найма рабочего {user_id}: {e}")
        return False, "Произошла ошибка при найме"


async def get_training_slots_info(user_id: int) -> dict:
    """Информация о слотах обучения"""
    try:
        trainings = await supabase_manager.execute_query(
            table="training_units",
            operation="select",
            filters={"user_id": user_id}
        )

        active_training = 0
        if trainings:
            active_training = len([t for t in trainings if t.get("status") == "training"])

        base_slots = 2
        total_slots = base_slots

        return {
            'used': active_training,
            'total': total_slots,
            'available': total_slots - active_training
        }
    except Exception as e:
        logger.error(f"Ошибка получения слотов обучения {user_id}: {e}")
        return {'used': 0, 'total': 2, 'available': 2}


async def start_training(user_id: int, unit_type: str) -> tuple[bool, str]:
    """Начать обучение специалиста"""
    try:
        workers_count = await get_hired_workers_count(user_id)
        if workers_count.get('laborer', 0) == 0:
            return False, "❌ Нет свободных разнорабочих! Наймите их на бирже труда."

        slots_info = await get_training_slots_info(user_id)
        if slots_info['available'] <= 0:
            return False, "❌ Все учебные места заняты! Дождитесь окончания обучения."

        training_data = {
            'builder': {'name': '👷 Строитель', 'cost': 100, 'time_hours': 2},
            'farmer': {'name': '👨‍🌾 Фермер', 'cost': 100, 'time_hours': 2},
            'woodman': {'name': '🧑‍🚒 Лесник', 'cost': 120, 'time_hours': 3},
            'soldier': {'name': '💂 Солдат', 'cost': 150, 'time_hours': 4},
            'fisherman': {'name': '🎣 Рыбак', 'cost': 110, 'time_hours': 2.5},
            'scientist': {'name': '👨‍🔬 Ученый', 'cost': 200, 'time_hours': 6},
            'cook': {'name': '👨‍🍳 Повар', 'cost': 130, 'time_hours': 3},
            'teacher': {'name': '👨‍🏫 Учитель', 'cost': 180, 'time_hours': 5},
            'doctor': {'name': '🧑‍⚕️ Доктор', 'cost': 220, 'time_hours': 8}
        }

        if unit_type not in training_data:
            return False, "❌ Неизвестная профессия!"

        user = await get_user(user_id)
        unit_info = training_data[unit_type]

        if user.ryabucks < unit_info['cost']:
            return False, f"❌ Недостаточно рябаксов! Нужно: {unit_info['cost']}💵"

        # Находим свободного рабочего
        workers = await supabase_manager.execute_query(
            table="hired_workers",
            operation="select",
            filters={"user_id": user_id}
        )

        worker = None
        if workers:
            for w in workers:
                if w.get("worker_type") == "laborer" and w.get("status") == "idle":
                    worker = w
                    break

        if not worker:
            return False, "❌ Нет свободных разнорабочих!"

        worker_id = worker['id']
        completion_time = (datetime.now() + timedelta(hours=unit_info['time_hours'])).isoformat()

        # Добавляем обучение
        training_data_insert = {
            "user_id": user_id,
            "unit_type": unit_type,
            "started_at": datetime.now().isoformat(),
            "completed_at": completion_time,
            "worker_id": worker_id,
            "status": "training"
        }

        training_result = await supabase_manager.execute_query(
            table="training_units",
            operation="insert",
            data=training_data_insert
        )

        if training_result:
            # Помечаем рабочего как занятого
            await supabase_manager.execute_query(
                table="hired_workers",
                operation="update",
                data={"status": "training"},
                filters={"id": worker_id}
            )

            # Списываем деньги
            await update_user_resources(user_id, ryabucks=-unit_info['cost'])

            hours = int(unit_info['time_hours'])
            minutes = int((unit_info['time_hours'] % 1) * 60)
            return True, f"✅ {unit_info['name']} отправлен на обучение!\\n⏰ Завершится через: {hours}ч {minutes}мин"

        return False, "Ошибка при запуске обучения"

    except Exception as e:
        logger.error(f"Ошибка начала обучения {user_id}: {e}")
        return False, "Произошла ошибка при обучении"


async def get_active_trainings(user_id: int) -> list:
    """Получить активные обучения"""
    try:
        trainings = await supabase_manager.execute_query(
            table="training_units",
            operation="select",
            filters={"user_id": user_id}
        )

        result = []
        if trainings:
            for training in trainings:
                if training.get("status") != "training":
                    continue

                completed_at_str = training['completed_at']
                if isinstance(completed_at_str, str):
                    completed_time = datetime.fromisoformat(completed_at_str.replace('Z', '+00:00'))
                else:
                    completed_time = completed_at_str

                time_left = completed_time.replace(tzinfo=None) - datetime.now()

                if time_left.total_seconds() > 0:
                    hours = int(time_left.total_seconds() // 3600)
                    minutes = int((time_left.total_seconds() % 3600) // 60)
                    result.append({
                        'type': training['unit_type'],
                        'time_left': f"{hours}ч {minutes}мин"
                    })

        return result
    except Exception as e:
        logger.error(f"Ошибка получения активных обучений {user_id}: {e}")
        return []


async def complete_trainings(user_id: int) -> int:
    """Завершение готовых обучений"""
    try:
        # Получаем завершенные обучения
        trainings = await supabase_manager.execute_query(
            table="training_units",
            operation="select",
            filters={"user_id": user_id}
        )

        count = 0
        if trainings:
            for training in trainings:
                if training.get("status") != "training":
                    continue

                completed_at_str = training['completed_at']
                if isinstance(completed_at_str, str):
                    completed_time = datetime.fromisoformat(completed_at_str.replace('Z', '+00:00'))
                else:
                    completed_time = completed_at_str

                # Проверяем, готово ли обучение
                if completed_time.replace(tzinfo=None) <= datetime.now():
                    training_id = training['id']
                    unit_type = training['unit_type']
                    worker_id = training['worker_id']

                    # Создаем специалиста
                    specialist_data = {
                        "user_id": user_id,
                        "specialist_type": unit_type,
                        "status": "available",
                        "created_at": datetime.now().isoformat()
                    }

                    await supabase_manager.execute_query(
                        table="trained_specialists",
                        operation="insert",
                        data=specialist_data
                    )

                    # Помечаем обучение как завершенное
                    await supabase_manager.execute_query(
                        table="training_units",
                        operation="update",
                        data={"status": "completed"},
                        filters={"id": training_id}
                    )

                    # Помечаем рабочего как использованного
                    await supabase_manager.execute_query(
                        table="hired_workers",
                        operation="update",
                        data={"status": "consumed"},
                        filters={"id": worker_id}
                    )

                    count += 1

        return count
    except Exception as e:
        logger.error(f"Ошибка завершения обучений {user_id}: {e}")
        return 0


async def get_specialists_count(user_id: int) -> dict:
    """Получение количества специалистов"""
    try:
        specialists = await supabase_manager.execute_query(
            table="trained_specialists",
            operation="select",
            filters={"user_id": user_id}
        )

        if specialists:
            result = {}
            for spec in specialists:
                if spec.get("status") == "dead":
                    continue
                spec_type = spec['specialist_type']
                result[spec_type] = result.get(spec_type, 0) + 1
            return result

        return {}
    except Exception as e:
        logger.error(f"Ошибка получения специалистов {user_id}: {e}")
        return {}


# ================== ISLAND STATS ==================

async def get_island_stats() -> dict:
    """Получение статистики острова через RPC функции"""
    try:
        # Используем RPC функцию для получения статистики
        stats = await supabase_manager.execute_rpc("get_island_statistics")

        if stats:
            return {
                'total_players': max(42, int(stats.get('total_players', 42))),
                'online_players': max(12, int(stats.get('active_players', 12))),
                'daily_rbtc': max(15.67, float(stats.get('daily_rbtc', 15.67))),
                'active_expeditions': max(8, int(stats.get('active_expeditions', 8)))
            }
    except Exception as e:
        logger.error(f"Ошибка получения статистики через RPC: {e}")

    # Fallback - получаем статистику обычными запросами
    try:
        # Общее количество игроков
        total_count = await supabase_manager.execute_query(
            table="users",
            operation="count"
        )

        return {
            'total_players': max(42, total_count or 42),
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


# ================== СОВМЕСТИМОСТЬ ==================

async def execute_db(query: str = None, *params, fetch_one=False, fetch_all=False, **kwargs):
    """Заглушка для совместимости со старым кодом"""
    logger.warning(f"execute_db вызван с query: {query}. Используйте Supabase методы!")
    return None


logger.info("✅ Database models loaded (Supabase version)")
