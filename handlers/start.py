"""
Обработчик стартовых команд для Ryabot Island v2.0
Полная поддержка Supabase архитектуры
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from utils.message_helper import send_formatted
from database.models import (
    get_user, create_user, update_user_language,
    clear_user_state, complete_tutorial, get_island_stats
)
from keyboards.main_menu import get_start_menu, get_island_menu, get_tutorial_keyboard
from utils.texts import get_text, t
from utils.states import MenuState, TutorialState
import logging

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("start"))
async def start_handler(message: Message, state: FSMContext):
    """
    Главный обработчик команды /start
    Определяет новый или существующий пользователь
    """
    user_id = message.from_user.id
    username = message.from_user.username

    try:
        # Проверяем существование пользователя
        user = await get_user(user_id)

        if not user:
            # Новый пользователь: предложить выбор языка
            await handle_new_user(message, state)
            return

        # Существующий пользователь: главное меню
        await clear_user_state(user_id)
        await send_main_menu(message, user, state)

    except Exception as e:
        logger.error(f"Ошибка в start_handler для пользователя {user_id}: {e}")
        await message.answer("⚠️ Произошла ошибка. Попробуйте позже или обратитесь в поддержку.")


async def handle_new_user(message: Message, state: FSMContext):
    """Обработка нового пользователя"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
        # [InlineKeyboardButton(text="🇺🇸 English", callback_data="lang_en")],  # Для будущего
    ])

    welcome_text = t("choose_language", "ru")
    await send_formatted(message, welcome_text, reply_markup=keyboard)
    await state.set_state(MenuState.OUTSIDE_ISLAND)


async def send_main_menu(message: Message, user, state: FSMContext):
    """
    Отправляет главное меню с актуальной статистикой острова
    """
    try:
        # Получаем статистику острова
        stats = await get_island_stats()

        welcome_text = await get_text(
            'welcome_to_game', user.user_id,
            online_players=stats.get('online_players', 12),
            daily_rbtc=f"{stats.get('daily_rbtc', 15.67):.2f}",
            active_expeditions=stats.get('active_expeditions', 8)
        )

        keyboard = get_start_menu(user.language)
        await send_formatted(message, welcome_text, reply_markup=keyboard)
        await state.set_state(MenuState.OUTSIDE_ISLAND)

    except Exception as e:
        logger.error(f"Ошибка отправки главного меню для пользователя {user.user_id}: {e}")
        # Fallback без статистики
        welcome_text = t('welcome_to_game', user.language,
                         online_players=12, daily_rbtc="15.67", active_expeditions=8)
        keyboard = get_start_menu(user.language)
        await send_formatted(message, welcome_text, reply_markup=keyboard)


