@router.message(Command("stats"))
async def stats_command(message: Message):
    if not is_admin(message.from_user.id):
        return

    from database.models import execute_db

    # PostgreSQL синтаксис
    total = await execute_db("SELECT COUNT(*) as count FROM users", fetch_one=True)
    active_today = await execute_db("""
        SELECT COUNT(*) as count FROM users 
        WHERE DATE(last_active) = CURRENT_DATE
    """, fetch_one=True)

    await message.answer(f"""
📊 **Статистика бота**

👥 Всего пользователей: {total['count'] if total else 0}
✅ Активных сегодня: {active_today['count'] if active_today else 0}
    """)
