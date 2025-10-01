"""
Система локализации для Ryabot Island v2.0
Полная поддержка Supabase архитектуры
"""
import asyncio
import logging
from typing import Optional
from database.models import get_user_language

logger = logging.getLogger(__name__)

# Кеш загруженных локализаций для оптимизации
_locales_cache = {}

def load_locale(lang_code: str) -> dict:
    """
    Загружает локализацию для указанного языка
    Поддерживает кеширование для повышения производительности

    Args:
        lang_code: код языка ('ru', 'en', etc.)

    Returns:
        dict: словарь с текстами локализации
    """
    if lang_code in _locales_cache:
        return _locales_cache[lang_code]

    try:
        if lang_code == 'ru':
            from locales.ru import TEXTS
            logger.debug(f"Загружена русская локализация")
        # elif lang_code == 'en':
        #     from locales.en import TEXTS  # Для будущего расширения
        # elif lang_code == 'uk':
        #     from locales.uk import TEXTS  # Украинская локализация
        else:
            # По умолчанию используем русскую локализацию
            from locales.ru import TEXTS
            logger.warning(f"Локализация '{lang_code}' не найдена, используем русскую")

        _locales_cache[lang_code] = TEXTS
        logger.info(f"✅ Локализация '{lang_code}' загружена и закеширована")
        return TEXTS

    except ImportError as e:
        logger.error(f"❌ Ошибка импорта локализации '{lang_code}': {e}")
        # Fallback - загружаем русскую локализацию
        try:
            from locales.ru import TEXTS
            _locales_cache[lang_code] = TEXTS
            return TEXTS
        except Exception as fallback_error:
            logger.critical(f"💥 Критическая ошибка загрузки локализации: {fallback_error}")
            # Возвращаем минимальный набор текстов
            return {"error": "[LOCALIZATION ERROR]"}

async def get_text(key: str, user_id: int, **kwargs) -> str:
    """
    Получает локализованный текст для пользователя (асинхронная версия)
    Автоматически определяет язык пользователя из Supabase БД

    Args:
        key: ключ текста в локализации
        user_id: ID пользователя Telegram (для определения языка)
        **kwargs: параметры для форматирования текста

    Returns:
        str: форматированный локализованный текст
    """
    try:
        # Получаем язык пользователя из Supabase
        user_lang = await get_user_language(user_id)

        # Загружаем нужную локализацию
        texts = load_locale(user_lang)

        # Получаем текст по ключу
        text = texts.get(key, f"[MISSING: {key}]")

        # Если текст не найден, логируем для разработчиков
        if text.startswith("[MISSING:"):
            logger.warning(f"⚠️ Отсутствует текст для ключа '{key}' в языке '{user_lang}'")

        # Форматируем текст с переданными параметрами
        try:
            formatted_text = text.format(**kwargs)
            return formatted_text
        except (KeyError, ValueError) as format_error:
            logger.error(f"❌ Ошибка форматирования текста '{key}': {format_error}")
            logger.error(f"   Параметры: {kwargs}")
            return text  # Возвращаем неформатированный текст

    except Exception as e:
        logger.error(f"❌ Ошибка получения текста '{key}' для пользователя {user_id}: {e}")
        return f"[ERROR: {key}]"

def t(key: str, lang: str = 'ru', **kwargs) -> str:
    """
    Быстрая синхронная функция для получения текста
    Используется когда язык уже известен (без обращения к БД)

    Args:
        key: ключ текста в локализации
        lang: код языка ('ru', 'en', etc.)
        **kwargs: параметры для форматирования текста

    Returns:
        str: форматированный локализованный текст
    """
    try:
        # Загружаем локализацию
        texts = load_locale(lang)

        # Получаем текст (используем default если ключ не найден)
        if key in texts:
            text = texts[key]
        elif default is not None:
            text = default
        else:
            text = f"[MISSING: {key}]"
            logger.warning(f"⚠️ Отсутствует текст для ключа '{key}' в языке '{lang}'")

        # Форматируем с параметрами
        try:
            return text.format(**kwargs)
        except (KeyError, ValueError) as format_error:
            logger.error(f"❌ Ошибка форматирования в t() '{key}': {format_error}")
            return text

    except Exception as e:
        logger.error(f"❌ Ошибка в функции t() '{key}': {e}")
        if default is not None:
            return default
        return f"[ERROR: {key}]"

