"""
Система меню для Ryabot Island v2.0
Полная поддержка Supabase архитектуры с улучшенным UX
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from utils.texts import t
import logging

logger = logging.getLogger(__name__)

def get_start_menu(lang: str = 'ru') -> ReplyKeyboardMarkup:
    """
    Стартовое меню (вне острова)
    Показывается до входа на остров - минималистичный дизайн
    """
    try:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                # Главная кнопка входа
                [KeyboardButton(text=t('btn_enter_island', lang, default="🏝️ Войти на остров"))],

                # Дополнительные опции в одну строку
                [
                    KeyboardButton(text=t('btn_settings', lang, default="⚙️ Настройки")),
                    KeyboardButton(text=t('btn_support', lang, default="📱 Поддержка")),
                    KeyboardButton(text=t('btn_language', lang, default="🌍 Язык"))
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=False,
            input_field_placeholder=t('placeholder_start_menu', lang,
                                     default="Выберите действие для начала игры..."),
            selective=True
        )

        logger.debug(f"Start menu created for language: {lang}")
        return keyboard

    except Exception as e:
        logger.error(f"Error creating start menu for {lang}: {e}")
        # Fallback меню
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🏝️ Войти на остров")],
                [
                    KeyboardButton(text="⚙️ Настройки"),
                    KeyboardButton(text="📱 Поддержка")
                ]
            ],
            resize_keyboard=True
        )

def get_island_menu(lang: str = 'ru') -> ReplyKeyboardMarkup:
    """
    Главное игровое меню (на острове)
    Оптимизированная сетка 2x4 для удобства использования
    """
    try:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                # Ряд 1: Основная деятельность
                [
                    KeyboardButton(text=t('menu_farm', lang, default="🏠 Ферма")),
                    KeyboardButton(text=t('menu_town', lang, default="🏢 Город"))
                ],
                # Ряд 2: Персональное развитие
                [
                    KeyboardButton(text=t('menu_citizen', lang, default="👤 Житель")),
                    KeyboardButton(text=t('menu_work', lang, default="💼 ₽ябота"))
                ],
                # Ряд 3: Управление ресурсами
                [
                    KeyboardButton(text=t('menu_storage', lang, default="🎒 Рюкзак")),
                    KeyboardButton(text=t('menu_referral', lang, default="👥 Друзья"))
                ],
                # Ряд 4: Соревнования и информация
                [
                    KeyboardButton(text=t('menu_rankings', lang, default="🏆 Лидеры")),
                    KeyboardButton(text=t('menu_about', lang, default="🗄️ Прочее"))
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=False,
            input_field_placeholder=t('placeholder_island_menu', lang,
                                     default="Используйте команды меню или /claim для быстрых действий!"),
            selective=False
        )

        logger.debug(f"Island menu created for language: {lang}")
        return keyboard

    except Exception as e:
        logger.error(f"Error creating island menu for {lang}: {e}")
        # Fallback меню
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🏠 Ферма"), KeyboardButton(text="🏢 Город")],
                [KeyboardButton(text="👤 Житель"), KeyboardButton(text="💼 ₽ябота")],
                [KeyboardButton(text="🎒 Рюкзак"), KeyboardButton(text="👥 Друзья")],
                [KeyboardButton(text="🏆 Лидеры"), KeyboardButton(text="🗄️ Прочее")]
            ],
            resize_keyboard=True
        )

def get_tutorial_keyboard(step: int, lang: str = 'ru') -> InlineKeyboardMarkup:
    """
    Клавиатура для системы туториала
    Адаптивные кнопки в зависимости от шага обучения
    """
    try:
        if step == 0:  # Начальный экран
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text=t('btn_tutorial_start', lang, default="🎓 Начать обучение"),
                    callback_data="tutorial_start"
                )],
                [InlineKeyboardButton(
                    text=t('btn_tutorial_skip', lang, default="⚡ Пропустить"),
                    callback_data="tutorial_skip"
                )]
            ])

        elif 1 <= step <= 2:  # Промежуточные шаги
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text=t('btn_tutorial_next', lang, default="➡️ Далее"),
                    callback_data=f"tutorial_step_{step + 1}"
                )],
                [InlineKeyboardButton(
                    text=t('btn_tutorial_skip', lang, default="⚡ Пропустить"),
                    callback_data="tutorial_skip"
                )]
            ])

        elif step == 3:  # Предпоследний шаг
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text=t('btn_tutorial_complete', lang, default="🎉 Завершить обучение"),
                    callback_data="tutorial_complete"
                )],
                [InlineKeyboardButton(
                    text=t('btn_tutorial_skip', lang, default="⚡ Пропустить"),
                    callback_data="tutorial_skip"
                )]
            ])

        else:  # Завершение (step >= 4)
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text=t('btn_tutorial_finish', lang, default="✨ Начать игру"),
                    callback_data="tutorial_complete"
                )]
            ])

        logger.debug(f"Tutorial keyboard created for step {step}, language: {lang}")
        return keyboard

    except Exception as e:
        logger.error(f"Error creating tutorial keyboard for step {step}: {e}")
        # Fallback клавиатура
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➡️ Продолжить", callback_data=f"tutorial_step_{step + 1}")],
            [InlineKeyboardButton(text="⚡ Пропустить", callback_data="tutorial_skip")]
        ])

def get_language_selection_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура выбора языка
    Расширяемая система для поддержки новых языков
    """
    try:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            # Основные языки
            [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
            # Будущие языки (закомментированы до реализации)
            # [InlineKeyboardButton(text="🇺🇸 English", callback_data="lang_en")],
            # [InlineKeyboardButton(text="🇺🇦 Українська", callback_data="lang_uk")],
            # [InlineKeyboardButton(text="🇰🇿 Қазақша", callback_data="lang_kz")],

            # Кнопка помощи
            [InlineKeyboardButton(
                text="❓ Помочь с переводом",
                callback_data="help_translate"
            )]
        ])

        logger.debug("Language selection keyboard created")
        return keyboard

    except Exception as e:
        logger.error(f"Error creating language keyboard: {e}")
        # Fallback клавиатура
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")]
        ])

