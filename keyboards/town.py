# keyboards/town.py
"""
Клавиатуры для раздела "Город"
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_town_menu(lang: str = "ru") -> InlineKeyboardMarkup:
    """Создает меню города с инлайн кнопками в 2 столбца"""

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        # Первый ряд
        [
            InlineKeyboardButton(text="🏛️ Ратуша", callback_data="town_hall"),
            InlineKeyboardButton(text="🛒 Рынок", callback_data="market")
        ],
        # Второй ряд
        [
            InlineKeyboardButton(text="🏦 Рябанк", callback_data="ryabank"),
            InlineKeyboardButton(text="🏪 Продукты", callback_data="products")
        ],
        # Третий ряд
        [
            InlineKeyboardButton(text="💫 Ломбард", callback_data="pawnshop"),
            InlineKeyboardButton(text="🍻 Таверна", callback_data="tavern1")
        ],
        # Четвертый ряд
        [
            InlineKeyboardButton(text="🏫 Академия", callback_data="academy"),
            InlineKeyboardButton(text="🎡 Развлечения", callback_data="entertainment")
        ],
        # Пятый ряд
        [
            InlineKeyboardButton(text="🏢 Недвижка", callback_data="real_estate"),
            InlineKeyboardButton(text="❤️‍🩹 Ветклиника", callback_data="vet_clinic")
        ],
        # Шестой ряд - ИЗМЕНЕНО
        [
            InlineKeyboardButton(text="🏗️ Строй-Сам", callback_data="construction"),
            InlineKeyboardButton(text="🏥 Больница", callback_data="hospital")
        ],
        # Седьмой ряд
        [
            InlineKeyboardButton(text="💻 КвантХаб", callback_data="quantum_hub"),
            InlineKeyboardButton(text="🪦 Кладбище", callback_data="cemetery")
        ]
    ])

    return keyboard
