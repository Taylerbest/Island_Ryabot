"""
Помощник для отправки сообщений в Ryabot Island v2.0
Универсальные функции для форматирования и отправки сообщений
Полная поддержка Supabase архитектуры
"""
import logging
from typing import Union, Optional, Any
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
import asyncio

logger = logging.getLogger(__name__)


async def send_formatted(
        obj: Union[Message, CallbackQuery],
        text: str,
        reply_markup: Optional[Union[InlineKeyboardMarkup, ReplyKeyboardMarkup]] = None,
        edit: bool = False,
        parse_mode: str = "Markdown",
        disable_web_page_preview: bool = True,
        protect_content: bool = False,
        reply_to_message_id: Optional[int] = None
) -> Optional[Message]:
    """
    Универсальная функция для отправки отформатированных сообщений
    Поддерживает как Message, так и CallbackQuery объекты

    Args:
        obj: Message или CallbackQuery объект
        text: текст сообщения (поддерживает Markdown)
        reply_markup: клавиатура (inline или reply)
        edit: редактировать существующее сообщение (только для CallbackQuery)
        parse_mode: режим парсинга ("Markdown", "HTML" или None)
        disable_web_page_preview: отключить предпросмотр ссылок
        protect_content: защитить контент от пересылки
        reply_to_message_id: ID сообщения для ответа

    Returns:
        Message: отправленное сообщение или None при ошибке
    """
    try:
        # Валидация текста
        if not text or not text.strip():
            logger.warning("Попытка отправить пустое сообщение")
            text = "⚠️ Пустое сообщение"

        # Обрезаем слишком длинные сообщения
        if len(text) > 4096:
            text = text[:4090] + "..."
            logger.warning(f"Сообщение обрезано до 4096 символов")

        # Параметры отправки
        send_params = {
            "text": text,
            "reply_markup": reply_markup,
            "parse_mode": parse_mode,
            "disable_web_page_preview": disable_web_page_preview,
            "protect_content": protect_content
        }

        # Обработка CallbackQuery (inline кнопки)
        if isinstance(obj, CallbackQuery):
            if edit and obj.message:
                # Редактирование существующего сообщения
                try:
                    return await obj.message.edit_text(**send_params)
                except TelegramBadRequest as e:
                    if "message is not modified" in str(e).lower():
                        logger.debug("Сообщение не изменилось - пропускаем")
                        return obj.message
                    elif "message to edit not found" in str(e).lower():
                        logger.warning("Сообщение для редактирования не найдено, отправляем новое")
                        return await obj.message.answer(**send_params)
                    else:
                        raise
            else:
                # Отправка нового сообщения
                if reply_to_message_id:
                    send_params["reply_to_message_id"] = reply_to_message_id
                return await obj.message.answer(**send_params)

        # Обработка Message (обычные сообщения)
        elif isinstance(obj, Message):
            if reply_to_message_id:
                send_params["reply_to_message_id"] = reply_to_message_id
            return await obj.answer(**send_params)

        else:
            logger.error(f"Неподдерживаемый тип объекта: {type(obj)}")
            return None

    except TelegramRetryAfter as e:
        # Обработка rate limit
        logger.warning(f"Rate limit: ждем {e.retry_after} секунд")
        await asyncio.sleep(e.retry_after)

        # Повторная попытка без retry_after параметров
        try:
            if isinstance(obj, CallbackQuery) and edit:
                return await obj.message.edit_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
            elif isinstance(obj, CallbackQuery):
                return await obj.message.answer(text, reply_markup=reply_markup, parse_mode=parse_mode)
            else:
                return await obj.answer(text, reply_markup=reply_markup, parse_mode=parse_mode)
        except Exception as retry_error:
            logger.error(f"Ошибка при повторной отправке: {retry_error}")
            return None

    except TelegramBadRequest as e:
        # Обработка ошибок форматирования
        error_msg = str(e).lower()

        if "can't parse entities" in error_msg or "bad request" in error_msg:
            logger.warning(f"Ошибка парсинга Markdown, отправляем как обычный текст: {e}")
            # Повторная отправка без форматирования
            try:
                send_params["parse_mode"] = None
                if isinstance(obj, CallbackQuery) and edit:
                    return await obj.message.edit_text(**send_params)
                elif isinstance(obj, CallbackQuery):
                    return await obj.message.answer(**send_params)
                else:
                    return await obj.answer(**send_params)
            except Exception as fallback_error:
                logger.error(f"Критическая ошибка отправки: {fallback_error}")
                return None
        else:
            logger.error(f"Ошибка Telegram API: {e}")
            return None

    except Exception as e:
        logger.error(f"Неожиданная ошибка отправки сообщения: {e}")
        return None


