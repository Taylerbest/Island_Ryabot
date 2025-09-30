# handlers/start.py

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from utils.message_helper import send_formatted
from database.models import (
    get_user, create_user, update_user_language,
    init_database, clear_user_state, complete_tutorial
)
from keyboards.main_menu import get_start_menu, get_island_menu, get_tutorial_keyboard
from utils.texts import t
from utils.states import MenuState, TutorialState

router = Router()

@router.message(Command("start"))
async def start_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username

    user = await get_user(user_id)

    if not user:
        # Новый пользователь: предложить выбор языка
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=t("language_ru", "ru"), callback_data="lang_ru")]
        ])
        welcome_text = t("choose_language", "ru")
        await send_formatted(message, welcome_text, reply_markup=keyboard)
        await state.set_state(MenuState.OUTSIDE_ISLAND)
        return

    # Существующий пользователь: показываем главное меню
    await clear_user_state(user_id)
    await send_main_menu(message, user, state)

async def send_main_menu(message: Message, user, state: FSMContext):
    """Отправляет главное меню с кнопками Вход на остров, Настройки и Поддержка"""
    welcome_text = t(
        "welcome_to_game", user.language,
        online_players=0,
        daily_rbtc="0.00",
        active_expeditions=0
    )

    keyboard = get_start_menu(user.language)
    await send_formatted(
        message,
        welcome_text,
        reply_markup=keyboard
    )
    await state.set_state(MenuState.OUTSIDE_ISLAND)

@router.callback_query(F.data.startswith("lang_"))
async def language_selected(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    username = callback.from_user.username
    language = callback.data.split("_")[1]

    user = await create_user(user_id, username)
    await update_user_language(user_id, language)

    await callback.message.edit_text(text=t("language_selected", language))
    await send_main_menu(callback.message, user, state)
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
                      rbtc=f"{user.rbtc:.2f}")

    await send_formatted(
        message,
        entering_text,
        reply_markup=get_island_menu(user.language)
    )
    await state.set_state(MenuState.ON_ISLAND)

async def start_tutorial(message: Message, user, state: FSMContext):
    """Запускает туториал для новых игроков"""
    tutorial_text = t('tutorial_welcome', user.language)

    await send_formatted(
        message,
        tutorial_text,
        reply_markup=get_tutorial_keyboard(0, user.language)
    )
    await state.set_state(TutorialState.STEP_1)

@router.callback_query(F.data == "tutorial_start")
async def tutorial_step_1(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user = await get_user(user_id)

    step1_text = t('tutorial_step_1', user.language)

    await send_formatted(
        callback,
        step1_text,
        reply_markup=get_tutorial_keyboard(1, user.language),
        edit=True
    )
    await state.set_state(TutorialState.STEP_1)
    await callback.answer()

@router.callback_query(F.data == "tutorial_step_2")
async def tutorial_step_2(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user = await get_user(user_id)

    step2_text = t('tutorial_step_2', user.language)

    await send_formatted(
        callback,
        step2_text,
        reply_markup=get_tutorial_keyboard(2, user.language),
        edit=True
    )
    await state.set_state(TutorialState.STEP_2)
    await callback.answer()

@router.callback_query(F.data == "tutorial_step_3")
async def tutorial_step_3(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user = await get_user(user_id)

    step3_text = t('tutorial_step_3', user.language)

    await send_formatted(
        callback,
        step3_text,
        reply_markup=get_tutorial_keyboard(3, user.language),
        edit=True
    )
    await state.set_state(TutorialState.STEP_3)
    await callback.answer()

@router.callback_query(F.data == "tutorial_complete")
async def tutorial_complete_handler(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    await complete_tutorial(user_id)

    user = await get_user(user_id)
    complete_text = t('tutorial_complete', user.language)
    await callback.message.edit_text(text=complete_text)

    entering_text = t('entering_island', user.language,
                      level=user.level,
                      energy=user.energy,
                      ryabucks=user.ryabucks,
                      rbtc=f"{user.rbtc:.2f}")

    await send_formatted(
        callback,
        entering_text,
        reply_markup=get_island_menu(user.language)
    )
    await state.set_state(MenuState.ON_ISLAND)
    await callback.answer()

@router.callback_query(F.data == "tutorial_skip")
async def tutorial_skip(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    await complete_tutorial(user_id)
    user = await get_user(user_id)

    entering_text = t('entering_island', user.language,
                      level=user.level,
                      energy=user.energy,
                      ryabucks=user.ryabucks,
                      rbtc=f"{user.rbtc:.2f}")

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
