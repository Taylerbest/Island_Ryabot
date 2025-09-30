"""
Модели базы данных для Ryabot Island (оптимизированная версия)
"""
import aiosqlite
from datetime import datetime
from typing import Optional
import asyncio
import logging

logger = logging.getLogger(__name__)

# Путь к базе данных
DB_PATH = "ryabot_island.db"


# ====== CONNECTION POOL ======

class SQLiteConnectionPool:
    """Пул соединений для ускорения работы с SQLite"""

    def __init__(self, db_path: str, max_connections: int = 30):  # Увеличено до 30
        self.db_path = db_path
        self.max_connections = max_connections
        self._pool = []
        self._lock = asyncio.Lock()

    async def acquire(self):
        """Взять соединение из пула"""
        async with self._lock:
            if self._pool:
                return self._pool.pop()

            conn = await aiosqlite.connect(self.db_path)
            await conn.execute("PRAGMA journal_mode=WAL")
            await conn.execute("PRAGMA synchronous=NORMAL")
            return conn

    async def release(self, conn):
        """Вернуть соединение обратно в пул"""
        async with self._lock:
            if len(self._pool) < self.max_connections:
                self._pool.append(conn)
            else:
                await conn.close()

    async def close_all(self):
        """Закрыть все соединения при выключении бота"""
        async with self._lock:
            for conn in self._pool:
                await conn.close()
            self._pool.clear()


# Создаем глобальный пул
connection_pool = SQLiteConnectionPool(DB_PATH, max_connections=30)


async def execute_db(query: str, params=(), fetch_one=False, fetch_all=False):
    """
    Выполнить запрос через connection pool с обработкой ошибок.
    """
    try:
        conn = await connection_pool.acquire()
        cursor = await conn.execute(query, params)

        if fetch_one:
            result = await cursor.fetchone()
        elif fetch_all:
            result = await cursor.fetchall()
        else:
            result = cursor.lastrowid

        await conn.commit()
        return result
    except Exception as e:
        logger.error(f"Database error: {e} | Query: {query} | Params: {params}", exc_info=True)
        return None
    finally:
        await connection_pool.release(conn)


# ====== МОДЕЛИ ======

class User:
    """Модель пользователя"""

    def __init__(self):
        self.user_id: int = 0
        self.username: Optional[str] = None
        self.language: str = 'ru'
        self.level: int = 1
        self.experience: int = 0
        self.energy: int = 100
        self.ryabucks: int = 1000
        self.rbtc: float = 0.0
        self.golden_shards: int = 0
        self.quantum_keys: int = 0
        self.land_plots: int = 1
        self.tutorial_completed: bool = False
        self.current_state: Optional[str] = None
        self.activity_data: Optional[str] = None
        self.created_at: datetime = datetime.now()
        self.last_active: datetime = datetime.now()


