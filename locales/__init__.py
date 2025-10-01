"""
Пакет локализации для Ryabot Island v2.0
Инициализация и управление переводами
"""

# Доступные языки
SUPPORTED_LANGUAGES = {
    'ru': 'Русский',
    # 'en': 'English',      # Для будущего расширения
    # 'uk': 'Українська',   # Украинский
    # 'kz': 'Қазақша',      # Казахский
}

# Язык по умолчанию
DEFAULT_LANGUAGE = 'ru'

def get_supported_languages():
    """Возвращает список поддерживаемых языков"""
    return SUPPORTED_LANGUAGES

def is_language_supported(lang_code: str) -> bool:
    """Проверяет, поддерживается ли язык"""
    return lang_code in SUPPORTED_LANGUAGES

def get_default_language() -> str:
    """Возвращает код языка по умолчанию"""
    return DEFAULT_LANGUAGE
