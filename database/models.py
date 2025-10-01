"""
Модели базы данных для Ryabot Island (только PostgreSQL/Supabase)
"""
import os
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, List

import asyncpg
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ================== POSTGRESQL CONNECTION POOL ==================

async def close_all(self):
    if self.pool:
        await self.pool.close()
        logger.info("✅ PostgreSQL connection pool closed")

    async def initialize(self):
        # IPv4 Fix: принудительно резолвим хост в IPv4
        import socket
        original_host = os.getenv("POSTGRES_HOST")
        user = os.getenv("POSTGRES_USER")
        password = os.getenv("POSTGRES_PASSWORD")
        database = os.getenv("POSTGRES_DB", "postgres")
        port = int(os.getenv("POSTGRES_PORT", 5432))

        # DNS резолюция в IPv4
        try:
            ipv4_host = socket.gethostbyname(original_host)
            logger.info(f"✅ Resolved {original_host} to IPv4: {ipv4_host}")
            use_host = ipv4_host
        except Exception as e:
            logger.error(f"❌ Failed to resolve {original_host}: {e}")
            use_host = original_host  # Fallback

        logger.info(f"🔌 Подключение к PostgreSQL: {use_host}:{port}")

        try:
            self.pool = await asyncpg.create_pool(
                host=use_host,
                user=user,
                password=password,
                database=database,
                port=port,
                ssl='require',  # SSL обязателен для Supabase
                min_size=1,
                max_size=5,
                command_timeout=60,
                timeout=15
            )
            logger.info("✅ PostgreSQL pool created!")

        except Exception as e:
            logger.error(f"❌ Pool creation failed: {type(e).__name__}: {e}")
            raise

    async def close_all(self):
        """Добавь этот метод!"""
        if self.pool:
            await self.pool.close()
            logger.info("✅ PostgreSQL connection pool closed")


# ================== POSTGRESQL CONNECTION POOL ==================

class PostgresConnectionPool:
    def __init__(self):
        self.pool = None

    async def initialize(self):
        # IPv4 Fix: принудительно резолвим хост в IPv4
        import socket
        original_host = os.getenv("POSTGRES_HOST")
        user = os.getenv("POSTGRES_USER")
        password = os.getenv("POSTGRES_PASSWORD")
        database = os.getenv("POSTGRES_DB", "postgres")
        port = int(os.getenv("POSTGRES_PORT", 5432))

        # DNS резолюция в IPv4
        try:
            ipv4_host = socket.gethostbyname(original_host)
            logger.info(f"✅ Resolved {original_host} to IPv4: {ipv4_host}")
            use_host = ipv4_host
        except Exception as e:
            logger.error(f"❌ Failed to resolve {original_host}: {e}")
            use_host = original_host  # Fallback

        logger.info(f"🔌 Подключение к PostgreSQL: {use_host}:{port}")

        try:
            self.pool = await asyncpg.create_pool(
                host=use_host,
                user=user,
                password=password,
                database=database,
                port=port,
                ssl='require',  # SSL обязателен для Supabase
                min_size=1,
                max_size=5,
                command_timeout=60,
                timeout=15
            )
            logger.info("✅ PostgreSQL pool created!")

        except Exception as e:
            logger.error(f"❌ Pool creation failed: {type(e).__name__}: {e}")
            raise

    async def acquire(self):
        return await self.pool.acquire()

    async def release(self, conn):
        await self.pool.release(conn)

    async def close_all(self):
        if self.pool:
            await self.pool.close()
            logger.info("✅ PostgreSQL connection pool closed")


# Глобальный пул (ПОСЛЕ объявления класса!)
connection_pool = PostgresConnectionPool()


# ================== UTILITY FUNCTIONS ==================