async def init_database():
    """Создает таблицы в базе данных и добавляет индексы"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Проверяем существование таблицы users
        cursor = await db.execute("""
                                  SELECT name
                                  FROM sqlite_master
                                  WHERE type = 'table'
                                    AND name = 'users'
                                  """)
        table_exists = await cursor.fetchone()

        if not table_exists:
            # Создаем новую таблицу с полной структурой
            await db.execute("""
                             CREATE TABLE users
                             (
                                 user_id            INTEGER PRIMARY KEY,
                                 username           TEXT,
                                 language           TEXT      DEFAULT 'ru',
                                 level              INTEGER   DEFAULT 1,
                                 experience         INTEGER   DEFAULT 0,
                                 energy             INTEGER   DEFAULT 100,
                                 ryabucks           INTEGER   DEFAULT 1000,
                                 rbtc               REAL      DEFAULT 0.0,
                                 golden_shards      INTEGER   DEFAULT 0,
                                 quantum_keys       INTEGER   DEFAULT 0,
                                 land_plots         INTEGER   DEFAULT 1,
                                 tutorial_completed BOOLEAN   DEFAULT 0,
                                 current_state      TEXT,
                                 activity_data      TEXT,
                                 created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                 last_active        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                             )
                             """)
        else:
            # Проверяем и добавляем недостающие столбцы
            cursor = await db.execute("PRAGMA table_info(users)")
            columns = await cursor.fetchall()
            column_names = [col[1] for col in columns]

            if 'tutorial_completed' not in column_names:
                await db.execute("ALTER TABLE users ADD COLUMN tutorial_completed BOOLEAN DEFAULT 0")
            if 'current_state' not in column_names:
                await db.execute("ALTER TABLE users ADD COLUMN current_state TEXT")
            if 'activity_data' not in column_names:
                await db.execute("ALTER TABLE users ADD COLUMN activity_data TEXT")
            if 'last_active' not in column_names:
                await db.execute("ALTER TABLE users ADD COLUMN last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP")

        # Таблица построек на ферме
        await db.execute("""
                         CREATE TABLE IF NOT EXISTS farm_buildings
                         (
                             id
                             INTEGER
                             PRIMARY
                             KEY
                             AUTOINCREMENT,
                             user_id
                             INTEGER,
                             building_type
                             TEXT
                             NOT
                             NULL,
                             level
                             INTEGER
                             DEFAULT
                             1,
                             is_active
                             BOOLEAN
                             DEFAULT
                             1,
                             last_collected
                             TIMESTAMP,
                             FOREIGN
                             KEY
                         (
                             user_id
                         ) REFERENCES users
                         (
                             user_id
                         )
                             )
                         """)

        # Таблица экспедиций
        await db.execute("""
                         CREATE TABLE IF NOT EXISTS expeditions
                         (
                             id
                             INTEGER
                             PRIMARY
                             KEY
                             AUTOINCREMENT,
                             user_id
                             INTEGER,
                             zone_id
                             INTEGER,
                             status
                             TEXT
                             DEFAULT
                             'active',
                             rbtc_found
                             REAL
                             DEFAULT
                             0.0,
                             started_at
                             TIMESTAMP
                             DEFAULT
                             CURRENT_TIMESTAMP,
                             completed_at
                             TIMESTAMP,
                             FOREIGN
                             KEY
                         (
                             user_id
                         ) REFERENCES users
                         (
                             user_id
                         )
                             )
                         """)

        # Таблица статистики острова
        await db.execute("""
                         CREATE TABLE IF NOT EXISTS island_stats
                         (
                             id
                             INTEGER
                             PRIMARY
                             KEY
                             AUTOINCREMENT,
                             date
                             TEXT
                             UNIQUE,
                             total_players
                             INTEGER
                             DEFAULT
                             0,
                             active_players
                             INTEGER
                             DEFAULT
                             0,
                             daily_rbtc
                             REAL
                             DEFAULT
                             0.0,
                             active_expeditions
                             INTEGER
                             DEFAULT
                             0,
                             updated_at
                             TIMESTAMP
                             DEFAULT
                             CURRENT_TIMESTAMP
                         )
                         """)

        # ====== ВАЖНО: ДОБАВЛЯЕМ ИНДЕКСЫ ДЛЯ УСКОРЕНИЯ ======
        await db.execute("CREATE INDEX IF NOT EXISTS idx_users_id ON users(user_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_expeditions_userid ON expeditions(user_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_expeditions_status ON expeditions(status)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_farm_buildings_userid ON farm_buildings(user_id)")

        await db.commit()


async def get_user(user_id: int) -> Optional[User]:
    """Получает пользователя из БД"""
    row = await execute_db(
        "SELECT * FROM users WHERE user_id = ?", (user_id,), fetch_one=True
    )

    if row:
        user = User()
        try:
            user.user_id = row[0]
            user.username = row[1] if len(row) > 1 else None
            user.language = row[2] if len(row) > 2 else 'ru'
            user.level = row[3] if len(row) > 3 else 1
            user.experience = row[4] if len(row) > 4 else 0
            user.energy = row[5] if len(row) > 5 else 100
            user.ryabucks = row[6] if len(row) > 6 else 1000
            user.rbtc = row[7] if len(row) > 7 else 0.0
            user.golden_shards = row[8] if len(row) > 8 else 0
            user.quantum_keys = row[9] if len(row) > 9 else 0
            user.land_plots = row[10] if len(row) > 10 else 1
            user.tutorial_completed = bool(row[11]) if len(row) > 11 else False
            user.current_state = row[12] if len(row) > 12 else None
            user.activity_data = row[13] if len(row) > 13 else None
            return user
        except (IndexError, TypeError):
            user.user_id = row[0]
            user.username = row[1] if len(row) > 1 else None
            return user
    return None


async def create_user(user_id: int, username: Optional[str] = None) -> User:
    """Создает нового пользователя"""
    await execute_db("""
                     INSERT INTO users (user_id, username)
                     VALUES (?, ?)
                     """, (user_id, username))

    return await get_user(user_id)


async def get_user_language(user_id: int) -> str:
    """Получает язык пользователя"""
    user = await get_user(user_id)
    return user.language if user else 'ru'


async def update_user_language(user_id: int, language: str):
    """Обновляет язык пользователя"""
    await execute_db(
        "UPDATE users SET language = ? WHERE user_id = ?",
        (language, user_id)
    )


async def complete_tutorial(user_id: int):
    """Отмечает туториал как завершенный и дает награды"""
    await execute_db("""
                     UPDATE users
                     SET tutorial_completed = 1,
                         ryabucks           = ryabucks + 500,
                         energy             = energy + 20
                     WHERE user_id = ?
                     """, (user_id,))


async def set_user_state(user_id: int, state: str, activity_data: str = None):
    """Устанавливает состояние пользователя"""
    await execute_db("""
                     UPDATE users
                     SET current_state = ?,
                         activity_data = ?
                     WHERE user_id = ?
                     """, (state, activity_data, user_id))


async def clear_user_state(user_id: int):
    """Очищает состояние пользователя"""
    await set_user_state(user_id, None, None)


async def get_island_stats() -> dict:
    """Получает статистику острова"""
    try:
        # Общее количество игроков
        result = await execute_db("SELECT COUNT(*) FROM users", fetch_one=True)
        total_players = result[0] if result else 0

        # Активные игроки
        result = await execute_db("""
                                  SELECT COUNT(*)
                                  FROM users
                                  WHERE date (last_active) = date ('now') OR last_active IS NULL
                                  """, fetch_one=True)
        active_players = result[0] if result else 0

        # RBTC найденные сегодня
        result = await execute_db("""
                                  SELECT COALESCE(SUM(rbtc_found), 0)
                                  FROM expeditions
                                  WHERE date (completed_at) = date ('now')
                                  """, fetch_one=True)
        daily_rbtc = result[0] if result else 0.0

        # Активные экспедиции
        result = await execute_db("""
                                  SELECT COUNT(*)
                                  FROM expeditions
                                  WHERE status = 'active'
                                  """, fetch_one=True)
        active_expeditions = result[0] if result else 0

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


async def update_user_resources(user_id: int, **resources):
    """Обновляет ресурсы пользователя"""
    if not resources:
        return

    set_clause = ", ".join([f"{key} = ?" for key in resources.keys()])
    values = list(resources.values()) + [user_id]

    await execute_db(
        f"UPDATE users SET {set_clause}, last_active = CURRENT_TIMESTAMP WHERE user_id = ?",
        values
    )


# ====== АКАДЕМИЯ ======

async def create_academy_tables():
    """Создает таблицы для системы Академии с индексами"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Таблица наемных рабочих
        await db.execute("""
                         CREATE TABLE IF NOT EXISTS hired_workers
                         (
                             id
                             INTEGER
                             PRIMARY
                             KEY
                             AUTOINCREMENT,
                             user_id
                             INTEGER,
                             worker_type
                             TEXT
                             DEFAULT
                             'laborer',
                             status
                             TEXT
                             DEFAULT
                             'idle',
                             hired_at
                             TIMESTAMP
                             DEFAULT
                             CURRENT_TIMESTAMP,
                             next_available_at
                             TIMESTAMP,
                             FOREIGN
                             KEY
                         (
                             user_id
                         ) REFERENCES users
                         (
                             user_id
                         )
                             )
                         """)

        # Таблица обучающихся специалистов
        await db.execute("""
                         CREATE TABLE IF NOT EXISTS training_units
                         (
                             id
                             INTEGER
                             PRIMARY
                             KEY
                             AUTOINCREMENT,
                             user_id
                             INTEGER,
                             unit_type
                             TEXT
                             NOT
                             NULL,
                             status
                             TEXT
                             DEFAULT
                             'training',
                             started_at
                             TIMESTAMP
                             DEFAULT
                             CURRENT_TIMESTAMP,
                             completed_at
                             TIMESTAMP,
                             worker_id
                             INTEGER,
                             FOREIGN
                             KEY
                         (
                             user_id
                         ) REFERENCES users
                         (
                             user_id
                         ),
                             FOREIGN KEY
                         (
                             worker_id
                         ) REFERENCES hired_workers
                         (
                             id
                         )
                             )
                         """)

        # Таблица готовых специалистов
        await db.execute("""
                         CREATE TABLE IF NOT EXISTS trained_specialists
                         (
                             id
                             INTEGER
                             PRIMARY
                             KEY
                             AUTOINCREMENT,
                             user_id
                             INTEGER,
                             specialist_type
                             TEXT
                             NOT
                             NULL,
                             level
                             INTEGER
                             DEFAULT
                             1,
                             status
                             TEXT
                             DEFAULT
                             'available',
                             created_at
                             TIMESTAMP
                             DEFAULT
                             CURRENT_TIMESTAMP,
                             last_worked
                             TIMESTAMP,
                             FOREIGN
                             KEY
                         (
                             user_id
                         ) REFERENCES users
                         (
                             user_id
                         )
                             )
                         """)

        # Таблица ограничений найма
        await db.execute("""
                         CREATE TABLE IF NOT EXISTS hire_cooldowns
                         (
                             id
                             INTEGER
                             PRIMARY
                             KEY
                             AUTOINCREMENT,
                             user_id
                             INTEGER,
                             last_hire_time
                             TIMESTAMP
                             DEFAULT
                             CURRENT_TIMESTAMP,
                             hires_count
                             INTEGER
                             DEFAULT
                             0,
                             reset_date
                             DATE
                             DEFAULT (
                             date
                         (
                             'now'
                         )),
                             FOREIGN KEY
                         (
                             user_id
                         ) REFERENCES users
                         (
                             user_id
                         )
                             )
                         """)

        # ====== ДОБАВЛЯЕМ ИНДЕКСЫ ДЛЯ АКАДЕМИИ ======
        await db.execute("CREATE INDEX IF NOT EXISTS idx_hired_userid ON hired_workers(user_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_hired_status ON hired_workers(status)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_trainings_userid ON training_units(user_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_trainings_status ON training_units(status)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_specialists_userid ON trained_specialists(user_id)")

        await db.commit()


