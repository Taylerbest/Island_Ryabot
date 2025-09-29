"""
Система локализации для Ryabot Island
"""
import asyncio
from typing import Optional
from database.models import get_user_language

# Кеш загруженных локализаций
_locales_cache = {}

def load_locale(lang_code: str) -> dict:
    """Загружает локализацию для указанного языка"""
    if lang_code in _locales_cache:
        return _locales_cache[lang_code]

    try:
        if lang_code == 'ru':
            from locales.ru import TEXTS
        # elif lang_code == 'en':
        #     from locales.en import TEXTS  # Для будущего
        else:
            from locales.ru import TEXTS  # По умолчанию русский

        _locales_cache[lang_code] = TEXTS
        return TEXTS
    except ImportError:
        # Если локализация не найдена, используем русскую
        from locales.ru import TEXTS
        return TEXTS

async def get_text(key: str, user_id: int, **kwargs) -> str:
    """
    Получает локализованный текст для пользователя

    Args:
        key: ключ текста в локализации
        user_id: ID пользователя (для определения языка)
        **kwargs: параметры для форматирования текста
    """
    # Получаем язык пользователя из БД
    user_lang = await get_user_language(user_id)

    # Загружаем нужную локализацию
    texts = load_locale(user_lang)

    # Получаем текст
    text = texts.get(key, f"[{key}]")  # Если ключ не найден, показываем его

    # Форматируем текст с параметрами
    try:
        return text.format(**kwargs)
    except (KeyError, ValueError):
        return text

def t(key: str, lang: str = 'ru', **kwargs) -> str:
    """
    Быстрая функция для получения текста (синхронная)
    Используется когда язык уже известен
    """
    texts = load_locale(lang)
    text = texts.get(key, f"[{key}]")

    try:
        return text.format(**kwargs)
    except (KeyError, ValueError):
        return text