def get_quick_actions_keyboard(lang: str = 'ru') -> InlineKeyboardMarkup:
    """
    Клавиатура быстрых действий для продвинутых пользователей
    Отображается при определенных условиях (Quantum Pass, высокий уровень)
    """
    try:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            # Ряд 1: Сбор ресурсов
            [
                InlineKeyboardButton(
                    text=t('quick_claim_energy', lang, default="🔋 Собрать энергию"),
                    callback_data="quick_claim_energy"
                ),
                InlineKeyboardButton(
                    text=t('quick_gather_all', lang, default="🧺 Собрать всё"),
                    callback_data="quick_gather_all"
                )
            ],
            # Ряд 2: Экономика
            [
                InlineKeyboardButton(
                    text=t('quick_economy', lang, default="📊 Экономика"),
                    callback_data="quick_economy"
                ),
                InlineKeyboardButton(
                    text=t('quick_stats', lang, default="📈 Статистика"),
                    callback_data="quick_stats"
                )
            ],
            # Ряд 3: Навигация
            [
                InlineKeyboardButton(
                    text=t('quick_academy', lang, default="🎓 Академия"),
                    callback_data="academy"
                ),
                InlineKeyboardButton(
                    text=t('quick_expeditions', lang, default="🗺️ Экспедиции"),
                    callback_data="expeditions"
                )
            ]
        ])

        logger.debug(f"Quick actions keyboard created for language: {lang}")
        return keyboard

    except Exception as e:
        logger.error(f"Error creating quick actions keyboard: {e}")
        # Fallback клавиатура
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📊 Экономика", callback_data="quick_economy")]
        ])

def get_settings_keyboard(lang: str = 'ru') -> InlineKeyboardMarkup:
    """
    Клавиатура настроек пользователя
    """
    try:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            # Основные настройки
            [
                InlineKeyboardButton(
                    text=t('settings_language', lang, default="🌍 Сменить язык"),
                    callback_data="settings_language"
                )
            ],
            [
                InlineKeyboardButton(
                    text=t('settings_notifications', lang, default="🔔 Уведомления"),
                    callback_data="settings_notifications"
                )
            ],
            # Премиум возможности
            [
                InlineKeyboardButton(
                    text=t('settings_quantum_pass', lang, default="✨ Quantum Pass"),
                    callback_data="settings_quantum_pass"
                )
            ],
            # Дополнительно
            [
                InlineKeyboardButton(
                    text=t('settings_reset_tutorial', lang, default="🔄 Повторить туториал"),
                    callback_data="settings_reset_tutorial"
                )
            ],
            # Назад
            [
                InlineKeyboardButton(
                    text=t('btn_back', lang, default="↩️ Назад"),
                    callback_data="back_to_start"
                )
            ]
        ])

        logger.debug(f"Settings keyboard created for language: {lang}")
        return keyboard

    except Exception as e:
        logger.error(f"Error creating settings keyboard: {e}")
        # Fallback клавиатура
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🌍 Язык", callback_data="settings_language")],
            [InlineKeyboardButton(text="↩️ Назад", callback_data="back_to_start")]
        ])

def get_support_keyboard(lang: str = 'ru') -> InlineKeyboardMarkup:
    """
    Клавиатура поддержки и помощи
    """
    try:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            # Прямые ссылки
            [
                InlineKeyboardButton(
                    text=t('support_telegram', lang, default="💬 Telegram поддержка"),
                    url="https://t.me/ryabot_support"
                )
            ],
            [
                InlineKeyboardButton(
                    text=t('support_faq', lang, default="❓ Часто задаваемые вопросы"),
                    callback_data="support_faq"
                )
            ],
            # Отчеты об ошибках
            [
                InlineKeyboardButton(
                    text=t('support_bug_report', lang, default="🐛 Сообщить об ошибке"),
                    callback_data="support_bug_report"
                )
            ],
            [
                InlineKeyboardButton(
                    text=t('support_feature_request', lang, default="💡 Предложить идею"),
                    callback_data="support_feature_request"
                )
            ],
            # Сообщество
            [
                InlineKeyboardButton(
                    text=t('support_community', lang, default="👥 Сообщество игроков"),
                    url="https://t.me/ryabot_island_chat"
                )
            ],
            # Назад
            [
                InlineKeyboardButton(
                    text=t('btn_back', lang, default="↩️ Назад"),
                    callback_data="back_to_start"
                )
            ]
        ])

        logger.debug(f"Support keyboard created for language: {lang}")
        return keyboard

    except Exception as e:
        logger.error(f"Error creating support keyboard: {e}")
        # Fallback клавиатура
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💬 Поддержка", url="https://t.me/ryabot_support")],
            [InlineKeyboardButton(text="↩️ Назад", callback_data="back_to_start")]
        ])

