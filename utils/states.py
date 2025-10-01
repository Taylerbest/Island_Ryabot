"""
FSM состояния для Ryabot Island v2.0
Полная поддержка Supabase архитектуры с расширенными состояниями
"""
from aiogram.fsm.state import State, StatesGroup
from enum import Enum
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Основные состояния навигации
class MenuState(StatesGroup):
    """Состояния главного меню и навигации"""
    OUTSIDE_ISLAND = State()    # Вне острова (стартовое меню)
    ON_ISLAND = State()         # На острове (игровое меню)
    IN_SETTINGS = State()       # В настройках
    IN_SUPPORT = State()        # В поддержке
    LANGUAGE_SELECTION = State() # Выбор языка

# Состояния туториала
class TutorialState(StatesGroup):
    """Состояния системы обучения новичков"""
    WELCOME = State()           # Приветствие
    STEP_1 = State()           # Шаг 1: Профиль и ресурсы
    STEP_2 = State()           # Шаг 2: Ферма и постройки
    STEP_3 = State()           # Шаг 3: Команды и навигация
    STEP_4 = State()           # Шаг 4: Город и услуги
    STEP_5 = State()           # Шаг 5: Академия и специалисты
    COMPLETING = State()        # Завершение туториала
    COMPLETED = State()         # Туториал завершен

# Состояния фермы
class FarmState(StatesGroup):
    """Состояния управления фермой"""
    MAIN_VIEW = State()         # Главный вид фермы
    BUYING_ANIMAL = State()     # Покупка животного
    BUILDING_CONSTRUCTION = State()  # Строительство
    PLANTING_CROPS = State()    # Посадка культур
    COLLECTING_RESOURCES = State()  # Сбор ресурсов
    ANIMAL_MANAGEMENT = State() # Управление животными
    PLOT_SELECTION = State()    # Выбор участка земли

# Состояния города
class TownState(StatesGroup):
    """Состояния навигации по городу"""
    MAIN_VIEW = State()         # Главная площадь
    IN_BUILDING = State()       # Внутри здания
    MARKET_SHOPPING = State()   # Покупки на рынке
    BANK_OPERATIONS = State()   # Операции в банке
    REAL_ESTATE = State()       # Недвижимость
    ENTERTAINMENT = State()     # Развлечения

# Состояния академии
class AcademyState(StatesGroup):
    """Состояния системы обучения и найма"""
    MAIN_VIEW = State()         # Главное меню академии
    LABOR_EXCHANGE = State()    # Биржа труда
    HIRING_WORKER = State()     # Процесс найма
    EXPERT_COURSES = State()    # Экспертные курсы
    PROFESSION_SELECTION = State() # Выбор профессии
    TRAINING_CLASS = State()    # Учебный класс
    CONFIRMING_TRAINING = State() # Подтверждение обучения
    MANAGING_SPECIALISTS = State() # Управление специалистами

# Состояния работы и заработка
class WorkState(StatesGroup):
    """Состояния системы заработка"""
    JOB_SELECTION = State()     # Выбор работы
    WORKING = State()           # Процесс работы
    EXPEDITION_PREP = State()   # Подготовка к экспедиции
    EXPEDITION_ACTIVE = State() # Активная экспедиция
    RBTC_MINING = State()       # Добыча RBTC
    QUEST_ACTIVE = State()      # Выполнение квеста

# Состояния профиля жителя
class CitizenState(StatesGroup):
    """Состояния управления профилем"""
    PROFILE_VIEW = State()      # Просмотр профиля
    ACHIEVEMENTS = State()      # Достижения
    STATISTICS = State()        # Статистика
    QUESTS = State()           # Активные квесты
    SETTINGS = State()         # Настройки профиля
    EDITING_PROFILE = State()   # Редактирование профиля

# Состояния инвентаря
class StorageState(StatesGroup):
    """Состояния управления инвентарем"""
    INVENTORY_VIEW = State()    # Просмотр инвентаря
    ITEM_DETAILS = State()     # Детали предмета
    USING_ITEM = State()       # Использование предмета
    SELLING_ITEM = State()     # Продажа предмета
    ORGANIZING = State()       # Организация инвентаря

# Состояния реферальной системы
class ReferralState(StatesGroup):
    """Состояния реферальной системы"""
    MAIN_VIEW = State()        # Главная страница
    INVITING_FRIEND = State()  # Приглашение друга
    CLAIMING_REWARDS = State() # Получение наград
    FRIEND_LIST = State()      # Список друзей
    BONUS_HISTORY = State()    # История бонусов

# Состояния рейтингов
class RankingState(StatesGroup):
    """Состояния системы рейтингов"""
    LEADERBOARD = State()      # Таблица лидеров
    CATEGORY_SELECTION = State() # Выбор категории
    PERSONAL_RANK = State()    # Личный рейтинг
    SEASON_RESULTS = State()   # Результаты сезона

# Состояния развлечений и игр
class GameState(StatesGroup):
    """Состояния мини-игр и развлечений"""
    ROOSTER_FIGHT_PREP = State()    # Подготовка к петушиному бою
    ROOSTER_FIGHT_ACTIVE = State()  # Активный петушиный бой
    HORSE_RACE_PREP = State()       # Подготовка к скачкам
    HORSE_RACE_ACTIVE = State()     # Активные скачки
    CASINO_GAMES = State()          # Казино игры
    LOTTERY = State()               # Лотерея
    FISHING = State()               # Рыбалка
    HUNTING = State()               # Охота

# Административные состояния
class AdminState(StatesGroup):
    """Состояния для администраторов"""
    MAIN_PANEL = State()           # Главная панель
    USER_MANAGEMENT = State()      # Управление пользователями
    ECONOMY_SETTINGS = State()     # Настройки экономики
    BROADCAST_MESSAGE = State()    # Рассылка сообщений
    STATISTICS_VIEW = State()      # Просмотр статистики
    DATABASE_OPERATIONS = State()  # Операции с БД