async def execute_db(query: str, *params, fetch_one=False, fetch_all=False):
    """Выполнение SQL запросов к PostgreSQL"""
    conn = await connection_pool.acquire()
    try:
        if fetch_one:
            result = await conn.fetchrow(query, *params)
            return dict(result) if result else None
        elif fetch_all:
            results = await conn.fetch(query, *params)
            return [dict(row) for row in results] if results else []
        else:
            return await conn.execute(query, *params)
    except Exception as e:
        logger.error(f"Database error: {e} | Query: {query} | Params: {params}", exc_info=True)
        return None
    finally:
        await connection_pool.release(conn)

# ================== INITIALIZATION ==================

async def initialize_db_pool():
    """Инициализация пула соединений"""
    await connection_pool.initialize()

async def close_connection_pool():
    """Закрытие пула соединений"""
    await connection_pool.close_all()

async def init_database():
    """Создание таблиц в PostgreSQL"""
    queries = [
        """CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            username TEXT,
            language TEXT DEFAULT 'ru',
            level INTEGER DEFAULT 1,
            experience INTEGER DEFAULT 0,
            energy INTEGER DEFAULT 100,
            ryabucks INTEGER DEFAULT 1000,
            rbtc NUMERIC(10,2) DEFAULT 0.0,
            golden_shards INTEGER DEFAULT 0,
            quantum_keys INTEGER DEFAULT 0,
            land_plots INTEGER DEFAULT 1,
            tutorial_completed BOOLEAN DEFAULT FALSE,
            current_state TEXT,
            activity_data TEXT,
            created_at TIMESTAMP DEFAULT NOW(),
            last_active TIMESTAMP DEFAULT NOW()
        )""",

        """CREATE TABLE IF NOT EXISTS farm_buildings (
            id SERIAL PRIMARY KEY,
            user_id BIGINT REFERENCES users(user_id),
            building_type TEXT NOT NULL,
            level INTEGER DEFAULT 1,
            is_active BOOLEAN DEFAULT TRUE,
            last_collected TIMESTAMP,
            next_collection TIMESTAMP,
            plot_id INTEGER,
            created_at TIMESTAMP DEFAULT NOW()
        )""",

        """CREATE TABLE IF NOT EXISTS expeditions (
            id SERIAL PRIMARY KEY,
            user_id BIGINT REFERENCES users(user_id),
            zone_id INTEGER,
            status TEXT DEFAULT 'active',
            rbtc_found NUMERIC(10,2) DEFAULT 0.0,
            started_at TIMESTAMP DEFAULT NOW(),
            completed_at TIMESTAMP
        )""",

        """CREATE TABLE IF NOT EXISTS island_stats (
                                                       id SERIAL PRIMARY KEY,
                                                       date DATE UNIQUE DEFAULT CURRENT_DATE,
                                                       total_players INTEGER DEFAULT 0,
                                                       active_players INTEGER DEFAULT 0,
                                                       daily_rbtc NUMERIC(10,2) DEFAULT 0.0,
            active_expeditions INTEGER DEFAULT 0,
            updated_at TIMESTAMP DEFAULT NOW()
        )""",

        # Индексы
        "CREATE INDEX IF NOT EXISTS idx_users_id ON users(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_users_last_active ON users(last_active)",
        "CREATE INDEX IF NOT EXISTS idx_farm_buildings_userid ON farm_buildings(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_expeditions_userid ON expeditions(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_expeditions_status ON expeditions(status)"
    ]

    for query in queries:
        await execute_db(query)

    logger.info("✅ Database tables created")

# ================== MODELS ==================

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
    """Получение пользователя"""
    result = await execute_db(
        "SELECT * FROM users WHERE user_id = $1", user_id, fetch_one=True
    )
    return User(result) if result else None

async def create_user(user_id: int, username: str = None) -> User:
    """Создание пользователя"""
    await execute_db("""
        INSERT INTO users (user_id, username, created_at, last_active) 
        VALUES ($1, $2, NOW(), NOW())
    """, user_id, username)

    return await get_user(user_id)

async def get_user_language(user_id: int) -> str:
    """Получение языка пользователя"""
    user = await get_user(user_id)
    return user.language if user else 'ru'

