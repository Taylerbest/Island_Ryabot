"""
Система меню для Ryabot Island (2 столбца по 4 пункта)
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from utils.texts import t

def get_start_menu(lang: str = 'ru') -> ReplyKeyboardMarkup:
    """Стартовое меню (вне острова) - в один ряд"""

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t('btn_enter_island', lang))],
            [
                KeyboardButton(text=t('btn_settings', lang)),
                KeyboardButton(text=t('btn_support', lang)),
                KeyboardButton(text=t('btn_language', lang))
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Выберите действие..."
    )

    return keyboard

def get_island_menu(lang: str = 'ru') -> ReplyKeyboardMarkup:
    """Игровое меню (на острове) - 2 столбца по 4 кнопки"""

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=t('menu_farm', lang)),
                KeyboardButton(text=t('menu_town', lang))
            ],
            [
                KeyboardButton(text=t('menu_citizen', lang)),
                KeyboardButton(text=t('menu_work', lang))
            ],
            [
                KeyboardButton(text=t('menu_storage', lang)),
                KeyboardButton(text=t('menu_referral', lang))
            ],
            [
                KeyboardButton(text=t('menu_rankings', lang)),
                KeyboardButton(text=t('menu_about', lang))
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Используйте команды меню для быстрых действий!"
    )

    return keyboard

def get_tutorial_keyboard(step: int, lang: str = 'ru') -> InlineKeyboardMarkup:
    """Клавиатура для туториала (без изменений)"""

    if step == 0:  # Начальный выбор
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=t('btn_tutorial_start', lang),
                callback_data="tutorial_start"
            )],
            [InlineKeyboardButton(
                text=t('btn_tutorial_skip', lang),
                callback_data="tutorial_skip"
            )]
        ])
    elif step < 3:  # Промежуточные шаги
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=t('btn_tutorial_next', lang),
                callback_data=f"tutorial_step_{step + 1}"
            )]
        ])
    else:  # Завершение
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=t('btn_tutorial_complete', lang),
                callback_data="tutorial_complete"
            )]
        ])

    return keyboard
