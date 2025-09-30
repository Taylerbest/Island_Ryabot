from aiogram import Router, F
from aiogram.types import CallbackQuery
from utils.message_helper import send_formatted
from database.models import (get_user, hire_worker, can_hire_worker,
                             get_hired_workers_count, start_training,
                             get_active_trainings, complete_trainings,
                             get_training_slots_info, get_specialists_count)
from keyboards.academy import (get_academy_menu, get_labor_exchange_menu,
                               get_profession_selection_menu, get_training_class_menu)
from utils.texts import t

router = Router()


@router.callback_query(F.data == "academy")
async def academy_main(callback: CallbackQuery):
    try:
        await callback.answer()  # ← СРАЗУ ОТВЕЧАЕМ
    except Exception:
        pass

    user_id = callback.from_user.id
    user = await get_user(user_id)

    completed_count = await complete_trainings(user_id)
    if completed_count > 0:
        try:
            await callback.answer(f"🎓 Обучение завершено! Выпустилось специалистов: {completed_count}", show_alert=True)
        except:
            pass

    workers_count = await get_hired_workers_count(user_id)
    specialists_count = await get_specialists_count(user_id)
    active_trainings = await get_active_trainings(user_id)

    academy_text = t(
        "academy_welcome", user.language,
        laborers=workers_count.get("laborer", 0),
        training=len(active_trainings),
        specialists=sum(specialists_count.values())
    )

    await send_formatted(
        callback,
        academy_text,
        reply_markup=get_academy_menu(),
        edit=True
    )


@router.callback_query(F.data == "labor_exchange")
async def labor_exchange(callback: CallbackQuery):
    try:
        await callback.answer()
    except Exception:
        pass

    user_id = callback.from_user.id
    user = await get_user(user_id)

    can_hire, reason, remaining = await can_hire_worker(user_id)
    workers_count = await get_hired_workers_count(user_id)

    if can_hire:
        status = t("hire_status_ready", user.language)
    elif reason == "cooldown":
        hours = remaining // 3600
        minutes = (remaining % 3600) // 60
        status = t("hire_status_cooldown", user.language, hours=hours, minutes=minutes)
    else:
        status = t("hire_status_limit", user.language)

    exchange_text = t(
        "labor_exchange", user.language,
        laborers=workers_count.get("laborer", 0),
        status=status
    )

    await send_formatted(
        callback,
        exchange_text,
        reply_markup=get_labor_exchange_menu(can_hire, sum(workers_count.values())),
        edit=True
    )


@router.callback_query(F.data.startswith("hire_slot_"))
async def hire_slot(callback: CallbackQuery):
    user_id = callback.from_user.id
    success, message = await hire_worker(user_id)

    try:
        await callback.answer(message, show_alert=True)
    except:
        pass

    if success:
        await labor_exchange(callback)


@router.callback_query(F.data == "expert_courses")
async def expert_courses(callback: CallbackQuery):
    try:
        await callback.answer()
    except Exception:
        pass

    user_id = callback.from_user.id
    user = await get_user(user_id)

    workers_count = await get_hired_workers_count(user_id)
    slots_info = await get_training_slots_info(user_id)

    courses_text = t(
        "expert_courses", user.language,
        laborers=workers_count.get("laborer", 0),
        slots_used=slots_info["used"],
        slots_total=slots_info["total"]
    )

    await send_formatted(
        callback,
        courses_text,
        reply_markup=get_profession_selection_menu(),
        edit=True
    )


@router.callback_query(F.data.startswith("train_"))
async def train_profession(callback: CallbackQuery):
    user_id = callback.from_user.id
    profession = callback.data.split("_")[1]

    success, message = await start_training(user_id, profession)

    try:
        await callback.answer(message, show_alert=True)
    except:
        pass

    if success:
        await expert_courses(callback)


@router.callback_query(F.data == "training_class")
async def training_class(callback: CallbackQuery):
    try:
        await callback.answer()
    except Exception:
        pass

    user_id = callback.from_user.id
    user = await get_user(user_id)

    active_trainings = await get_active_trainings(user_id)
    slots_info = await get_training_slots_info(user_id)

    if not active_trainings:
        class_text = t("training_class_empty", user.language)
    else:
        profession_icons = {
            "builder": "👷", "farmer": "👨‍🌾", "woodman": "🧑‍🚒",
            "soldier": "💂", "fisherman": "🎣", "scientist": "👨‍🔬",
            "cook": "👨‍🍳", "teacher": "👨‍🏫", "doctor": "🧑‍⚕️"
        }
        profession_names = {
            "builder": "Строитель", "farmer": "Фермер", "woodman": "Лесник",
            "soldier": "Солдат", "fisherman": "Рыбак", "scientist": "Ученый",
            "cook": "Повар", "teacher": "Учитель", "doctor": "Доктор"
        }
        training_list = ""
        for i, training in enumerate(active_trainings, 1):
            icon = profession_icons.get(training["type"], "👤")
            name = profession_names.get(training["type"], "Специалист")
            training_list += f"{i}. {icon} {name} - ⏰ {training['time_left']}\n"

        class_text = t(
            "training_class_active", user.language,
            slots_used=slots_info["used"],
            slots_total=slots_info["total"],
            training_list=training_list.strip()
        )

    await send_formatted(
        callback,
        class_text,
        reply_markup=get_training_class_menu(),
        edit=True
    )


@router.callback_query(F.data == "back_to_academy")
async def back_to_academy(callback: CallbackQuery):
    try:
        await callback.answer()
    except Exception:
        pass
    await academy_main(callback)