async def update_user_language(user_id: int, language: str):
    """Обновление языка"""
    await execute_db(
        "UPDATE users SET language = $1, last_active = NOW() WHERE user_id = $2",
        language, user_id
    )

async def complete_tutorial(user_id: int):
    """Завершение туториала"""
    await execute_db("""
        UPDATE users SET 
            tutorial_completed = TRUE,
            ryabucks = ryabucks + 500,
            energy = energy + 20,
            last_active = NOW()
        WHERE user_id = $1
    """, user_id)

async def set_user_state(user_id: int, state: str, activity_data: str = None):
    """Установка состояния пользователя"""
    await execute_db("""
        UPDATE users SET 
            current_state = $1,
            activity_data = $2,
            last_active = NOW()
        WHERE user_id = $3
    """, state, activity_data, user_id)

async def clear_user_state(user_id: int):
    """Очистка состояния пользователя"""
    await set_user_state(user_id, None, None)

async def update_user_resources(user_id: int, **resources):
    """Обновление ресурсов пользователя"""
    if not resources:
        return

    set_clause = ", ".join([f"{key} = {key} + ${i+1}" for i, key in enumerate(resources.keys())])
    params = list(resources.values()) + [user_id]

    await execute_db(
        f"UPDATE users SET {set_clause}, last_active = NOW() WHERE user_id = ${len(params)}",
        *params
    )

# ================== ACADEMY FUNCTIONS ==================

async def create_academy_tables():
    """Создание таблиц академии"""
    queries = [
        """CREATE TABLE IF NOT EXISTS hired_workers (
            id SERIAL PRIMARY KEY,
            user_id BIGINT REFERENCES users(user_id),
            worker_type TEXT DEFAULT 'laborer',
            status TEXT DEFAULT 'idle',
            hired_at TIMESTAMP DEFAULT NOW(),
            next_available_at TIMESTAMP
        )""",

        """CREATE TABLE IF NOT EXISTS training_units (
            id SERIAL PRIMARY KEY,
            user_id BIGINT REFERENCES users(user_id),
            unit_type TEXT NOT NULL,
            status TEXT DEFAULT 'training',
            started_at TIMESTAMP DEFAULT NOW(),
            completed_at TIMESTAMP,
            worker_id INTEGER REFERENCES hired_workers(id)
        )""",

        """CREATE TABLE IF NOT EXISTS trained_specialists (
            id SERIAL PRIMARY KEY,
            user_id BIGINT REFERENCES users(user_id),
            specialist_type TEXT NOT NULL,
            level INTEGER DEFAULT 1,
            status TEXT DEFAULT 'available',
            created_at TIMESTAMP DEFAULT NOW(),
            last_worked TIMESTAMP
        )""",

        """CREATE TABLE IF NOT EXISTS hire_cooldowns (
            id SERIAL PRIMARY KEY,
            user_id BIGINT REFERENCES users(user_id) UNIQUE,
            last_hire_time TIMESTAMP DEFAULT NOW(),
            hires_count INTEGER DEFAULT 0,
            reset_date DATE DEFAULT CURRENT_DATE
        )""",

        # Индексы
        "CREATE INDEX IF NOT EXISTS idx_hired_userid ON hired_workers(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_hired_status ON hired_workers(status)",
        "CREATE INDEX IF NOT EXISTS idx_trainings_userid ON training_units(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_trainings_status ON training_units(status)",
        "CREATE INDEX IF NOT EXISTS idx_specialists_userid ON trained_specialists(user_id)"
    ]

    for query in queries:
        await execute_db(query)

    logger.info("✅ Academy tables created")

async def get_hired_workers_count(user_id: int) -> dict:
    """Получение количества нанятых рабочих"""
    results = await execute_db("""
        SELECT worker_type, COUNT(*) as count
        FROM hired_workers
        WHERE user_id = $1 AND status != 'consumed'
        GROUP BY worker_type
    """, user_id, fetch_all=True)

    return {row['worker_type']: row['count'] for row in results} if results else {}