def get_back_button(lang: str = 'ru', callback_data: str = "back") -> InlineKeyboardMarkup:
    """
    Универсальная кнопка "Назад"
    Используется в различных меню для единообразия
    """
    try:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=t('btn_back', lang, default="↩️ Назад"),
                callback_data=callback_data
            )]
        ])

        return keyboard

    except Exception as e:
        logger.error(f"Error creating back button: {e}")
        # Fallback кнопка
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="↩️ Назад", callback_data=callback_data)]
        ])

# Функции валидации клавиатур
def validate_keyboard_structure(keyboard: ReplyKeyboardMarkup) -> bool:
    """
    Валидирует структуру Reply клавиатуры
    Проверяет лимиты Telegram API
    """
    try:
        if not keyboard.keyboard:
            return False

        # Максимум 12 строк
        if len(keyboard.keyboard) > 12:
            logger.warning("Reply keyboard has more than 12 rows")
            return False

        # Максимум 4 кнопки в строке для оптимального отображения
        for row in keyboard.keyboard:
            if len(row) > 4:
                logger.warning("Reply keyboard row has more than 4 buttons")
                return False

        return True

    except Exception as e:
        logger.error(f"Error validating keyboard structure: {e}")
        return False

def validate_inline_keyboard_structure(keyboard: InlineKeyboardMarkup) -> bool:
    """
    Валидирует структуру Inline клавиатуры
    Проверяет лимиты Telegram API
    """
    try:
        if not keyboard.inline_keyboard:
            return False

        # Максимум 100 кнопок общим числом
        total_buttons = sum(len(row) for row in keyboard.inline_keyboard)
        if total_buttons > 100:
            logger.warning("Inline keyboard has more than 100 buttons")
            return False

        # Максимум 8 кнопок в строке
        for row in keyboard.inline_keyboard:
            if len(row) > 8:
                logger.warning("Inline keyboard row has more than 8 buttons")
                return False

        return True

    except Exception as e:
        logger.error(f"Error validating inline keyboard structure: {e}")
        return False

# Функции для создания адаптивных клавиатур
def create_adaptive_keyboard(items: list, max_columns: int = 2, lang: str = 'ru') -> ReplyKeyboardMarkup:
    """
    Создает адаптивную Reply клавиатуру на основе списка элементов
    Автоматически распределяет элементы по строкам
    """
    try:
        if not items:
            return get_island_menu(lang)  # Fallback на основное меню

        rows = []
        current_row = []

        for item in items:
            current_row.append(KeyboardButton(text=item))

            if len(current_row) >= max_columns:
                rows.append(current_row)
                current_row = []

        # Добавляем последнюю строку если есть оставшиеся элементы
        if current_row:
            rows.append(current_row)

        keyboard = ReplyKeyboardMarkup(
            keyboard=rows,
            resize_keyboard=True,
            one_time_keyboard=False
        )

        if validate_keyboard_structure(keyboard):
            return keyboard
        else:
            logger.warning("Adaptive keyboard validation failed, using fallback")
            return get_island_menu(lang)

    except Exception as e:
        logger.error(f"Error creating adaptive keyboard: {e}")
        return get_island_menu(lang)

def create_adaptive_inline_keyboard(items: list, max_columns: int = 2) -> InlineKeyboardMarkup:
    """
    Создает адаптивную Inline клавиатуру на основе списка элементов
    Каждый элемент должен быть tuple (text, callback_data)
    """
    try:
        if not items:
            return InlineKeyboardMarkup(inline_keyboard=[])

        rows = []
        current_row = []

        for item in items:
            if isinstance(item, tuple) and len(item) == 2:
                text, callback_data = item
                current_row.append(InlineKeyboardButton(text=text, callback_data=callback_data))

                if len(current_row) >= max_columns:
                    rows.append(current_row)
                    current_row = []

        # Добавляем последнюю строку если есть оставшиеся элементы
        if current_row:
            rows.append(current_row)

        keyboard = InlineKeyboardMarkup(inline_keyboard=rows)

        if validate_inline_keyboard_structure(keyboard):
            return keyboard
        else:
            logger.warning("Adaptive inline keyboard validation failed")
            return InlineKeyboardMarkup(inline_keyboard=[])

    except Exception as e:
        logger.error(f"Error creating adaptive inline keyboard: {e}")
        return InlineKeyboardMarkup(inline_keyboard=[])

logger.info("✅ Main menu keyboards loaded (Supabase версия)")