# Функции для работы с разнорабочими
async def get_hired_workers_count(user_id: int) -> dict:
    """Получает количество нанятых рабочих по типам"""
    results = await execute_db("""
                               SELECT worker_type, COUNT(*)
                               FROM hired_workers
                               WHERE user_id = ?
                                 AND status != 'consumed'
                               GROUP BY worker_type
                               """, (user_id,), fetch_all=True)

    return {row[0]: row[1] for row in results} if results else {}


async def can_hire_worker(user_id: int) -> tuple[bool, str, int]:
    """
    Проверяет, может ли пользователь нанять рабочего
    Returns: (можно_нанять, причина, время_до_следующего_найма_в_секундах)
    """
    cooldown = await execute_db("""
                                SELECT last_hire_time, hires_count, reset_date
                                FROM hire_cooldowns
                                WHERE user_id = ?
                                ORDER BY id DESC LIMIT 1
                                """, (user_id,), fetch_one=True)

    if cooldown:
        from datetime import datetime, timedelta
        last_hire = datetime.fromisoformat(cooldown[0])
        hires_today = cooldown[1]
        reset_date = cooldown[2]

        if reset_date != datetime.now().date().isoformat():
            hires_today = 0

        time_since_last_hire = datetime.now() - last_hire
        if time_since_last_hire < timedelta(hours=24):
            remaining_seconds = int((timedelta(hours=24) - time_since_last_hire).total_seconds())
            return False, "cooldown", remaining_seconds

        max_hires = 3
        if hires_today >= max_hires:
            return False, "limit_reached", 0

    return True, "ok", 0


