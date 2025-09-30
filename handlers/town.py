"""
Обработчик для города
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database.models import get_user
from keyboards.town import get_town_menu
from utils.texts import t
from utils.states import MenuState

router = Router()


# Обработчик текстовых сообщений для входа в город
@router.message(F.text.in_(["🏢 Город", "Town", "🏛️ Город"]))
async def town_handler(message: Message, state: FSMContext):
    """Вход в город через текстовое меню"""
    user_id = message.from_user.id
    user = await get_user(user_id)

    if not user:
        await message.answer("⚠️ Сначала зарегистрируйтесь, нажав /start")
        return

    town_text = t(
        "town_welcome",
        user.language,
        level=user.level,
        energy=user.energy,
        ryabucks=user.ryabucks
    )

    await message.answer(
        text=town_text,
        reply_markup=get_town_menu(user.language)
    )
    await state.set_state(MenuState.ON_ISLAND)


# НОВЫЙ ОБРАБОТЧИК - для callback-кнопок возврата в город
@router.callback_query(F.data == "town")
async def town_callback_handler(callback: CallbackQuery, state: FSMContext):
    """Возврат в город через callback-кнопку"""
    user_id = callback.from_user.id
    user = await get_user(user_id)

    if not user:
        await callback.answer("⚠️ Ошибка: пользователь не найден")
        return

    town_text = t(
        "town_welcome",
        user.language,
        level=user.level,
        energy=user.energy,
        ryabucks=user.ryabucks
    )

    await callback.message.edit_text(
        text=town_text,
        reply_markup=get_town_menu(user.language)
    )
    await state.set_state(MenuState.ON_ISLAND)
    await callback.answer()


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
