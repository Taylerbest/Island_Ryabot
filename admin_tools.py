"""
Простые административные команды для разработки (PostgreSQL)
Запуск: python admin_tools.py
"""
import asyncio
from database.models import execute_db, get_user, initialize_db_pool, close_connection_pool

async def give_resources(user_id: int, ryabucks: int = 0, rbtc: float = 0.0):
    """Выдать ресурсы пользователю"""
    if ryabucks > 0:
        await execute_db("UPDATE users SET ryabucks = ryabucks + $1 WHERE user_id = $2", ryabucks, user_id)
    if rbtc > 0:
        await execute_db("UPDATE users SET rbtc = rbtc + $1 WHERE user_id = $2", rbtc, user_id)

    print(f"✅ Выдано пользователю {user_id}: {ryabucks}💵 {rbtc}RBTC")

async def set_level(user_id: int, level: int):
    """Установить уровень пользователя"""
    await execute_db("UPDATE users SET level = $1 WHERE user_id = $2", level, user_id)
    print(f"✅ Уровень пользователя {user_id} установлен на {level}")

async def reset_user(user_id: int):
    """Сбросить прогресс пользователя"""
    await execute_db("""
        UPDATE users SET 
            level = 1, experience = 0, energy = 100,
            ryabucks = 1000, rbtc = 0.0, tutorial_completed = FALSE
        WHERE user_id = $1
    """, user_id)
    print(f"✅ Прогресс пользователя {user_id} сброшен")

async def list_users():
    """Показать всех пользователей"""
    users = await execute_db("""
        SELECT user_id, username, level, ryabucks, rbtc 
        FROM users ORDER BY created_at DESC LIMIT 10
    """, fetch_all=True)

    print("\n📋 Последние пользователи:")
    for user in users:
        print(f"ID: {user['user_id']} | @{user['username']} | Lvl: {user['level']} | 💵{user['ryabucks']} | 🪙{user['rbtc']:.2f}")

async def main():
    # Инициализация подключения
    await initialize_db_pool()

    print("🛠️ Административные команды для Ryabot Island")
    print("=" * 50)
    print("1. Выдать ресурсы")
    print("2. Установить уровень")
    print("3. Сбросить прогресс")
    print("4. Список пользователей")
    print("0. Выход")

    choice = input("\nВведите номер команды: ")

    try:
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
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        await close_connection_pool()

if __name__ == "__main__":
    asyncio.run(main())
