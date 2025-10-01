"""
Административные команды для Ryabot Island v2.0
Полная поддержка Supabase архитектуры
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from database.models import get_user, get_island_stats
from utils.message_helper import send_formatted
from config import config
import logging

logger = logging.getLogger(__name__)

# ИСПРАВЛЕНИЕ: Создаем роутер
router = Router()


def is_admin(user_id: int) -> bool:
    """Проверка, является ли пользователь администратором"""
    try:
        admin_ids = config.bot.admin_ids if hasattr(config.bot, 'admin_ids') else []
        return user_id in admin_ids
    except:
        # Fallback - хардкод админов из .env
        import os
        admin_ids_str = os.getenv("ADMIN_IDS", "")
        if admin_ids_str:
            admin_ids = [int(x.strip()) for x in admin_ids_str.split(",") if x.strip()]
            return user_id in admin_ids
        return False


@router.message(Command("stats"))
async def stats_command(message: Message):
    """Статистика бота для администраторов"""
    if not is_admin(message.from_user.id):
        return

    try:
        # Получаем статистику через Supabase
        stats = await get_island_stats()

        await message.answer(f"""
📊 **Статистика Ryabot Island**

👥 Всего игроков: {stats.get('total_players', 0)}
✅ Активных сегодня: {stats.get('online_players', 0)}
💠 RBTC добыто сегодня: {stats.get('daily_rbtc', 0):.2f}
🗺️ Активных экспедиций: {stats.get('active_expeditions', 0)}
        """, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Ошибка получения статистики: {e}")
        await message.answer("❌ Ошибка получения статистики")


@router.message(Command("admin"))
async def admin_command(message: Message):
    """Админская панель"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав администратора")
        return

    await message.answer("""
🔧 **Панель администратора**

📋 Доступные команды:
• /stats - Статистика бота
• /broadcast - Рассылка (в разработке)
• /maintenance - Режим обслуживания (в разработке)

🛠️ Для расширенного управления используйте admin_tools.py
    """, parse_mode="Markdown")


@router.message(Command("version"))
async def version_command(message: Message):
    """Версия бота"""
    if not is_admin(message.from_user.id):
        return

    await message.answer("""
🏝️ **Ryabot Island v2.0**

🔧 Архитектура: Supabase
📊 База данных: PostgreSQL (Supabase)
🤖 Framework: aiogram 3.x
🐍 Python: 3.11+
⚡ Статус: Активен
    """, parse_mode="Markdown")


logger.info("✅ Admin handler загружен (Supabase версия)")
