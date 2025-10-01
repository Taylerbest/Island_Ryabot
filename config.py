"""
Конфигурация Ryabot Island для Supabase
Версия 2.0 - Полный переход на Supabase с Python SDK
"""
import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()


@dataclass
class SupabaseConfig:
    """Конфигурация Supabase"""
    url: str = os.getenv("SUPABASE_URL", "")
    anon_key: str = os.getenv("SUPABASE_ANON_KEY", "")
    service_role_key: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

    def validate(self) -> tuple[bool, list[str]]:
        """Валидация обязательных параметров"""
        errors = []

        if not self.url:
            errors.append("SUPABASE_URL не установлен")
        elif not self.url.startswith("https://"):
            errors.append("SUPABASE_URL должен начинаться с https://")

        if not self.anon_key:
            errors.append("SUPABASE_ANON_KEY не установлен")
        elif len(self.anon_key) < 100:
            errors.append("SUPABASE_ANON_KEY слишком короткий")

        return len(errors) == 0, errors


@dataclass
class BotConfig:
    """Конфигурация Telegram бота"""
    token: str = os.getenv("BOT_TOKEN", "")
    webhook_url: Optional[str] = os.getenv("WEBHOOK_URL")
    webhook_path: str = "/webhook"
    admin_ids: list[int] = None

    def __post_init__(self):
        # Парсим ID админов из строки
        admin_str = os.getenv("ADMIN_IDS", "")
        if admin_str:
            try:
                self.admin_ids = [int(x.strip()) for x in admin_str.split(",") if x.strip()]
            except ValueError:
                self.admin_ids = []
        else:
            self.admin_ids = []

    def validate(self) -> tuple[bool, list[str]]:
        """Валидация параметров бота"""
        errors = []

        if not self.token:
            errors.append("BOT_TOKEN не установлен")
        elif not self.token.count(":") == 1:
            errors.append("BOT_TOKEN имеет неверный формат")

        if self.webhook_url and not self.webhook_url.startswith("https://"):
            errors.append("WEBHOOK_URL должен начинаться с https://")

        return len(errors) == 0, errors

    def is_admin(self, user_id: int) -> bool:
        """Проверка админских прав"""
        return user_id in self.admin_ids


@dataclass
class GameConfig:
    """Игровая конфигурация"""
    # Энергия
    max_energy: int = int(os.getenv("MAX_ENERGY", "100"))
    energy_regen_hours: int = int(os.getenv("ENERGY_REGEN_HOURS", "4"))

    # Лимиты
    max_land_plots: int = int(os.getenv("MAX_LAND_PLOTS", "12"))
    max_buildings_per_plot: int = int(os.getenv("MAX_BUILDINGS_PER_PLOT", "4"))

    # Экономика
    base_ryabucks: int = int(os.getenv("BASE_RYABUCKS", "1000"))
    rbtc_to_ryabucks_rate: float = float(os.getenv("RBTC_RATE", "100.0"))

    # Найм рабочих
    hire_base_cost: int = int(os.getenv("HIRE_BASE_COST", "30"))
    hire_cost_increment: int = int(os.getenv("HIRE_COST_INCREMENT", "5"))
    hire_cooldown_hours: int = int(os.getenv("HIRE_COOLDOWN_HOURS", "24"))
    hire_daily_limit: int = int(os.getenv("HIRE_DAILY_LIMIT", "3"))

    # Академия
    training_base_slots: int = int(os.getenv("TRAINING_BASE_SLOTS", "2"))

    def get_hire_cost(self, current_workers: int) -> int:
        """Расчет стоимости найма рабочего"""
        return self.hire_base_cost + (self.hire_cost_increment * current_workers)


@dataclass
class ServerConfig:
    """Конфигурация сервера"""
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    environment: str = os.getenv("ENVIRONMENT", "development")  # development | production
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Middleware настройки
    throttle_rate: float = float(os.getenv("THROTTLE_RATE", "0.3"))

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        return self.environment == "development"


@dataclass
class LoggingConfig:
    """Конфигурация логирования"""
    level: str = os.getenv("LOG_LEVEL", "INFO")
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = os.getenv("LOG_FILE")
    max_file_size: int = int(os.getenv("LOG_MAX_SIZE", "10485760"))  # 10MB
    backup_count: int = int(os.getenv("LOG_BACKUP_COUNT", "5"))


