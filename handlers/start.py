"""
Обработчик команд и меню Ryabot Island (версия с командами)
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta
import random

from database.models import (
    get_user, create_user, update_user_language, init_database,
    get_island_stats, complete_tutorial, set_user_state, clear_user_state
)
from keyboards.main_menu import get_start_menu, get_island_menu, get_tutorial_keyboard
from utils.texts import get_text, t
from utils.states import MenuState, TutorialState
from locales.ru import GAME_PRICES

router = Router()

@router.message(Command('start'))
async def start_handler(message: Message, state: FSMContext):
    """Команда /start - перезагрузка/начало игры"""
    user_id = message.from_user.id
    username = message.from_user.username

    await init_database()
    user = await get_user(user_id)

    if not user:
        # Новый пользователь
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=t('language_ru'), callback_data="lang_ru")]
        ])

        await message.answer(
            text=t('choose_language'),
            reply_markup=keyboard
        )
        await state.set_state(MenuState.OUTSIDE_ISLAND)
    else:
        # Существующий пользователь - перезагрузка
        await clear_user_state(user_id)
        await show_start_menu(message, user, state)

@router.message(Command('menu'))
async def menu_handler(message: Message, state: FSMContext):
    """Команда /menu - возврат в главное меню"""
    user_id = message.from_user.id
    user = await get_user(user_id)

    if not user:
        await start_handler(message, state)
        return

    # Показываем главное меню острова
    menu_text = t('main_menu_message', user.language,
        level=user.level,
        energy=user.energy,
        ryabucks=user.ryabucks,
        rbtc=f"{user.rbtc:.2f}"
    )

    await message.answer(
        text=menu_text,
        reply_markup=get_island_menu(user.language)
    )
    await state.set_state(MenuState.ON_ISLAND)

@router.message(Command('economy'))
async def economy_handler(message: Message):
    """Команда /economy - обзор экономики"""
    user_id = message.from_user.id
    user = await get_user(user_id)

    if not user:
        await message.answer("Сначала войдите на остров: /start")
        return

    economy_text = t('economy_overview', user.language, **GAME_PRICES)

    await message.answer(text=economy_text)

@router.message(Command('claim'))
async def claim_energy_handler(message: Message):
    """Команда /claim - сбор энергии с конюшни"""
    user_id = message.from_user.id
    user = await get_user(user_id)

    if not user:
        await message.answer("Сначала войдите на остров: /start")
        return

    # Проверяем, есть ли конюшня (пока заглушка)
    has_stable = user.level >= 2  # Примерное условие

    if not has_stable:
        no_stable_text = t('no_stable', user.language,
                          stable_price=GAME_PRICES['stable_price'])
        await message.answer(text=no_stable_text)
        return

    # Симуляция: энергия готова каждые 4 часа
    # В реальной игре это будет через базу данных
    last_claim = datetime.now() - timedelta(hours=5)  # Симуляция
    next_claim = last_claim + timedelta(hours=4)

    if datetime.now() < next_claim:
        time_left = str(next_claim - datetime.now()).split('.')[0]
        not_ready_text = t('energy_not_ready', user.language,
            time_left=time_left,
            current_energy=user.energy
        )
        await message.answer(text=not_ready_text)
        return

    # Начисляем энергию
    energy_amount = random.randint(15, 25)
    new_energy = min(100, user.energy + energy_amount)

    # Обновляем в базе (пока без реального обновления)
    claimed_text = t('energy_claimed', user.language,
        energy_amount=energy_amount,
        current_energy=new_energy,
        next_claim_time="4 часа"
    )

    await message.answer(text=claimed_text)

@router.message(Command('gather'))
async def gather_all_handler(message: Message):
    """Команда /gather - сбор всего с фермы (Premium)"""
    user_id = message.from_user.id
    user = await get_user(user_id)

    if not user:
        await message.answer("Сначала войдите на остров: /start")
        return

    # Проверяем Quantum Pass (пока заглушка)
    has_quantum_pass = user.level >= 10  # Примерное условие

    if not has_quantum_pass:
        premium_text = t('gather_premium_only', user.language)
        await message.answer(text=premium_text)
        return

    # Симуляция сбора с фермы
    has_resources = random.choice([True, False])

    if not has_resources:
        nothing_text = t('gather_all_nothing', user.language,
            eggs_time_left="2 часа",
            milk_time_left="3 часа",
            crops_time_left="1 час"
        )
        await message.answer(text=nothing_text)
        return

    # Симуляция успешного сбора
    eggs = random.randint(5, 15)
    milk = random.randint(3, 8)
    crops = random.randint(10, 25)
    honey = random.randint(2, 6)
    total_income = eggs * 10 + milk * 15 + crops * 5 + honey * 20

    success_text = t('gather_all_success', user.language,
        eggs_collected=eggs,
        milk_collected=milk,
        crops_collected=crops,
        honey_collected=honey,
        total_income=total_income
    )

    await message.answer(text=success_text)

async def show_start_menu(message: Message, user, state: FSMContext):
    """Показывает стартовое меню с статистикой острова"""
    stats = await get_island_stats()

    welcome_text = t('welcome_to_game', user.language,
        online_players=stats['online_players'],
        daily_rbtc=f"{stats['daily_rbtc']:.2f}",
        active_expeditions=stats['active_expeditions']
    )

    await message.answer(
        text=welcome_text,
        reply_markup=get_start_menu(user.language)
    )
    await state.set_state(MenuState.OUTSIDE_ISLAND)

@router.callback_query(F.data.startswith('lang_'))
async def language_selected(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора языка"""
    user_id = callback.from_user.id
    username = callback.from_user.username
    language = callback.data.split('_')[1]

    user = await create_user(user_id, username)
    await update_user_language(user_id, language)

    await callback.message.edit_text(text=t('language_selected', language))
    await show_start_menu(callback.message, user, state)
    await callback.answer()