async def hire_worker(user_id: int) -> tuple[bool, str]:
    """
    Нанимает разнорабочего
    Returns: (успешно, сообщение)
    """
    can_hire, reason, remaining = await can_hire_worker(user_id)

    if not can_hire:
        if reason == "cooldown":
            hours = remaining // 3600
            minutes = (remaining % 3600) // 60
            return False, f"⏰ Следующий найм через: {hours}ч {minutes}мин"
        elif reason == "limit_reached":
            return False, "🚫 Достигнут лимит найма! Улучшите подписку."

    user = await get_user(user_id)
    workers_count = await get_hired_workers_count(user_id)
    total_workers = sum(workers_count.values())
    hire_cost = 30 + (5 * total_workers)

    if user.ryabucks < hire_cost:
        return False, f"❌ Недостаточно рябаксов! Нужно: {hire_cost}💵"

    from datetime import datetime, timedelta
    next_available = datetime.now() + timedelta(hours=24)

    await execute_db("""
                     INSERT INTO hired_workers (user_id, worker_type, status, next_available_at)
                     VALUES (?, 'laborer', 'idle', ?)
                     """, (user_id, next_available.isoformat()))

    await execute_db("""
                     INSERT INTO hire_cooldowns (user_id, last_hire_time, hires_count, reset_date)
                     VALUES (?, ?, 1, date ('now')) ON CONFLICT(user_id) DO
                     UPDATE SET
                         last_hire_time = excluded.last_hire_time,
                         hires_count = CASE
                         WHEN reset_date = date ('now') THEN hires_count + 1
                         ELSE 1
                     END
                     ,
            reset_date = date('now')
                     """, (user_id, datetime.now().isoformat()))

    await execute_db("""
                     UPDATE users
                     SET ryabucks = ryabucks - ?
                     WHERE user_id = ?
                     """, (hire_cost, user_id))

    return True, f"✅ Разнорабочий нанят! Потрачено: {hire_cost}💵"


