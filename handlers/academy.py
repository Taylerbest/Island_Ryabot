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
    get_academy_menu, get_labor_exchange_menu,
    get_profession_selection_menu, get_training_class_menu
)
from utils.texts import t

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

    academy_text = t('academy_welcome', user.language,
        laborers=workers_count.get('laborer', 0),
        training=len(active_trainings),
        specialists=sum(specialists_count.values())
    )

    await callback.message.edit_text(
        text=academy_text,
        reply_markup=get_academy_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "labor_exchange")
async def labor_exchange(callback: CallbackQuery):
    """Биржа труда - найм разнорабочих"""
    user_id = callback.from_user.id
    user = await get_user(user_id)

    can_hire, reason, remaining = await can_hire_worker(user_id)
    workers_count = await get_hired_workers_count(user_id)

    # Статус найма
    if can_hire:
        status = t('hire_status_ready', user.language)
    elif reason == "cooldown":
        hours = remaining // 3600
        minutes = (remaining % 3600) // 60
        status = t('hire_status_cooldown', user.language, hours=hours, minutes=minutes)
    else:
        status = t('hire_status_limit', user.language)

    exchange_text = t('labor_exchange', user.language,
        laborers=workers_count.get('laborer', 0),
        status=status
    )

    await callback.message.edit_text(
        text=exchange_text,
        reply_markup=get_labor_exchange_menu(can_hire, workers_count.get('laborer', 0)),
        parse_mode="Markdown"
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
    user = await get_user(callback.from_user.id)
    info_text = t('info_free_slots', user.language)
    await callback.answer(info_text, show_alert=True)


@router.callback_query(F.data == "info_business_slots")
async def info_business_slots(callback: CallbackQuery):
    """Информация о слотах бизнес-лицензии"""
    user = await get_user(callback.from_user.id)
    info_text = t('info_business_slots', user.language)
    await callback.answer(info_text, show_alert=True)


@router.callback_query(F.data == "info_quantum_slots")
async def info_quantum_slots(callback: CallbackQuery):
    """Информация о слотах Quantum-Pass"""
    user = await get_user(callback.from_user.id)
    info_text = t('info_quantum_slots', user.language)
    await callback.answer(info_text, show_alert=True)


@router.callback_query(F.data == "expert_courses")
async def expert_courses(callback: CallbackQuery):
    """Экспертные курсы - выбор профессии"""
    user_id = callback.from_user.id
    user = await get_user(user_id)

    workers_count = await get_hired_workers_count(user_id)
    slots_info = await get_training_slots_info(user_id)

    courses_text = t('expert_courses', user.language,
        laborers=workers_count.get('laborer', 0),
        slots_used=slots_info['used'],
        slots_total=slots_info['total']
    )

    await callback.message.edit_text(
        text=courses_text,
        reply_markup=get_profession_selection_menu(),
        parse_mode="Markdown"
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
    user = await get_user(user_id)

    active_trainings = await get_active_trainings(user_id)
    slots_info = await get_training_slots_info(user_id)

    if not active_trainings:
        class_text = t('training_class_empty', user.language)
    else:
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

        training_list = ""
        for i, training in enumerate(active_trainings, 1):
            icon = profession_icons.get(training['type'], '👤')
            name = profession_names.get(training['type'], 'Специалист')
            training_list += f"{i}. {icon} {name} - ⏰ {training['time_left']}\n"

        class_text = t('training_class_active', user.language,
            slots_used=slots_info['used'],
            slots_total=slots_info['total'],
            training_list=training_list.strip()
        )

    await callback.message.edit_text(
        text=class_text,
        reply_markup=get_training_class_menu(),
        parse_mode="Markdown"
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
    user = await get_user(callback.from_user.id)
    await callback.answer(t('cooldown_slot', user.language), show_alert=True)
