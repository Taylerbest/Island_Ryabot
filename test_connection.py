"""
Тест подключения к Supabase для Ryabot Island
"""
import asyncio
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()


async def test_supabase_connection():
    """Проверка подключения к Supabase"""
    print("🔌 Проверка подключения к Supabase...")

    try:
        # Проверяем переменные окружения
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")

        if not supabase_url or not supabase_key:
            print("❌ Ошибка: SUPABASE_URL или SUPABASE_ANON_KEY не установлены в .env")
            return False

        print(f"✅ URL: {supabase_url}")
        print(f"✅ Key: {supabase_key[:20]}...")

        # Импортируем и инициализируем клиент
        from database.supabase_client import supabase_manager
        supabase_manager.initialize()

        # Тестовый запрос
        result = await supabase_manager.execute_query(
            table="users",
            operation="count"
        )

        print(f"✅ Подключение работает! Пользователей в БД: {result or 0}")
        return True

    except ImportError as e:
        print(f"❌ Ошибка импорта модулей: {e}")
        print("💡 Убедитесь, что установили: pip install supabase python-dotenv")
        return False

    except Exception as e:
        print(f"❌ Ошибка подключения к Supabase: {e}")
        print("💡 Проверьте URL и ключи в .env файле")
        return False


async def test_telegram_token():
    """Проверка токена Telegram бота"""
    print("\n🤖 Проверка токена Telegram...")

    try:
        bot_token = os.getenv("BOT_TOKEN")

        if not bot_token:
            print("❌ BOT_TOKEN не установлен в .env")
            return False

        print(f"✅ Token: {bot_token[:10]}...{bot_token[-10:]}")

        # Проверяем токен через API
        from aiogram import Bot
        bot = Bot(token=bot_token)

        bot_info = await bot.get_me()
        print(f"✅ Бот найден: @{bot_info.username} ({bot_info.first_name})")

        await bot.session.close()
        return True

    except Exception as e:
        print(f"❌ Ошибка с токеном бота: {e}")
        print("💡 Проверьте BOT_TOKEN в .env файле")
        return False


async def main():
    """Основная функция тестирования"""
    print("=" * 50)
    print("🏝️  RYABOT ISLAND - ТЕСТ ПОДКЛЮЧЕНИЙ")
    print("=" * 50)

    # Тест 1: Supabase
    supabase_ok = await test_supabase_connection()

    # Тест 2: Telegram
    telegram_ok = await test_telegram_token()

    # Итоги
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("=" * 50)

    if supabase_ok and telegram_ok:
        print("🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("✅ Supabase подключение работает")
        print("✅ Telegram токен действителен")
        print("\n🚀 Можно запускать бота: python main.py")
    else:
        print("⚠️  ОБНАРУЖЕНЫ ПРОБЛЕМЫ:")
        if not supabase_ok:
            print("❌ Проблемы с Supabase")
        if not telegram_ok:
            print("❌ Проблемы с Telegram")
        print("\n🔧 Исправьте ошибки перед запуском бота")


if __name__ == "__main__":
    asyncio.run(main())