@router.message(F.text == "🏝️ Войти на остров")
async def enter_island(message: Message, state: FSMContext):
    """Обработчик входа на остров"""
    user_id = message.from_user.id
    user = await get_user(user_id)

    if not user:
        await start_handler(message, state)
        return

    if not user.tutorial_completed:
        await start_tutorial(message, user, state)
        return

    entering_text = t('entering_island', user.language,
        level=user.level,
        energy=user.energy,
        ryabucks=user.ryabucks,
        rbtc=f"{user.rbtc:.2f}"
    )

    await message.answer(
        text=entering_text,
        reply_markup=get_island_menu(user.language)
    )
    await state.set_state(MenuState.ON_ISLAND)

# Туториал (без изменений)
async def start_tutorial(message: Message, user, state: FSMContext):
    """Запускает туториал для новых игроков"""
    tutorial_text = t('tutorial_welcome', user.language)

    await message.answer(
        text=tutorial_text,
        reply_markup=get_tutorial_keyboard(0, user.language)
    )
    await state.set_state(TutorialState.STEP_1)

@router.callback_query(F.data == "tutorial_start")
async def tutorial_step_1(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user = await get_user(user_id)

    step1_text = t('tutorial_step_1', user.language)

    await callback.message.edit_text(
        text=step1_text,
        reply_markup=get_tutorial_keyboard(1, user.language)
    )
    await state.set_state(TutorialState.STEP_1)
    await callback.answer()

@router.callback_query(F.data == "tutorial_step_2")
async def tutorial_step_2(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user = await get_user(user_id)

    step2_text = t('tutorial_step_2', user.language)

    await callback.message.edit_text(
        text=step2_text,
        reply_markup=get_tutorial_keyboard(2, user.language)
    )
    await state.set_state(TutorialState.STEP_2)
    await callback.answer()

@router.callback_query(F.data == "tutorial_step_3")
async def tutorial_step_3(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user = await get_user(user_id)

    step3_text = t('tutorial_step_3', user.language)

    await callback.message.edit_text(
        text=step3_text,
        reply_markup=get_tutorial_keyboard(3, user.language)
    )
    await state.set_state(TutorialState.STEP_3)
    await callback.answer()

@router.callback_query(F.data == "tutorial_complete")
async def tutorial_complete_handler(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user = await get_user(user_id)

    await complete_tutorial(user_id)

    complete_text = t('tutorial_complete', user.language)
    await callback.message.edit_text(text=complete_text)

    entering_text = t('entering_island', user.language,
        level=user.level,
        energy=120,  # С бонусом
        ryabucks=1500,  # С бонусом
        rbtc=f"{user.rbtc:.2f}"
    )

    await callback.message.answer(
        text=entering_text,
        reply_markup=get_island_menu(user.language)
    )

    await state.set_state(MenuState.ON_ISLAND)
    await callback.answer()

@router.callback_query(F.data == "tutorial_skip")
async def tutorial_skip(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user = await get_user(user_id)

    await complete_tutorial(user_id)

    entering_text = t('entering_island', user.language,
        level=user.level,
        energy=user.energy,
        ryabucks=user.ryabucks,
        rbtc=f"{user.rbtc:.2f}"
    )

    await callback.message.edit_text(text="Туториал пропущен!")
    await callback.message.answer(
        text=entering_text,
        reply_markup=get_island_menu(user.language)
    )

    await state.set_state(MenuState.ON_ISLAND)
    await callback.answer()

@router.message(F.text.in_(["⚙️ Настройки", "📱 Поддержка", "🌍 Язык"]))
async def start_menu_buttons(message: Message, state: FSMContext):
    button_text = message.text

    if button_text == "⚙️ Настройки":
        await message.answer("🚧 Настройки в разработке!")
    elif button_text == "📱 Поддержка":
        await message.answer("📱 Поддержка: @your_support_username")
    elif button_text == "🌍 Язык":
        await message.answer("🚧 Смена языка в разработке!")
