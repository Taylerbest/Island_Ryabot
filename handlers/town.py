# handlers/town.py
"""
Обработчик для раздела "Город"
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database.models import get_user
from keyboards.town import get_town_menu
from utils.texts import t
from utils.states import MenuState

router = Router()


@router.message(F.text.in_(["🏢 Город", "🏢 Town", "Город"]))
async def town_handler(message: Message, state: FSMContext):
    """Обработчик входа в город"""
    user_id = message.from_user.id
    user = await get_user(user_id)

    if not user:
        await message.answer("❗ Пожалуйста, используйте команду /start")
        return

    town_text = t("town_welcome", user.language,
                  level=user.level,
                  energy=user.energy,
                  ryabucks=user.ryabucks)

    await message.answer(
        text=town_text,
        reply_markup=get_town_menu(user.language)
    )
    await state.set_state(MenuState.ON_ISLAND)


# Обработчики для каждой кнопки города
@router.callback_query(F.data == "town_hall")
async def town_hall_handler(callback: CallbackQuery):
    """Ратуша"""
    await callback.message.answer("🏛️ Ратуша\n\nВ разработке...")
    await callback.answer()


@router.callback_query(F.data == "market")
async def market_handler(callback: CallbackQuery):
    """Рынок"""
    await callback.message.answer("🛒 Рынок\n\nВ разработке...")
    await callback.answer()


@router.callback_query(F.data == "ryabank")
async def ryabank_handler(callback: CallbackQuery):
    """Рябанк"""
    await callback.message.answer("🏦 Рябанк\n\nВ разработке...")
    await callback.answer()


@router.callback_query(F.data == "products")
async def products_handler(callback: CallbackQuery):
    """Продукты"""
    await callback.message.answer("🏪 Продукты\n\nВ разработке...")
    await callback.answer()


@router.callback_query(F.data == "pawnshop")
async def pawnshop_handler(callback: CallbackQuery):
    """Ломбард"""
    await callback.message.answer("💫 Ломбард\n\nВ разработке...")
    await callback.answer()


@router.callback_query(F.data == "tavern1")
async def tavern1_handler(callback: CallbackQuery):
    """Таверна"""
    await callback.message.answer("🍻 Таверна\n\nВ разработке...")
    await callback.answer()


@router.callback_query(F.data == "academy")
async def academy_handler(callback: CallbackQuery):
    """Академия"""
    await callback.message.answer("🏫 Академия\n\nВ разработке...")
    await callback.answer()


@router.callback_query(F.data == "entertainment")
async def entertainment_handler(callback: CallbackQuery):
    """Развлечения"""
    await callback.message.answer("🎡 Развлечения\n\nВ разработке...")
    await callback.answer()


@router.callback_query(F.data == "realestate")
async def realestate_handler(callback: CallbackQuery):
    """Недвижка"""
    await callback.message.answer("🏢 Недвижка\n\nВ разработке...")
    await callback.answer()


@router.callback_query(F.data == "vet_clinic")
async def vet_clinic_handler(callback: CallbackQuery):
    """Ветклиника"""
    await callback.message.answer("❤️‍🩹 Ветклиника\n\nВ разработке...")
    await callback.answer()


@router.callback_query(F.data == "construction")
async def construction_handler(callback: CallbackQuery):
    """Строй-Сам - ИЗМЕНЕНО"""
    await callback.message.answer("🏗️ Строй-Сам\n\nВ разработке...")
    await callback.answer()


@router.callback_query(F.data == "hospital")
async def hospital_handler(callback: CallbackQuery):
    """Больница"""
    await callback.message.answer("🏥 Больница\n\nВ разработке...")
    await callback.answer()


@router.callback_query(F.data == "quantum_hub")
async def quantum_hub_handler(callback: CallbackQuery):
    """КвантХаб"""
    await callback.message.answer("💻 КвантХаб\n\nВ разработке...")
    await callback.answer()


@router.callback_query(F.data == "cemetery")
async def cemetery_handler(callback: CallbackQuery):
    """Кладбище"""
    await callback.message.answer("🪦 Кладбище\n\nВ разработке...")
    await callback.answer()
