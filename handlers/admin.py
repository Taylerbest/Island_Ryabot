from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from database.models import get_user, update_user_resources

router = Router()

ADMIN_IDS = [123456789]  # ← Твой Telegram ID


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет доступа!")
        return

    await message.answer("""
🛠️ **Админ-панель**

/give [user_id] [ryabucks] - Выдать рябаксы
/setlevel [user_id] [level] - Установить уровень
/stats - Статистика бота
    """)


@router.message(Command("give"))
async def give_command(message: Message):
    if not is_admin(message.from_user.id):
        return

    try:
        parts = message.text.split()
        user_id = int(parts[1])
        amount = int(parts[2])

        await update_user_resources(user_id, ryabucks=amount)
        await message.answer(f"✅ Выдано {amount}💵 пользователю {user_id}")
    except:
        await message.answer("❌ Использование: /give [user_id] [amount]")


@router.message(Command("stats"))
async def stats_command(message: Message):
    if not is_admin(message.from_user.id):
        return

    from database.models import execute_db

    total = await execute_db("SELECT COUNT(*) FROM users", fetch_one=True)
    active_today = await execute_db("""
                                    SELECT COUNT(*)
                                    FROM users
                                    WHERE date (last_active) = date ('now')
                                    """, fetch_one=True)

    await message.answer(f"""
📊 **Статистика бота**

👥 Всего пользователей: {total[0]}
✅ Активных сегодня: {active_today[0]}
    """)