class Config:
    """Основной класс конфигурации"""

    def __init__(self):
        self.supabase = SupabaseConfig()
        self.bot = BotConfig()
        self.game = GameConfig()
        self.server = ServerConfig()
        self.logging = LoggingConfig()

        # Кеш для часто используемых значений
        self._prices_cache = None

    def validate_all(self) -> tuple[bool, list[str]]:
        """Валидация всех конфигураций"""
        all_errors = []

        supabase_valid, supabase_errors = self.supabase.validate()
        bot_valid, bot_errors = self.bot.validate()

        all_errors.extend(supabase_errors)
        all_errors.extend(bot_errors)

        return len(all_errors) == 0, all_errors

    def get_game_prices(self) -> dict:
        """Получение игровых цен (с кешированием)"""
        if self._prices_cache is not None:
            return self._prices_cache

        self._prices_cache = {
            # Животные
            'ryaba_price': int(os.getenv("RYABA_PRICE", "250")),
            'rooster_price': int(os.getenv("ROOSTER_PRICE", "500")),
            'chick_price': int(os.getenv("CHICK_PRICE", "100")),
            'horse_price': int(os.getenv("HORSE_PRICE", "1500")),
            'cow_price': int(os.getenv("COW_PRICE", "1200")),

            # Семена
            'grain_seeds_price': int(os.getenv("GRAIN_SEEDS_PRICE", "25")),
            'tomato_seeds_price': int(os.getenv("TOMATO_SEEDS_PRICE", "50")),
            'cucumber_seeds_price': int(os.getenv("CUCUMBER_SEEDS_PRICE", "40")),

            # Постройки
            'henhouse_price': int(os.getenv("HENHOUSE_PRICE", "800")),
            'stable_price': int(os.getenv("STABLE_PRICE", "2000")),
            'cowshed_price': int(os.getenv("COWSHED_PRICE", "1800")),

            # Валюты
            'rbtc_rate': self.game.rbtc_to_ryabucks_rate,
            'shard_rate': float(os.getenv("SHARD_RATE", "50.0")),
        }

        return self._prices_cache

    def get_training_data(self) -> dict:
        """Данные о профессиях для обучения"""
        return {
            'builder': {
                'name': '👷 Строитель',
                'cost': int(os.getenv("BUILDER_COST", "100")),
                'time_hours': float(os.getenv("BUILDER_TIME", "2.0"))
            },
            'farmer': {
                'name': '👨‍🌾 Фермер',
                'cost': int(os.getenv("FARMER_COST", "100")),
                'time_hours': float(os.getenv("FARMER_TIME", "2.0"))
            },
            'woodman': {
                'name': '🧑‍🚒 Лесник',
                'cost': int(os.getenv("WOODMAN_COST", "120")),
                'time_hours': float(os.getenv("WOODMAN_TIME", "3.0"))
            },
            'soldier': {
                'name': '💂 Солдат',
                'cost': int(os.getenv("SOLDIER_COST", "150")),
                'time_hours': float(os.getenv("SOLDIER_TIME", "4.0"))
            },
            'fisherman': {
                'name': '🎣 Рыбак',
                'cost': int(os.getenv("FISHERMAN_COST", "110")),
                'time_hours': float(os.getenv("FISHERMAN_TIME", "2.5"))
            },
            'scientist': {
                'name': '👨‍🔬 Ученый',
                'cost': int(os.getenv("SCIENTIST_COST", "200")),
                'time_hours': float(os.getenv("SCIENTIST_TIME", "6.0"))
            },
            'cook': {
                'name': '👨‍🍳 Повар',
                'cost': int(os.getenv("COOK_COST", "130")),
                'time_hours': float(os.getenv("COOK_TIME", "3.0"))
            },
            'teacher': {
                'name': '👨‍🏫 Учитель',
                'cost': int(os.getenv("TEACHER_COST", "180")),
                'time_hours': float(os.getenv("TEACHER_TIME", "5.0"))
            },
            'doctor': {
                'name': '🧑‍⚕️ Доктор',
                'cost': int(os.getenv("DOCTOR_COST", "220")),
                'time_hours': float(os.getenv("DOCTOR_TIME", "8.0"))
            }
        }

    def clear_cache(self):
        """Очистка кеша (для перезагрузки цен)"""
        self._prices_cache = None


# Глобальный экземпляр конфигурации
config = Config()


# Функция для быстрой валидации при запуске
def validate_config_or_exit():
    """Валидация конфигурации с выходом при ошибке"""
    import sys
    import logging

    valid, errors = config.validate_all()

    if not valid:
        logging.error("❌ Ошибки конфигурации:")
        for error in errors:
            logging.error(f"   - {error}")

        logging.error("\n💡 Проверьте ваш .env файл:")
        logging.error("   SUPABASE_URL=https://your-project.supabase.co")
        logging.error("   SUPABASE_ANON_KEY=your-anon-key")
        logging.error("   BOT_TOKEN=your-bot-token")

        sys.exit(1)

    return True


# Для совместимости со старым кодом
class LegacyConfig:
    """Обратная совместимость со старым config.py"""

    @property
    def BOT_TOKEN(self):
        return config.bot.token

    @property
    def WEBHOOK_URL(self):
        return config.bot.webhook_url

    @property
    def WEBHOOK_PATH(self):
        return config.bot.webhook_path

    @property
    def MAX_ENERGY(self):
        return config.game.max_energy

    @property
    def ENERGY_REGEN_HOURS(self):
        return config.game.energy_regen_hours

    @property
    def HOST(self):
        return config.server.host

    @property
    def PORT(self):
        return config.server.port

    @property
    def ENVIRONMENT(self):
        return config.server.environment


# Создаем экземпляр для обратной совместимости
legacy_config = LegacyConfig()

# Экспорт для удобства
__all__ = [
    'config',
    'validate_config_or_exit',
    'SupabaseConfig',
    'BotConfig',
    'GameConfig',
    'ServerConfig',
    'LoggingConfig',
    'Config'
]
