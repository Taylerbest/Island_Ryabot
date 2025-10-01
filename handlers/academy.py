"""
Обработчик Академии для Ryabot Island v2.0
Полная поддержка Supabase архитектуры с улучшенной обработкой ошибок
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from utils.message_helper import send_formatted
from database.models import (
    get_user, hire_worker, can_hire_worker,
    get_hired_workers_count, start_training,
    get_active_trainings, complete_trainings,
    get_training_slots_info, get_specialists_count
)
from keyboards.academy import (
    get_academy_menu, get_labor_exchange_menu,
    get_profession_selection_menu, get_training_class_menu
)
from utils.texts import get_text, t
from config import config
import logging

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data == "academy")
async def academy_main(callback: CallbackQuery):
    """Главное меню Академии с автоматическим завершением обучений"""
    try:
        await callback.answer()

        user_id = callback.from_user.id
        user = await get_user(user_id)

        if not user:
            await callback.message.edit_text("❌ Ошибка: пользователь не найден")
            return

        # Автоматически завершаем готовые обучения
        completed_count = await complete_trainings(user_id)
        if completed_count > 0:
            try:
                completion_message = await get_text(
                    'training_completed_alert', user_id,
                    count=completed_count
                )
                await callback.answer(completion_message, show_alert=True)
            except Exception as e:
                logger.warning(f"Ошибка показа уведомления о завершении обучения: {e}")
                await callback.answer(f"🎓 Обучение завершено! Выпустилось специалистов: {completed_count}",
                                      show_alert=True)

        # Получаем актуальную информацию
        workers_count = await get_hired_workers_count(user_id)
        specialists_count = await get_specialists_count(user_id)
        active_trainings = await get_active_trainings(user_id)

        # Форматируем сообщение академии
        academy_text = await get_text(
            "academy_welcome", user_id,
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

    except Exception as e:
        logger.error(f"Ошибка в academy_main для пользователя {callback.from_user.id}: {e}")
        await callback.message.edit_text("⚠️ Произошла ошибка в Академии. Попробуйте позже.")


@router.callback_query(F.data == "labor_exchange")
async def labor_exchange(callback: CallbackQuery):
    """Биржа труда с детальной информацией о найме"""
    try:
        await callback.answer()

        user_id = callback.from_user.id
        user = await get_user(user_id)

        if not user:
            await callback.message.edit_text("❌ Ошибка: пользователь не найден")
            return

        # Проверяем возможность найма
        can_hire, reason, remaining = await can_hire_worker(user_id)
        workers_count = await get_hired_workers_count(user_id)
        total_workers = sum(workers_count.values())

        # Формируем статус найма
        if can_hire:
            hire_cost = config.game.get_hire_cost(total_workers)
            status = await get_text("hire_status_ready", user_id, cost=hire_cost)
        elif reason == "cooldown":
            hours = remaining // 3600
            minutes = (remaining % 3600) // 60
            status = await get_text("hire_status_cooldown", user_id, hours=hours, minutes=minutes)
        elif reason == "limit_reached":
            status = await get_text("hire_status_limit", user_id)
        else:
            status = await get_text("hire_status_unknown", user_id)

        # Отправляем сообщение биржи труда
        exchange_text = await get_text(
            "labor_exchange", user_id,
            laborers=workers_count.get("laborer", 0),
            status=status,
            total_workers=total_workers
        )

        await send_formatted(
            callback,
            exchange_text,
            reply_markup=get_labor_exchange_menu(can_hire, total_workers),
            edit=True
        )

    except Exception as e:
        logger.error(f"Ошибка в labor_exchange для пользователя {callback.from_user.id}: {e}")
        await callback.message.edit_text("⚠️ Ошибка биржи труда. Попробуйте позже.")


@router.callback_query(F.data.startswith("hire_slot_"))
async def hire_slot(callback: CallbackQuery):
    """Обработка найма рабочего с детальной обратной связью"""
    try:
        user_id = callback.from_user.id
        slot_data = callback.data.split("_")

        # Извлекаем информацию о слоте
        if len(slot_data) >= 3:
            slot_type = slot_data[2]  # free, business, quantum
            slot_index = slot_data[3] if len(slot_data) > 3 else "0"
        else:
            slot_type = "free"
            slot_index = "0"

        logger.info(f"Попытка найма пользователем {user_id}, слот {slot_type}_{slot_index}")

        # Выполняем найм
        success, message = await hire_worker(user_id)

        # Показываем результат пользователю
        await callback.answer(message, show_alert=True)

        # Если найм успешен, обновляем интерфейс
        if success:
            # Ждем небольшую паузу для обновления данных в БД
            import asyncio
            await asyncio.sleep(0.1)
            await labor_exchange(callback)
        else:
            # При неудаче просто показываем ошибку, интерфейс не меняем
            logger.warning(f"Неудачный найм пользователем {user_id}: {message}")

    except Exception as e:
        logger.error(f"Ошибка hire_slot для пользователя {callback.from_user.id}: {e}")
        await callback.answer("⚠️ Произошла ошибка при найме. Попробуйте позже.", show_alert=True)


@router.callback_query(F.data == "expert_courses")
async def expert_courses(callback: CallbackQuery):
    """Экспертные курсы с проверкой доступности"""
    try:
        await callback.answer()

        user_id = callback.from_user.id
        user = await get_user(user_id)

        if not user:
            await callback.message.edit_text("❌ Ошибка: пользователь не найден")
            return

        # Получаем информацию для курсов
        workers_count = await get_hired_workers_count(user_id)
        slots_info = await get_training_slots_info(user_id)

        courses_text = await get_text(
            "expert_courses", user_id,
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

    except Exception as e:
        logger.error(f"Ошибка в expert_courses для пользователя {callback.from_user.id}: {e}")
        await callback.message.edit_text("⚠️ Ошибка экспертных курсов. Попробуйте позже.")


@router.callback_query(F.data.startswith("train_"))
async def train_profession(callback: CallbackQuery):
    """Обработка начала обучения профессии"""
    try:
        user_id = callback.from_user.id
        profession = callback.data.split("_")[1]

        logger.info(f"Запуск обучения {profession} для пользователя {user_id}")

        # Запускаем обучение
        success, message = await start_training(user_id, profession)

        # Показываем результат
        await callback.answer(message, show_alert=True)

        # Если обучение началось, обновляем интерфейс
        if success:
            # Небольшая пауза для обновления БД
            import asyncio
            await asyncio.sleep(0.1)
            await expert_courses(callback)
        else:
            logger.warning(f"Неудачное обучение {profession} для пользователя {user_id}: {message}")

    except Exception as e:
        logger.error(f"Ошибка train_profession для пользователя {callback.from_user.id}: {e}")
        await callback.answer("⚠️ Произошла ошибка при запуске обучения. Попробуйте позже.", show_alert=True)


@router.callback_query(F.data == "training_class")
async def training_class(callback: CallbackQuery):
    """Учебный класс с активными обучениями"""
    try:
        await callback.answer()

        user_id = callback.from_user.id
        user = await get_user(user_id)

        if not user:
            await callback.message.edit_text("❌ Ошибка: пользователь не найден")
            return

        active_trainings = await get_active_trainings(user_id)
        slots_info = await get_training_slots_info(user_id)

        if not active_trainings:
            class_text = await get_text("training_class_empty", user_id)
        else:
            # Словари для отображения профессий
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

            # Формируем список обучающихся
            training_list = ""
            for i, training in enumerate(active_trainings, 1):
                icon = profession_icons.get(training["type"], "👤")
                name = profession_names.get(training["type"], "Специалист")
                training_list += f"{i}. {icon} {name} - ⏰ {training['time_left']}\n"

            class_text = await get_text(
                "training_class_active", user_id,
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

    except Exception as e:
        logger.error(f"Ошибка в training_class для пользователя {callback.from_user.id}: {e}")
        await callback.message.edit_text("⚠️ Ошибка учебного класса. Попробуйте позже.")


@router.callback_query(F.data == "back_to_academy")
async def back_to_academy(callback: CallbackQuery):
    """Возврат в главное меню Академии"""
    try:
        await callback.answer()
        await academy_main(callback)
    except Exception as e:
        logger.error(f"Ошибка back_to_academy для пользователя {callback.from_user.id}: {e}")
        await callback.answer("⚠️ Ошибка возврата в Академию", show_alert=True)


# Обработчики информационных кнопок (для слотов найма)
@router.callback_query(F.data.in_(["info_header", "info_free_slots", "info_business_slots", "info_quantum_slots"]))
async def info_handlers(callback: CallbackQuery):
    """Информационные всплывающие подсказки"""
    try:
        info_key = callback.data.replace("info_", "")

        if info_key == "header":
            message = "📋 Слоты найма рабочих"
        elif info_key == "free_slots":
            message = await get_text("info_free_slots", callback.from_user.id)
        elif info_key == "business_slots":
            message = await get_text("info_business_slots", callback.from_user.id)
        elif info_key == "quantum_slots":
            message = await get_text("info_quantum_slots", callback.from_user.id)
        else:
            message = "ℹ️ Информация"

        await callback.answer(message, show_alert=True)

    except Exception as e:
        logger.error(f"Ошибка info_handlers для {callback.data}: {e}")
        await callback.answer("ℹ️ Информация временно недоступна", show_alert=True)


# Обработчики кулдаунов слотов
@router.callback_query(F.data.startswith("cooldown_"))
async def cooldown_handlers(callback: CallbackQuery):
    """Обработка кликов по слотам на кулдауне"""
    try:
        message = await get_text("cooldown_slot", callback.from_user.id)
        await callback.answer(message, show_alert=True)
    except Exception as e:
        logger.error(f"Ошибка cooldown_handlers: {e}")
        await callback.answer("⏳ Этот слот на кулдауне", show_alert=True)


# Обработчики премиум функций
@router.callback_query(F.data.in_(["skip_hire_cooldown", "boost_training"]))
async def premium_handlers(callback: CallbackQuery):
    """Обработка премиум функций (ускорения)"""
    try:
        if callback.data == "skip_hire_cooldown":
            message = await get_text("boost_hire_info", callback.from_user.id)
        elif callback.data == "boost_training":
            message = await get_text("boost_training_info", callback.from_user.id)
        else:
            message = "💠 Премиум функция"

        await callback.answer(message, show_alert=True)

    except Exception as e:
        logger.error(f"Ошибка premium_handlers для {callback.data}: {e}")
        await callback.answer("💠 Премиум функции в разработке", show_alert=True)


# Обработчики заголовков слотов (для информации)
@router.callback_query(F.data.startswith("slot_header_"))
async def slot_header_handlers(callback: CallbackQuery):
    """Информация о конкретных слотах"""
    try:
        slot_num = callback.data.split("_")[-1]
        message = f"📋 Информация о слоте #{slot_num}"
        await callback.answer(message, show_alert=True)
    except Exception as e:
        logger.error(f"Ошибка slot_header_handlers: {e}")
        await callback.answer("📋 Слот найма", show_alert=True)


logger.info("✅ Academy handler загружен (Supabase версия)")