async def get_training_slots_info(user_id: int) -> dict:
    """Получает информацию о слотах обучения"""
    result = await execute_db("""
                              SELECT COUNT(*)
                              FROM training_units
                              WHERE user_id = ?
                                AND status = 'training'
                              """, (user_id,), fetch_one=True)

    active_training = result[0] if result else 0
    base_slots = 2
    total_slots = base_slots

    return {
        'used': active_training,
        'total': total_slots,
        'available': total_slots - active_training
    }


async def start_training(user_id: int, unit_type: str) -> tuple[bool, str]:
    """
    Начинает обучение специалиста
    Returns: (успешно, сообщение)
    """
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

    from datetime import datetime, timedelta

    worker = await execute_db("""
                              SELECT id
                              FROM hired_workers
                              WHERE user_id = ?
                                AND worker_type = 'laborer'
                                AND status = 'idle' LIMIT 1
                              """, (user_id,), fetch_one=True)

    if not worker:
        return False, "❌ Нет свободных разнорабочих!"

    worker_id = worker[0]
    completion_time = datetime.now() + timedelta(hours=unit_info['time_hours'])

    await execute_db("""
                     INSERT INTO training_units (user_id, unit_type, started_at, completed_at, worker_id)
                     VALUES (?, ?, ?, ?, ?)
                     """, (user_id, unit_type, datetime.now().isoformat(), completion_time.isoformat(), worker_id))

    await execute_db("""
                     UPDATE hired_workers
                     SET status = 'training'
                     WHERE id = ?
                     """, (worker_id,))

    await execute_db("""
                     UPDATE users
                     SET ryabucks = ryabucks - ?
                     WHERE user_id = ?
                     """, (unit_info['cost'], user_id))

    hours = int(unit_info['time_hours'])
    minutes = int((unit_info['time_hours'] % 1) * 60)
    return True, f"✅ {unit_info['name']} отправлен на обучение!\n⏰ Завершится через: {hours}ч {minutes}мин"


async def get_active_trainings(user_id: int) -> list:
    """Получает список активных обучений"""
    from datetime import datetime

    trainings = await execute_db("""
                                 SELECT unit_type, started_at, completed_at
                                 FROM training_units
                                 WHERE user_id = ?
                                   AND status = 'training'
                                 ORDER BY completed_at ASC
                                 """, (user_id,), fetch_all=True)

    result = []
    if trainings:
        for training in trainings:
            unit_type, started, completed = training
            completed_time = datetime.fromisoformat(completed)
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
    """Завершает готовые обучения и возвращает количество выпускников"""
    from datetime import datetime

    completed = await execute_db("""
                                 SELECT id, unit_type, worker_id
                                 FROM training_units
                                 WHERE user_id = ?
                                   AND status = 'training'
                                   AND completed_at <= ?
                                 """, (user_id, datetime.now().isoformat()), fetch_all=True)

    count = 0
    if completed:
        for training in completed:
            training_id, unit_type, worker_id = training

            await execute_db("""
                             INSERT INTO trained_specialists (user_id, specialist_type, status)
                             VALUES (?, ?, 'available')
                             """, (user_id, unit_type))

            await execute_db("""
                             UPDATE training_units
                             SET status = 'completed'
                             WHERE id = ?
                             """, (training_id,))

            await execute_db("""
                             UPDATE hired_workers
                             SET status = 'consumed'
                             WHERE id = ?
                             """, (worker_id,))

            count += 1

    return count


async def get_specialists_count(user_id: int) -> dict:
    """Получает количество обученных специалистов по типам"""
    results = await execute_db("""
                               SELECT specialist_type, COUNT(*)
                               FROM trained_specialists
                               WHERE user_id = ?
                                 AND status != 'dead'
                               GROUP BY specialist_type
                               """, (user_id,), fetch_all=True)

    return {row[0]: row[1] for row in results} if results else {}