async def can_hire_worker(user_id: int) -> tuple[bool, str, int]:
    """Проверка возможности найма рабочего"""
    cooldown = await execute_db("""
        SELECT last_hire_time, hires_count, reset_date
        FROM hire_cooldowns
        WHERE user_id = $1
    """, user_id, fetch_one=True)

    if cooldown:
        last_hire = cooldown['last_hire_time']
        hires_today = cooldown['hires_count']
        reset_date = cooldown['reset_date']

        # Проверяем, нужно ли обнулить счетчик
        today = datetime.now().date()
        if reset_date != today:
            hires_today = 0

        # Проверяем кулдаун (24 часа)
        time_since_last_hire = datetime.now() - last_hire
        if time_since_last_hire < timedelta(hours=24):
            remaining_seconds = int((timedelta(hours=24) - time_since_last_hire).total_seconds())
            return False, "cooldown", remaining_seconds

        # Проверяем лимит найма в день
        max_hires = 3
        if hires_today >= max_hires:
            return False, "limit_reached", 0

    return True, "ok", 0

async def hire_worker(user_id: int) -> tuple[bool, str]:
    """Найм рабочего"""
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
    next_available = datetime.now() + timedelta(hours=24)
    await execute_db("""
        INSERT INTO hired_workers (user_id, worker_type, status, next_available_at)
        VALUES ($1, 'laborer', 'idle', $2)
    """, user_id, next_available)

    # Обновляем кулдаун
    await execute_db("""
        INSERT INTO hire_cooldowns (user_id, last_hire_time, hires_count, reset_date)
        VALUES ($1, NOW(), 1, CURRENT_DATE)
        ON CONFLICT (user_id) DO UPDATE SET
            last_hire_time = EXCLUDED.last_hire_time,
            hires_count = CASE
                WHEN hire_cooldowns.reset_date = CURRENT_DATE THEN hire_cooldowns.hires_count + 1
                ELSE 1
            END,
            reset_date = CURRENT_DATE
    """, user_id)

    # Списываем деньги
    await execute_db("""
        UPDATE users SET ryabucks = ryabucks - $1 WHERE user_id = $2
    """, hire_cost, user_id)

    return True, f"✅ Разнорабочий нанят! Потрачено: {hire_cost}💵"

async def get_training_slots_info(user_id: int) -> dict:
    """Информация о слотах обучения"""
    result = await execute_db("""
        SELECT COUNT(*) as count FROM training_units
        WHERE user_id = $1 AND status = 'training'
    """, user_id, fetch_one=True)

    active_training = result['count'] if result else 0
    base_slots = 2
    total_slots = base_slots

    return {
        'used': active_training,
        'total': total_slots,
        'available': total_slots - active_training
    }

async def start_training(user_id: int, unit_type: str) -> tuple[bool, str]:
    """Начать обучение специалиста"""
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
    worker = await execute_db("""
        SELECT id FROM hired_workers
        WHERE user_id = $1 AND worker_type = 'laborer' AND status = 'idle'
        LIMIT 1
    """, user_id, fetch_one=True)

    if not worker:
        return False, "❌ Нет свободных разнорабочих!"

    worker_id = worker['id']
    completion_time = datetime.now() + timedelta(hours=unit_info['time_hours'])

    # Добавляем обучение
    await execute_db("""
        INSERT INTO training_units (user_id, unit_type, started_at, completed_at, worker_id)
        VALUES ($1, $2, NOW(), $3, $4)
    """, user_id, unit_type, completion_time, worker_id)

    # Помечаем рабочего как занятого
    await execute_db("""
        UPDATE hired_workers SET status = 'training' WHERE id = $1
    """, worker_id)

    # Списываем деньги
    await execute_db("""
        UPDATE users SET ryabucks = ryabucks - $1 WHERE user_id = $2
    """, unit_info['cost'], user_id)

    hours = int(unit_info['time_hours'])
    minutes = int((unit_info['time_hours'] % 1) * 60)
    return True, f"✅ {unit_info['name']} отправлен на обучение!\n⏰ Завершится через: {hours}ч {minutes}мин"