@router.callback_query(F.data.startswith("lang_"))
async def language_selected(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора языка новым пользователем"""
    try:
        await callback.answer()

        user_id = callback.from_user.id
        username = callback.from_user.username
        language = callback.data.split("_")[1]

        # Создаем нового пользователя
        user = await create_user(user_id, username)
        if not user:
            await callback.message.edit_text("❌ Ошибка создания профиля. Попробуйте /start")
            return

        # Устанавливаем язык
        await update_user_language(user_id, language)

        # Подтверждаем выбор языка
        confirmation_text = t("language_selected", language)
        await callback.message.edit_text(confirmation_text)

        # Небольшая пауза и показываем главное меню
        import asyncio
        await asyncio.sleep(1)

        # Обновляем объект пользователя с новым языком
        user.language = language
        await send_main_menu(callback.message, user, state)

    except Exception as e:
        logger.error(f"Ошибка выбора языка для пользователя {callback.from_user.id}: {e}")
        await callback.message.edit_text("❌ Ошибка выбора языка. Попробуйте /start")


@router.message(F.text == "🏝️ Войти на остров")
async def enter_island(message: Message, state: FSMContext):
    """Обработчик входа на остров"""
    try:
        user_id = message.from_user.id
        user = await get_user(user_id)

        if not user:
            await start_handler(message, state)
            return

        # Проверяем туториал
        if not user.tutorial_completed:
            await start_tutorial(message, user, state)
            return

        # Входим на остров
        entering_text = await get_text('entering_island', user_id,
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

    except Exception as e:
        logger.error(f"Ошибка входа на остров для пользователя {message.from_user.id}: {e}")
        await message.answer("⚠️ Ошибка входа на остров. Попробуйте позже.")


async def start_tutorial(message: Message, user, state: FSMContext):
    """Запускает туториал для новых игроков"""
    try:
        tutorial_text = await get_text('tutorial_welcome', user.user_id)

        await send_formatted(
            message,
            tutorial_text,
            reply_markup=get_tutorial_keyboard(0, user.language)
        )
        await state.set_state(TutorialState.STEP_1)

    except Exception as e:
        logger.error(f"Ошибка запуска туториала для пользователя {user.user_id}: {e}")
        # Пропускаем туториал при ошибке
        await complete_tutorial(user.user_id)
        await enter_island(message, state)


@router.callback_query(F.data == "tutorial_start")
async def tutorial_step_1(callback: CallbackQuery, state: FSMContext):
    """Первый шаг туториала"""
    try:
        await callback.answer()

        user_id = callback.from_user.id
        user = await get_user(user_id)

        if not user:
            await callback.message.edit_text("❌ Ошибка: пользователь не найден")
            return

        step1_text = await get_text('tutorial_step_1', user_id)

        await send_formatted(
            callback,
            step1_text,
            reply_markup=get_tutorial_keyboard(1, user.language),
            edit=True
        )
        await state.set_state(TutorialState.STEP_1)

    except Exception as e:
        logger.error(f"Ошибка tutorial_step_1 для пользователя {callback.from_user.id}: {e}")
        await callback.message.edit_text("❌ Ошибка туториала. Переходим к игре...")
        await tutorial_complete_handler(callback, state)


@router.callback_query(F.data == "tutorial_step_2")
async def tutorial_step_2(callback: CallbackQuery, state: FSMContext):
    """Второй шаг туториала"""
    try:
        await callback.answer()

        user_id = callback.from_user.id
        user = await get_user(user_id)

        if not user:
            await callback.message.edit_text("❌ Ошибка: пользователь не найден")
            return

        step2_text = await get_text('tutorial_step_2', user_id)

        await send_formatted(
            callback,
            step2_text,
            reply_markup=get_tutorial_keyboard(2, user.language),
            edit=True
        )
        await state.set_state(TutorialState.STEP_2)

    except Exception as e:
        logger.error(f"Ошибка tutorial_step_2 для пользователя {callback.from_user.id}: {e}")
        await callback.message.edit_text("❌ Ошибка туториала. Переходим к игре...")
        await tutorial_complete_handler(callback, state)


@router.callback_query(F.data == "tutorial_step_3")
async def tutorial_step_3(callback: CallbackQuery, state: FSMContext):
    """Третий шаг туториала"""
    try:
        await callback.answer()

        user_id = callback.from_user.id
        user = await get_user(user_id)

        if not user:
            await callback.message.edit_text("❌ Ошибка: пользователь не найден")
            return

        step3_text = await get_text('tutorial_step_3', user_id)

        await send_formatted(
            callback,
            step3_text,
            reply_markup=get_tutorial_keyboard(3, user.language),
            edit=True
        )
        await state.set_state(TutorialState.STEP_3)

    except Exception as e:
        logger.error(f"Ошибка tutorial_step_3 для пользователя {callback.from_user.id}: {e}")
        await callback.message.edit_text("❌ Ошибка туториала. Переходим к игре...")
        await tutorial_complete_handler(callback, state)


@router.callback_query(F.data == "tutorial_complete")
async def tutorial_complete_handler(callback: CallbackQuery, state: FSMContext):
    """Завершение туториала"""
    try:
        user_id = callback.from_user.id

        # Завершаем туториал (дает бонусы)
        await complete_tutorial(user_id)

        # Получаем обновленные данные пользователя
        user = await get_user(user_id)
        if not user:
            await callback.message.edit_text("❌ Ошибка завершения туториала")
            return

        # Показываем сообщение о завершении
        complete_text = await get_text('tutorial_complete', user_id)
        await callback.message.edit_text(complete_text)

        # Пауза для чтения
        import asyncio
        await asyncio.sleep(2)

        # Переходим на остров
        entering_text = await get_text('entering_island', user_id,
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

    except Exception as e:
        logger.error(f"Ошибка завершения туториала для пользователя {callback.from_user.id}: {e}")
        await callback.message.edit_text("✅ Туториал завершен! Добро пожаловать на остров!")


@router.callback_query(F.data == "tutorial_skip")
async def tutorial_skip(callback: CallbackQuery, state: FSMContext):
    """Пропуск туториала"""
    try:
        await callback.answer("⚡ Туториал пропущен!")

        user_id = callback.from_user.id
        await complete_tutorial(user_id)

        user = await get_user(user_id)
        if not user:
            await callback.message.edit_text("❌ Ошибка пропуска туториала")
            return

        entering_text = await get_text('entering_island', user_id,
                                       level=user.level,
                                       energy=user.energy,
                                       ryabucks=user.ryabucks,
                                       rbtc=f"{user.rbtc:.2f}")

        await callback.message.edit_text("⚡ Туториал пропущен!")

        # Отправляем новое сообщение с островом
        await send_formatted(
            callback.message,
            entering_text,
            reply_markup=get_island_menu(user.language)
        )

        await state.set_state(MenuState.ON_ISLAND)

    except Exception as e:
        logger.error(f"Ошибка пропуска туториала для пользователя {callback.from_user.id}: {e}")
        await callback.message.edit_text("⚡ Туториал пропущен! Добро пожаловать на остров!")


@router.message(F.text.in_(["⚙️ Настройки", "📱 Поддержка", "🌍 Язык"]))
async def start_menu_buttons(message: Message, state: FSMContext):
    """Обработка кнопок стартового меню"""
    try:
        button_text = message.text

        if button_text == "⚙️ Настройки":
            settings_text = """⚙️ **Настройки**

🔧 Доступные настройки:
• 🌍 Смена языка (скоро)
• 🔔 Уведомления (скоро)
• 🎨 Темы оформления (скоро)

📱 Для изменения настроек обратитесь в поддержку."""
            await message.answer(settings_text, parse_mode="Markdown")

        elif button_text == "📱 Поддержка":
            support_text = """📱 **Техническая поддержка**

🆘 Нужна помощь?

📧 Напишите нам:
• Telegram: @support_ryabot
• Email: support@ryabotisland.com

🐛 Нашли баг?
• GitHub: /report_bug

⏰ Время ответа: до 24 часов"""
            await message.answer(support_text, parse_mode="Markdown")

        elif button_text == "🌍 Язык":
            language_text = """🌍 **Языковые настройки**

🗣️ Текущий язык: Русский

🔄 Смена языка:
В разработке... Скоро будет доступна смена на:
• 🇺🇸 English
• 🇺🇦 Українська
• 🇰🇿 Қазақша

📝 Хотите помочь с переводом? Напишите в поддержку!"""
            await message.answer(language_text, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Ошибка обработки кнопки стартового меню {message.text}: {e}")
        await message.answer("⚠️ Произошла ошибка. Попробуйте позже.")


# Команды для отладки и поддержки
@router.message(Command("help"))
async def help_command(message: Message):
    """Команда помощи"""
    help_text = """🆘 **Помощь по Ryabot Island**

🎮 **Основные команды:**
/start - Перезапуск бота
/help - Эта справка
/menu - Вернуться в главное меню

⚡ **Быстрые команды:**
/economy - Текущие цены
/claim - Собрать энергию
/gather - Собрать все (Premium)

🏝️ **Разделы игры:**
🏠 Ферма - Животные и постройки
🏢 Город - Здания и услуги  
👤 Житель - Ваш профиль
💼 Работа - Заработок денег
🎒 Рюкзак - Инвентарь
👥 Друзья - Реферальная система
🏆 Лидеры - Рейтинги игроков

📱 Нужна помощь? @support_ryabot"""

    await message.answer(help_text, parse_mode="Markdown")


@router.message(Command("menu"))
async def menu_command(message: Message, state: FSMContext):
    """Быстрое возвращение в главное меню"""
    user = await get_user(message.from_user.id)
    if user:
        await clear_user_state(user.user_id)
        await send_main_menu(message, user, state)
    else:
        await start_handler(message, state)


logger.info("✅ Start handler загружен (Supabase версия)")
