"""
Обработчик для Академии - найм и обучение рабочих
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database.models import (
    get_user, hire_worker, can_hire_worker, get_hired_workers_count,
    start_training, get_active_trainings, complete_trainings,
    get_training_slots_info, get_specialists_count, create_academy_tables
)
from keyboards.academy import (
    get_academy_menu, get_labor_exchange_menu, get_training_menu,
    get_profession_selection_menu, get_training_class_menu
)

router = Router()


@router.callback_query(F.data == "academy")
async def academy_main(callback: CallbackQuery, state: FSMContext):
    """Главное меню Академии"""
    user_id = callback.from_user.id
    user = await get_user(user_id)

    # Инициализируем таблицы при первом входе
    await create_academy_tables()

    # Завершаем готовые обучения
    completed_count = await complete_trainings(user_id)
    if completed_count > 0:
        await callback.answer(f"🎓 Обучение завершено! Выпустилось специалистов: {completed_count}", show_alert=True)

    workers_count = await get_hired_workers_count(user_id)
    specialists_count = await get_specialists_count(user_id)
    active_trainings = await get_active_trainings(user_id)

    academy_text = (
        "🏫 <b>АВИАНСКАЯ АКАДЕМИЯ</b>\n\n"
        "📜 <i>\"Шепчущие залы, где мозолистые руки учатся забытым ремеслам. "
        "Здесь, усталые работяги становятся ремесленниками — их пот "
        "обменивается на точность каменщиков, интуицию архитекторов, "
        "терпение строителей мостов. Доски гудят уравнениями, мастерские "
        "пахнут сосновой смолой и амбициями.\"</i>\n\n"
        f"🙍‍♂️ <b>Разнорабочих:</b> {workers_count.get('laborer', 0)}\n"
        f"📚 <b>Обучается:</b> {len(active_trainings)}\n"
        f"🎓 <b>Специалистов:</b> {sum(specialists_count.values())}\n\n"
        "🎯 Выберите действие:"
    )

    await callback.message.edit_text(
        text=academy_text,
        reply_markup=get_academy_menu(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "labor_exchange")
async def labor_exchange(callback: CallbackQuery):
    """Биржа труда - найм разнорабочих"""
    user_id = callback.from_user.id
    user = await get_user(user_id)

    can_hire, reason, remaining = await can_hire_worker(user_id)
    workers_count = await get_hired_workers_count(user_id)
    total_workers = sum(workers_count.values())

    # Стоимость найма (процент команды)
    hire_cost_percent = 30 + (total_workers * 5)

    # Статус найма
    if can_hire:
        status = "✅ Можно нанять рабочего"
    elif reason == "cooldown":
        hours = remaining // 3600
        minutes = (remaining % 3600) // 60
        status = f"⏰ Следующий найм через: {hours}ч {minutes}мин"
    else:
        status = "🚫 Достигнут дневной лимит"

    exchange_text = (
        "🛠️ <b>БИРЖА ТРУДА</b>\n\n"
        "💼 <i>\"Ищите работников среди островитян — но поторопитесь, "
        "хорошие долго не задерживаются!\"</i>\n\n"
        f"⚠️ <b>Внимание:</b> Стоимость найма работника увеличивается "
        f"на 5💵 из-за нехватки персонала на острове.\n\n"
        f"💰 <b>Цена найма:</b> (30 + %w_team%) 💵\n"
        f"🙍‍♂️ <b>У вас разнорабочих:</b> {workers_count.get('laborer', 0)}\n\n"
        f"🔄 {status}\n\n"
        "💡 После найма следующий рабочий будет доступен через 24 часа "
        "(можно пропустить за 💠RBTC)."
    )

    await callback.message.edit_text(
        text=exchange_text,
        reply_markup=get_labor_exchange_menu(can_hire, workers_count.get('laborer', 0)),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("hire_slot_"))
async def hire_slot(callback: CallbackQuery):
    """Нанять разнорабочего из конкретного слота"""
    user_id = callback.from_user.id
    slot_type = callback.data.split("_")[2]  # free, business, quantum

    # TODO: Проверить доступность слота в зависимости от типа
    # if slot_type == "business" and not user.has_business_license:
    #     await callback.answer("❌ Нужна бизнес-лицензия!", show_alert=True)
    #     return

    success, message = await hire_worker(user_id)

    await callback.answer(message, show_alert=True)

    if success:
        # Обновляем меню
        await labor_exchange(callback)


@router.callback_query(F.data == "info_free_slots")
async def info_free_slots(callback: CallbackQuery):
    """Информация о бесплатных слотах"""
    info_text = (
        "🆓 <b>БЕСПЛАТНЫЕ СЛОТЫ</b>\n\n"
        "Доступно всем игрокам без дополнительных условий.\n\n"
        "📊 <b>Лимит:</b> 3 рабочих\n"
        "💰 <b>Стоимость:</b> (30 + %w_team%) 💵\n"
        "⏰ <b>Cooldown:</b> 24 часа между наймом"
    )
    await callback.answer(info_text, show_alert=True)


@router.callback_query(F.data == "info_business_slots")
async def info_business_slots(callback: CallbackQuery):
    """Информация о слотах бизнес-лицензии"""
    info_text = (
        "📜 <b>СЛОТЫ БИЗНЕС-ЛИЦЕНЗИИ</b>\n\n"
        "Требуется активная бизнес-лицензия.\n\n"
        "📊 <b>Лимит:</b> +3 дополнительных рабочих\n"
        "💰 <b>Стоимость:</b> (30 + %w_team%) 💵\n"
        "⏰ <b>Cooldown:</b> 24 часа между наймом\n\n"
        "🔑 Купите бизнес-лицензию для разблокировки!"
    )
    await callback.answer(info_text, show_alert=True)


@router.callback_query(F.data == "info_quantum_slots")
async def info_quantum_slots(callback: CallbackQuery):
    """Информация о слотах Quantum-Pass"""
    info_text = (
        "🪪 <b>СЛОТЫ QUANTUM-PASS</b>\n\n"
        "Требуется активный Quantum-Pass.\n\n"
        "📊 <b>Лимит:</b> +3 дополнительных рабочих\n"
        "💰 <b>Стоимость:</b> (30 + %w_team%) 💵\n"
        "⏰ <b>Cooldown:</b> 24 часа между наймом\n\n"
        "✨ Купите Quantum-Pass для разблокировки!"
    )
    await callback.answer(info_text, show_alert=True)


@router.callback_query(F.data == "expert_courses")
async def expert_courses(callback: CallbackQuery):
    """Экспертные курсы - выбор профессии"""
    user_id = callback.from_user.id

    workers_count = await get_hired_workers_count(user_id)
    slots_info = await get_training_slots_info(user_id)

    courses_text = (
        "🎓 <b>ЭКСПЕРТНЫЕ КУРСЫ</b>\n\n"
        "📚 <i>\"Превратите простых работяг в опытных специалистов через "
        "суровое обучение в Авианской Академии. Каждый курс требует времени, "
        "ресурсов и щепотку квантовой удачи.\"</i>\n\n"
        f"🙍‍♂️ <b>Разнорабочих доступно:</b> {workers_count.get('laborer', 0)}\n"
        f"📖 <b>Учебных мест:</b> {slots_info['used']}/{slots_info['total']}\n\n"
        "🎯 <b>Выберите профессию для обучения:</b>"
    )

    await callback.message.edit_text(
        text=courses_text,
        reply_markup=get_profession_selection_menu(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("train_"))
async def train_profession(callback: CallbackQuery):
    """Начать обучение профессии"""
    user_id = callback.from_user.id
    profession = callback.data.split("_")[1]

    success, message = await start_training(user_id, profession)

    await callback.answer(message, show_alert=True)

    if success:
        # Возвращаемся к выбору профессий
        await expert_courses(callback)


@router.callback_query(F.data == "training_class")
async def training_class(callback: CallbackQuery):
    """Учебный класс - просмотр обучающихся"""
    user_id = callback.from_user.id

    active_trainings = await get_active_trainings(user_id)
    slots_info = await get_training_slots_info(user_id)

    if not active_trainings:
        class_text = (
            "🏫 <b>УЧЕБНЫЙ КЛАСС</b>\n\n"
            "📝 Сейчас никто не обучается.\n"
            "Отправьте разнорабочих на экспертные курсы!"
        )
    else:
        class_text = (
            "🏫 <b>УЧЕБНЫЙ КЛАСС</b>\n\n"
            f"📖 <b>Занято мест:</b> {slots_info['used']}/{slots_info['total']}\n\n"
            "👨‍🎓 <b>Обучаются:</b>\n"
        )

        profession_icons = {
            'builder': '👷', 'farmer': '👨‍🌾', 'woodman': '🧑‍🚒',
            'soldier': '💂', 'fisherman': '🎣', 'scientist': '👨‍🔬',
            'cook': '👨‍🍳', 'teacher': '👨‍🏫', 'doctor': '🧑‍⚕️'
        }

        profession_names = {
            'builder': 'Строитель', 'farmer': 'Фермер', 'woodman': 'Лесник',
            'soldier': 'Солдат', 'fisherman': 'Рыбак', 'scientist': 'Ученый',
            'cook': 'Повар', 'teacher': 'Учитель', 'doctor': 'Доктор'
        }

        for i, training in enumerate(active_trainings, 1):
            icon = profession_icons.get(training['type'], '👤')
            name = profession_names.get(training['type'], 'Специалист')
            class_text += f"{i}. {icon} {name} - ⏰ {training['time_left']}\n"

        class_text += "\n💡 Обучение завершится автоматически!"

    await callback.message.edit_text(
        text=class_text,
        reply_markup=get_training_class_menu(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_academy")
async def back_to_academy(callback: CallbackQuery, state: FSMContext):
    """Вернуться в главное меню Академии"""
    await academy_main(callback, state)


@router.callback_query(F.data == "skip_hire_cooldown")
async def skip_hire_cooldown(callback: CallbackQuery):
    """Пропустить кулдаун найма за RBTC"""
    # TODO: Реализовать пропуск за RBTC
    await callback.answer("🚧 Функция в разработке!", show_alert=True)


@router.callback_query(F.data == "boost_training")
async def boost_training(callback: CallbackQuery):
    """Ускорить обучение за RBTC"""
    # TODO: Реализовать ускорение обучения
    await callback.answer("🚧 Функция в разработке!", show_alert=True)


@router.callback_query(F.data == "info_header")
async def info_header(callback: CallbackQuery):
    """Заглушка для заголовка"""
    await callback.answer()


@router.callback_query(F.data.startswith("slot_header_"))
async def slot_header(callback: CallbackQuery):
    """Заглушка для заголовков слотов"""
    await callback.answer()


@router.callback_query(F.data.startswith("cooldown_"))
async def cooldown_info(callback: CallbackQuery):
    """Информация о слоте на кулдауне"""
    await callback.answer("⏳ Этот слот на 24-часовом кулдауне. Используйте Boost для пропуска!", show_alert=True)
