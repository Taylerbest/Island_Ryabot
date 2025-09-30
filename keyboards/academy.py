"""
Клавиатуры для системы Академии
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_academy_menu() -> InlineKeyboardMarkup:
    """Главное меню Академии"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛠️ Биржа Труда", callback_data="labor_exchange")],
        [InlineKeyboardButton(text="🎓 Экспертные Курсы", callback_data="expert_courses")],
        [InlineKeyboardButton(text="🏫 Учебный Класс", callback_data="training_class")],
        [InlineKeyboardButton(text="↩️ Назад", callback_data="town")]
    ])
    return keyboard


def get_labor_exchange_menu(can_hire: bool, hired_count: int) -> InlineKeyboardMarkup:
    """Меню биржи труда с визуальным представлением слотов"""
    buttons = []

    # Заголовки столбцов (слева направо)
    header_row = [
        InlineKeyboardButton(text="📋", callback_data="info_header"),  # Заголовок
        InlineKeyboardButton(text="Слот 1", callback_data="slot_header_1"),
        InlineKeyboardButton(text="Слот 2", callback_data="slot_header_2"),
        InlineKeyboardButton(text="Слот 3", callback_data="slot_header_3")
    ]
    buttons.append(header_row)

    # Строка 1: Бесплатные слоты (3 шт)
    free_row = [InlineKeyboardButton(text="🆓", callback_data="info_free_slots")]
    for i in range(3):
        if i < hired_count and hired_count <= 3:
            # Слот на кулдауне
            free_row.append(InlineKeyboardButton(text="⏳", callback_data=f"cooldown_free_{i}"))
        else:
            # Свободный слот
            free_row.append(InlineKeyboardButton(text="🙍‍♂️", callback_data=f"hire_slot_free_{i}"))
    buttons.append(free_row)

    # Строка 2: Слоты бизнес-лицензии (3 шт)
    business_row = [InlineKeyboardButton(text="📜", callback_data="info_business_slots")]
    for i in range(3, 6):
        if i < hired_count and 3 < hired_count <= 6:
            business_row.append(InlineKeyboardButton(text="⏳", callback_data=f"cooldown_business_{i}"))
        else:
            business_row.append(InlineKeyboardButton(text="🙍‍♂️", callback_data=f"hire_slot_business_{i}"))
    buttons.append(business_row)

    # Строка 3: Слоты Quantum-Pass (3 шт)
    quantum_row = [InlineKeyboardButton(text="🪪", callback_data="info_quantum_slots")]
    for i in range(6, 9):
        if i < hired_count and hired_count > 6:
            quantum_row.append(InlineKeyboardButton(text="⏳", callback_data=f"cooldown_quantum_{i}"))
        else:
            quantum_row.append(InlineKeyboardButton(text="🙍‍♂️", callback_data=f"hire_slot_quantum_{i}"))
    buttons.append(quantum_row)

    # Кнопка ускорения и назад
    buttons.append([InlineKeyboardButton(text="💠 Boost", callback_data="skip_hire_cooldown")])
    buttons.append([InlineKeyboardButton(text="↩️ Назад", callback_data="back_to_academy")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_profession_selection_menu() -> InlineKeyboardMarkup:
    """Меню выбора профессии для обучения (3x3 сетка)"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        # Ряд 1: Основные профессии
        [
            InlineKeyboardButton(text="👷 Строитель", callback_data="train_builder"),
            InlineKeyboardButton(text="👨‍🌾 Фермер", callback_data="train_farmer"),
            InlineKeyboardButton(text="🧑‍🚒 Лесник", callback_data="train_woodman")
        ],
        # Ряд 2: Боевые и добывающие
        [
            InlineKeyboardButton(text="💂 Солдат", callback_data="train_soldier"),
            InlineKeyboardButton(text="🎣 Рыбак", callback_data="train_fisherman"),
            InlineKeyboardButton(text="👨‍🔬 Ученый", callback_data="train_scientist")
        ],
        # Ряд 3: Обслуживающие профессии
        [
            InlineKeyboardButton(text="👨‍🍳 Повар", callback_data="train_cook"),
            InlineKeyboardButton(text="👨‍🏫 Учитель", callback_data="train_teacher"),
            InlineKeyboardButton(text="🧑‍⚕️ Доктор", callback_data="train_doctor")
        ],
        # Назад
        [InlineKeyboardButton(text="↩️ Назад", callback_data="back_to_academy")]
    ])
    return keyboard


def get_training_menu() -> InlineKeyboardMarkup:
    """Меню подтверждения обучения"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Начать обучение", callback_data="confirm_training")],
        [InlineKeyboardButton(text="↩️ Назад", callback_data="expert_courses")]
    ])
    return keyboard


def get_training_class_menu() -> InlineKeyboardMarkup:
    """Меню учебного класса"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💠 Ускорить обучение", callback_data="boost_training")],
        [InlineKeyboardButton(text="🔄 Обновить", callback_data="training_class")],
        [InlineKeyboardButton(text="↩️ Назад", callback_data="back_to_academy")]
    ])
    return keyboard