async def send_error_message(
        obj: Union[Message, CallbackQuery],
        error_text: str = "⚠️ Произошла ошибка. Попробуйте позже.",
        show_alert: bool = False
) -> bool:
    """
    Отправляет сообщение об ошибке пользователю

    Args:
        obj: Message или CallbackQuery объект
        error_text: текст ошибки
        show_alert: показать как alert (только для CallbackQuery)

    Returns:
        bool: успешность отправки
    """
    try:
        if isinstance(obj, CallbackQuery):
            if show_alert:
                await obj.answer(error_text, show_alert=True)
                return True
            else:
                await obj.answer(error_text, show_alert=False)
                await send_formatted(obj, error_text)
                return True
        else:
            await send_formatted(obj, error_text)
            return True
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения об ошибке: {e}")
        return False


async def send_success_message(
        obj: Union[Message, CallbackQuery],
        success_text: str = "✅ Операция выполнена успешно!",
        show_alert: bool = False,
        auto_close_alert: bool = True
) -> bool:
    """
    Отправляет сообщение об успешном выполнении операции

    Args:
        obj: Message или CallbackQuery объект
        success_text: текст успеха
        show_alert: показать как alert (только для CallbackQuery)
        auto_close_alert: автоматически закрыть alert

    Returns:
        bool: успешность отправки
    """
    try:
        if isinstance(obj, CallbackQuery):
            if show_alert:
                await obj.answer(success_text, show_alert=True)
                return True
            else:
                if auto_close_alert:
                    await obj.answer(success_text, show_alert=False)
                return True
        else:
            await send_formatted(obj, success_text)
            return True
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения об успехе: {e}")
        return False


async def send_loading_message(
        obj: Union[Message, CallbackQuery],
        loading_text: str = "⏳ Обработка запроса...",
        edit: bool = False
) -> Optional[Message]:
    """
    Отправляет сообщение о загрузке/обработке

    Args:
        obj: Message или CallbackQuery объект
        loading_text: текст загрузки
        edit: редактировать сообщение (для CallbackQuery)

    Returns:
        Message: отправленное сообщение или None
    """
    try:
        return await send_formatted(obj, loading_text, edit=edit, parse_mode=None)
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения загрузки: {e}")
        return None


def escape_markdown_v2(text: str) -> str:
    """
    Экранирует специальные символы для MarkdownV2

    Args:
        text: исходный текст

    Returns:
        str: экранированный текст
    """
    # Символы, которые нужно экранировать в MarkdownV2
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']

    for char in special_chars:
        text = text.replace(char, f'\\{char}')

    return text


