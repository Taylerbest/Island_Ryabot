"""
Простые административные команды для разработки
Запуск: python admin_tools.py
"""
import asyncio
import aiosqlite
from database.models import DB_PATH, get_user, update_user_resources


async def give_resources(user_id: int, ryabucks: int = 0, rbtc: float = 0.0):
    """Выдать ресурсы пользователю"""
    if ryabucks > 0 or rbtc > 0:
        await update_user_resources(user_id, ryabucks=ryabucks, rbtc=rbtc)
        print(f"✅ Выдано пользователю {user_id}: {ryabucks}💵 {rbtc}RBTC")


async def set_level(user_id: int, level: int):
    """Установить уровень пользователя"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET level = ? WHERE user_id = ?", (level, user_id))
        await db.commit()
    print(f"✅ Уровень пользователя {user_id} установлен на {level}")


async def reset_user(user_id: int):
    """Сбросить прогресс пользователя"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
                         UPDATE users
                         SET level              = 1,
                             experience         = 0,
                             energy             = 100,
                             ryabucks           = 1000,
                             rbtc               = 0.0,
                             tutorial_completed = 0
                         WHERE user_id = ?
                         """, (user_id,))
        await db.commit()
    print(f"✅ Прогресс пользователя {user_id} сброшен")


async def list_users():
    """Показать всех пользователей"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT user_id, username, level, ryabucks, rbtc FROM users")
        users = await cursor.fetchall()

    print("\n📋 Пользователи:")
    for user in users:
        print(f"ID: {user[0]} | @{user[1]} | Lvl: {user[2]} | 💵{user[3]} | 🪙{user[4]:.2f}")


async def main():
    print("🛠️ Административные команды для Ryabot Island")
    print("=" * 50)
    print("1. Выдать ресурсы")
    print("2. Установить уровень")
    print("3. Сбросить прогресс")
    print("4. Список пользователей")
    print("0. Выход")

    choice = input("\nВведите номер команды: ")

    if choice == "1":
        user_id = int(input("ID пользователя: "))
        ryabucks = int(input("Рябаксы: "))
        rbtc = float(input("RBTC: "))
        await give_resources(user_id, ryabucks, rbtc)
    elif choice == "2":
        user_id = int(input("ID пользователя: "))
        level = int(input("Уровень: "))
        await set_level(user_id, level)
    elif choice == "3":
        user_id = int(input("ID пользователя: "))
        await reset_user(user_id)
    elif choice == "4":
        await list_users()


if __name__ == "__main__":
    asyncio.run(main())