async def get_active_trainings(user_id: int) -> list:
    """Получить активные обучения"""
    trainings = await execute_db("""
        SELECT unit_type, started_at, completed_at
        FROM training_units
        WHERE user_id = $1 AND status = 'training'
        ORDER BY completed_at ASC
    """, user_id, fetch_all=True)

    result = []
    if trainings:
        for training in trainings:
            unit_type = training['unit_type']
            completed_time = training['completed_at']

            time_left = completed_time - datetime.now()

            if time_left.total_seconds() > 0:
                hours = int(time_left.total_seconds() // 3600)
                minutes = int((time_left.total_seconds() % 3600) // 60)
                result.append({
                    'type': unit_type,
                    'time_left': f"{hours}ч {minutes}мин"
                })

    return result

async def complete_trainings(user_id: int) -> int:
    """Завершение готовых обучений"""
    completed = await execute_db("""
        SELECT id, unit_type, worker_id
        FROM training_units
        WHERE user_id = $1 AND status = 'training' AND completed_at <= NOW()
    """, user_id, fetch_all=True)

    count = 0
    if completed:
        for training in completed:
            training_id = training['id']
            unit_type = training['unit_type']
            worker_id = training['worker_id']

            # Создаем специалиста
            await execute_db("""
                INSERT INTO trained_specialists (user_id, specialist_type, status)
                VALUES ($1, $2, 'available')
            """, user_id, unit_type)

            # Помечаем обучение как завершенное
            await execute_db("""
                UPDATE training_units SET status = 'completed' WHERE id = $1
            """, training_id)

            # Помечаем рабочего как использованного
            await execute_db("""
                UPDATE hired_workers SET status = 'consumed' WHERE id = $1
            """, worker_id)

            count += 1

    return count

async def get_specialists_count(user_id: int) -> dict:
    """Получение количества специалистов"""
    results = await execute_db("""
        SELECT specialist_type, COUNT(*) as count
        FROM trained_specialists
        WHERE user_id = $1 AND status != 'dead'
        GROUP BY specialist_type
    """, user_id, fetch_all=True)

    return {row['specialist_type']: row['count'] for row in results} if results else {}

# ================== ISLAND STATS ==================

async def get_island_stats() -> dict:
    """Получение статистики острова"""
    try:
        # Общее количество игроков
        result = await execute_db("SELECT COUNT(*) as count FROM users", fetch_one=True)
        total_players = result['count'] if result else 0

        # Активные игроки (заходили сегодня)
        result = await execute_db("""
            SELECT COUNT(*) as count FROM users 
            WHERE DATE(last_active) = CURRENT_DATE
        """, fetch_one=True)
        active_players = result['count'] if result else 0

        # RBTC найденные сегодня
        result = await execute_db("""
            SELECT COALESCE(SUM(rbtc_found), 0) as total FROM expeditions 
            WHERE DATE(completed_at) = CURRENT_DATE
        """, fetch_one=True)
        daily_rbtc = float(result['total']) if result else 0.0

        # Активные экспедиции
        result = await execute_db("""
            SELECT COUNT(*) as count FROM expeditions 
            WHERE status = 'active'
        """, fetch_one=True)
        active_expeditions = result['count'] if result else 0

        return {
            'total_players': max(42, total_players),
            'online_players': max(12, active_players),
            'daily_rbtc': max(15.67, daily_rbtc),
            'active_expeditions': max(8, active_expeditions)
        }

    except Exception as e:
        logger.error(f"Ошибка получения статистики: {e}")
        return {
            'total_players': 42,
            'online_players': 12,
            'daily_rbtc': 15.67,
            'active_expeditions': 8
        }

logger.info("✅ Database models loaded (PostgreSQL/Supabase only)")