# Универсальные состояния
class CommonState(StatesGroup):
    """Общие состояния для всех модулей"""
    CONFIRMATION = State()         # Подтверждение действия
    PAYMENT_PROCESSING = State()   # Обработка платежа
    LOADING = State()              # Загрузка данных
    ERROR_HANDLING = State()       # Обработка ошибки
    PREMIUM_UPGRADE = State()      # Улучшение до Premium

# Перечисления для типизации
class ActivityType(Enum):
    """Типы активности пользователя"""
    IDLE = "idle"                  # Бездействие
    FARMING = "farming"            # Работа на ферме
    EXPEDITION = "expedition"      # В экспедиции
    TRAINING = "training"          # Обучение
    BUILDING = "building"          # Строительство
    SHOPPING = "shopping"          # Покупки
    GAMING = "gaming"              # Игры
    SOCIALIZING = "socializing"    # Общение

class ResourceType(Enum):
    """Типы игровых ресурсов"""
    RYABUCKS = "ryabucks"          # Рябаксы
    RBTC = "rbtc"                  # RBTC кристаллы
    ENERGY = "energy"              # Энергия
    EXPERIENCE = "experience"      # Опыт
    GOLDEN_SHARDS = "golden_shards" # Золотые осколки
    QUANTUM_KEYS = "quantum_keys"   # Квантовые ключи

class PremiumType(Enum):
    """Типы премиум подписок"""
    FREE = "free"                  # Бесплатный аккаунт
    BUSINESS = "business"          # Бизнес лицензия
    QUANTUM = "quantum"            # Quantum Pass
    LIFETIME = "lifetime"          # Пожизненный доступ

# Утилиты для работы с состояниями
class StateManager:
    """Менеджер состояний для Supabase интеграции"""

    @staticmethod
    def get_state_category(state: State) -> str:
        """Получить категорию состояния"""
        if not state:
            return "unknown"

        state_name = state.state
        if ":" in state_name:
            return state_name.split(":")[0]
        return "common"

    @staticmethod
    def get_state_name(state: State) -> str:
        """Получить имя состояния"""
        if not state:
            return "unknown"

        state_name = state.state
        if ":" in state_name:
            return state_name.split(":")[1]
        return state_name

    @staticmethod
    async def save_user_state(user_id: int, state: State, data: Dict[str, Any] = None):
        """Сохранить состояние пользователя в Supabase"""
        try:
            from database.models import set_user_state
            import json

            state_str = state.state if state else None
            data_str = json.dumps(data) if data else None

            await set_user_state(user_id, state_str, data_str)
            logger.debug(f"Состояние пользователя {user_id} сохранено: {state_str}")

        except Exception as e:
            logger.error(f"Ошибка сохранения состояния пользователя {user_id}: {e}")

    @staticmethod
    async def load_user_state(user_id: int) -> tuple[Optional[str], Optional[Dict[str, Any]]]:
        """Загрузить состояние пользователя из Supabase"""
        try:
            from database.models import get_user
            import json

            user = await get_user(user_id)
            if not user:
                return None, None

            state_str = user.current_state
            data = None

            if user.activity_data:
                try:
                    data = json.loads(user.activity_data)
                except json.JSONDecodeError:
                    logger.warning(f"Некорректные данные состояния для пользователя {user_id}")
                    data = None

            return state_str, data

        except Exception as e:
            logger.error(f"Ошибка загрузки состояния пользователя {user_id}: {e}")
            return None, None

    @staticmethod
    async def clear_user_state(user_id: int):
        """Очистить состояние пользователя"""
        try:
            from database.models import clear_user_state
            await clear_user_state(user_id)
            logger.debug(f"Состояние пользователя {user_id} очищено")

        except Exception as e:
            logger.error(f"Ошибка очистки состояния пользователя {user_id}: {e}")

# Константы для состояний
DEFAULT_STATE = MenuState.ON_ISLAND
INITIAL_STATE = MenuState.OUTSIDE_ISLAND

# Маппинг состояний к их описаниям
STATE_DESCRIPTIONS = {
    MenuState.OUTSIDE_ISLAND: "Вне острова",
    MenuState.ON_ISLAND: "На острове",
    TutorialState.STEP_1: "Туториал: Основы",
    TutorialState.STEP_2: "Туториал: Ферма",
    TutorialState.STEP_3: "Туториал: Команды",
    FarmState.MAIN_VIEW: "Ферма",
    TownState.MAIN_VIEW: "Город",
    AcademyState.MAIN_VIEW: "Академия",
    WorkState.EXPEDITION_ACTIVE: "Экспедиция",
    GameState.ROOSTER_FIGHT_ACTIVE: "Петушиный бой",
    GameState.HORSE_RACE_ACTIVE: "Скачки"
}

# Функции для быстрого доступа к состояниям
def get_state_description(state: State) -> str:
    """Получить описание состояния на русском языке"""
    return STATE_DESCRIPTIONS.get(state, "Неизвестное состояние")

def is_game_state(state: State) -> bool:
    """Проверить, является ли состояние игровым"""
    if not state:
        return False
    return isinstance(state, (GameState, WorkState))

def is_menu_state(state: State) -> bool:
    """Проверить, является ли состояние меню"""
    if not state:
        return False
    return isinstance(state, MenuState)

def is_tutorial_state(state: State) -> bool:
    """Проверить, является ли состояние туториалом"""
    if not state:
        return False
    return isinstance(state, TutorialState)

# Создание глобального менеджера состояний
state_manager = StateManager()

logger.info("✅ FSM States системы загружены (Supabase версия)")