def get_game_prices(lang: str = 'ru') -> dict:
    """
    Получает игровые цены из локализации
    Используется для отображения экономической информации

    Args:
        lang: код языка

    Returns:
        dict: словарь с ценами
    """
    try:
        if lang == 'ru':
            from locales.ru import GAME_PRICES
            return GAME_PRICES
        else:
            # Fallback на русские цены
            from locales.ru import GAME_PRICES
            return GAME_PRICES
    except ImportError:
        logger.error(f"❌ Не удалось загрузить цены для языка '{lang}'")
        # Минимальные цены по умолчанию
        return {
            'ryaba_price': 250,
            'rooster_price': 500,
            'rbtc_rate': 100
        }

def validate_localization(lang: str = 'ru') -> tuple[bool, list[str]]:
    """
    Проверяет целостность локализации
    Полезно для отладки и тестирования

    Args:
        lang: код языка для проверки

    Returns:
        tuple: (успешно: bool, список ошибок: list[str])
    """
    errors = []

    try:
        texts = load_locale(lang)

        # Проверяем обязательные ключи
        required_keys = [
            'welcome_to_game',
            'entering_island',
            'academy_welcome',
            'town_welcome',
            'btn_enter_island'
        ]

        for key in required_keys:
            if key not in texts:
                errors.append(f"Отсутствует обязательный ключ: {key}")

        # Проверяем наличие цен
        try:
            prices = get_game_prices(lang)
            if not prices:
                errors.append("Отсутствуют игровые цены")
        except Exception as e:
            errors.append(f"Ошибка загрузки цен: {e}")

    except Exception as e:
        errors.append(f"Критическая ошибка локализации: {e}")

    return len(errors) == 0, errors

def clear_locale_cache():
    """
    Очищает кеш локализаций
    Полезно для перезагрузки текстов в процессе разработки
    """
    global _locales_cache
    _locales_cache.clear()
    logger.info("🧹 Кеш локализаций очищен")

# Функции для совместимости со старым кодом
async def get_user_text(user_id: int, key: str, **kwargs) -> str:
    """Алиас для get_text() - обратная совместимость"""
    return await get_text(key, user_id, **kwargs)

def quick_text(key: str, **kwargs) -> str:
    """Быстрое получение русского текста без указания языка"""
    return t(key, 'ru', **kwargs)

# Функции для форматирования ресурсов
def format_resources(user_data: dict, lang: str = 'ru') -> str:
    """
    Форматирует ресурсы пользователя в читаемый вид

    Args:
        user_data: данные пользователя из БД
        lang: код языка

    Returns:
        str: форматированная строка ресурсов
    """
    try:
        return t('user_resources', lang,
                level=user_data.get('level', 1),
                energy=user_data.get('energy', 100),
                ryabucks=user_data.get('ryabucks', 1000),
                rbtc=f"{user_data.get('rbtc', 0.0):.2f}")
    except Exception as e:
        logger.error(f"❌ Ошибка форматирования ресурсов: {e}")
        return "Уровень: 1 | Энергия: 100/100 | Рябаксы: 1000 | RBTC: 0.00"

def format_time_left(seconds: int, lang: str = 'ru') -> str:
    """
    Форматирует оставшееся время в читаемый вид

    Args:
        seconds: количество секунд
        lang: код языка

    Returns:
        str: форматированное время
    """
    if seconds <= 0:
        return t('time_ready', lang, default="Готово")

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60

    if hours > 0:
        return t('time_hours_minutes', lang, hours=hours, minutes=minutes,
                default=f"{hours}ч {minutes}мин")
    else:
        return t('time_minutes', lang, minutes=minutes, default=f"{minutes}мин")

# Экспорт всех функций
__all__ = [
    'load_locale',
    'get_text',
    't',
    'get_game_prices',
    'validate_localization',
    'clear_locale_cache',
    'get_user_text',
    'quick_text',
    'format_resources',
    'format_time_left'
]

logger.info("✅ Система локализации загружена (Supabase версия)")
