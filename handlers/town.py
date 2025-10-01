"""
Обработчик для города
"""
"""
Обработчик для города
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
# ИСПРАВЛЕНИЕ: импорт из правильного модуля
from database.models import get_user, create_user, update_user_resources, get_island_stats
from keyboards.town import get_town_menu
from utils.texts import t
from utils.states import MenuState
from utils.message_helper import send_formatted

router = Router()

@router.message(F.text.in_(["🏢 Город", "Town", "🏛️ Город"]))
async def town_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user = await get_user(user_id)

    if not user:
        await message.answer("⚠️ Сначала зарегистрируйтесь, нажав /start")
        return

    # ИСПРАВЛЕНИЕ: fallback значения для t()
    town_text = t(
        "town_welcome",
        user.language,
        level=user.level,
        energy=user.energy,
        ryabucks=user.ryabucks,
        default="🏢 **Добро пожаловать в город!**\n\n🏛️ Центр цивилизации на острове.\n\n👤 **Ваш статус:**\n⭐ Уровень: {level}\n🔋 Энергия: {energy}/100\n💵 Рябаксы: {ryabucks}\n\n🏗️ Выберите здание для посещения:"
    )

    await send_formatted(
        message,
        town_text,
        reply_markup=get_town_menu(user.language)
    )
    await state.set_state(MenuState.ON_ISLAND)

@router.callback_query(F.data == "town")
async def town_callback_handler(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user = await get_user(user_id)

    if not user:
        await callback.answer("⚠️ Ошибка: пользователь не найден")
        return

    # ИСПРАВЛЕНИЕ: fallback значения для t()
    town_text = t(
        "town_welcome",
        user.language,
        level=user.level,
        energy=user.energy,
        ryabucks=user.ryabucks,
        default="🏢 **Добро пожаловать в город!**\n\n🏛️ Центр цивилизации на острове.\n\n👤 **Ваш статус:**\n⭐ Уровень: {level}\n🔋 Энергия: {energy}/100\n💵 Рябаксы: {ryabucks}\n\n🏗️ Выберите здание для посещения:"
    )

    await send_formatted(
        callback,
        town_text,
        reply_markup=get_town_menu(user.language),
        edit=True
    )
    await state.set_state(MenuState.ON_ISLAND)
    await callback.answer()

# Остальные обработчики остаются как есть...



# Остальные обработчики города...
@router.callback_query(F.data == "town_hall")
async def town_hall_handler(callback: CallbackQuery):
    await callback.message.answer("🏛️ Ратуша - в разработке...")
    await callback.answer()


@router.callback_query(F.data == "market")
async def market_handler(callback: CallbackQuery):
    await callback.message.answer("🛒 Рынок - в разработке...")
    await callback.answer()


@router.callback_query(F.data == "ryabank")
async def ryabank_handler(callback: CallbackQuery):
    await callback.message.answer("🏦 РяБанк - в разработке...")
    await callback.answer()


@router.callback_query(F.data == "products")
async def products_handler(callback: CallbackQuery):
    await callback.message.answer("🏭 Производство - в разработке...")
    await callback.answer()


@router.callback_query(F.data == "pawnshop")
async def pawnshop_handler(callback: CallbackQuery):
    await callback.message.answer("💎 Ломбард - в разработке...")
    await callback.answer()


@router.callback_query(F.data == "tavern1")
async def tavern1_handler(callback: CallbackQuery):
    await callback.message.answer("🍺 Таверна - в разработке...")
    await callback.answer()


# ВАЖНО: Удалите старый обработчик academy, т.к. он теперь в отдельном файле
# @router.callback_query(F.data == "academy")
# async def academy_handler(callback: CallbackQuery):
#     await callback.message.answer("🎓 Академия - в разработке...")
#     await callback.answer()


@router.callback_query(F.data == "entertainment")
async def entertainment_handler(callback: CallbackQuery):
    await callback.message.answer("🎭 Развлечения - в разработке...")
    await callback.answer()


@router.callback_query(F.data == "real_estate")
async def real_estate_handler(callback: CallbackQuery):
    await callback.message.answer("🏘️ Недвижимость - в разработке...")
    await callback.answer()


@router.callback_query(F.data == "vet_clinic")
async def vet_clinic_handler(callback: CallbackQuery):
    await callback.message.answer("🐾 Ветклиника - в разработке...")
    await callback.answer()


@router.callback_query(F.data == "construction")
async def construction_handler(callback: CallbackQuery):
    await callback.message.answer("🏗️ Строительство - в разработке...")
    await callback.answer()


@router.callback_query(F.data == "hospital")
async def hospital_handler(callback: CallbackQuery):
    await callback.message.answer("🏥 Больница - в разработке...")
    await callback.answer()


@router.callback_query(F.data == "quantum_hub")
async def quantum_hub_handler(callback: CallbackQuery):
    await callback.message.answer("⚛️ Квантовый хаб - в разработке...")
    await callback.answer()


@router.callback_query(F.data == "cemetery")
async def cemetery_handler(callback: CallbackQuery):
    await callback.message.answer("⚰️ Кладбище - в разработке...")
    await callback.answer()