def format_user_resources(user_data: dict, language: str = 'ru') -> str:
    """
    Форматирует ресурсы пользователя в читаемый вид

    Args:
        user_data: данные пользователя (dict или объект User)
        language: язык пользователя

    Returns:
        str: форматированная строка ресурсов
    """
    try:
        if hasattr(user_data, '__dict__'):
            # Объект User
            level = getattr(user_data, 'level', 1)
            energy = getattr(user_data, 'energy', 100)
            ryabucks = getattr(user_data, 'ryabucks', 1000)
            rbtc = getattr(user_data, 'rbtc', 0.0)
        else:
            # Словарь
            level = user_data.get('level', 1)
            energy = user_data.get('energy', 100)
            ryabucks = user_data.get('ryabucks', 1000)
            rbtc = user_data.get('rbtc', 0.0)

        return f"⭐ Уровень: {level} | 🔋 {energy}/100 | 💵 {ryabucks} | 💠 {rbtc:.2f}"

    except Exception as e:
        logger.error(f"Ошибка форматирования ресурсов: {e}")
        return "⭐ Уровень: 1 | 🔋 100/100 | 💵 1000 | 💠 0.00"


def format_time_remaining(seconds: int, language: str = 'ru') -> str:
    """
    Форматирует оставшееся время в человеческий вид

    Args:
        seconds: количество секунд
        language: язык пользователя

    Returns:
        str: форматированное время
    """
    if seconds <= 0:
        return "Готово"

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60

    if hours > 0:
        return f"{hours}ч {minutes}мин"
    elif minutes > 0:
        return f"{minutes}мин {remaining_seconds}с"
    else:
        return f"{remaining_seconds}с"


async def safe_callback_answer(
        callback: CallbackQuery,
        text: str = "",
        show_alert: bool = False,
        cache_time: int = 0
) -> bool:
    """
    Безопасный ответ на callback query с обработкой ошибок

    Args:
        callback: CallbackQuery объект
        text: текст ответа
        show_alert: показать как alert
        cache_time: время кеширования

    Returns:
        bool: успешность ответа
    """
    try:
        await callback.answer(
            text=text,
            show_alert=show_alert,
            cache_time=cache_time
        )
        return True
    except TelegramBadRequest as e:
        if "query is too old" in str(e).lower():
            logger.debug("Callback query слишком старый - игнорируем")
        else:
            logger.warning(f"Ошибка ответа на callback: {e}")
        return False
    except Exception as e:
        logger.error(f"Неожиданная ошибка callback answer: {e}")
        return False


async def send_progress_message(
        obj: Union[Message, CallbackQuery],
        current: int,
        total: int,
        description: str = "Прогресс",
        edit: bool = False
) -> Optional[Message]:
    """
    Отправляет сообщение с прогресс-баром

    Args:
        obj: Message или CallbackQuery объект
        current: текущее значение
        total: максимальное значение
        description: описание прогресса
        edit: редактировать сообщение

    Returns:
        Message: отправленное сообщение
    """
    try:
        if total <= 0:
            percentage = 0
        else:
            percentage = min(100, int((current / total) * 100))

        # Создаем визуальный прогресс-бар
        filled = int(percentage / 10)
        empty = 10 - filled
        progress_bar = "🟩" * filled + "⬜" * empty

        progress_text = f"{description}\n{progress_bar}\n{current}/{total} ({percentage}%)"

        return await send_formatted(obj, progress_text, edit=edit, parse_mode=None)

    except Exception as e:
        logger.error(f"Ошибка отправки прогресса: {e}")
        return None


# Алиасы для обратной совместимости
async def send_message(obj, text, **kwargs):
    """Алиас для send_formatted"""
    return await send_formatted(obj, text, **kwargs)


async def edit_message(obj, text, **kwargs):
    """Алиас для send_formatted с edit=True"""
    return await send_formatted(obj, text, edit=True, **kwargs)


# Статистика использования (для мониторинга)
_message_stats = {
    'sent': 0,
    'errors': 0,
    'rate_limits': 0
}


def get_message_stats() -> dict:
    """Получить статистику отправки сообщений"""
    return _message_stats.copy()


def reset_message_stats():
    """Сбросить статистику"""
    global _message_stats
    _message_stats = {'sent': 0, 'errors': 0, 'rate_limits': 0}


logger.info("✅ Message helper загружен (Supabase версия)")
