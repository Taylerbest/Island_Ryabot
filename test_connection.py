import asyncio
import os
import socket
from dotenv import load_dotenv

load_dotenv()


async def test_supabase_ipv4():
    host = os.getenv("POSTGRES_HOST")
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    db = os.getenv("POSTGRES_DB")
    port = int(os.getenv("POSTGRES_PORT", 5432))

    print(f"🔍 Хост: {host}")

    # Принудительно резолвим в IPv4
    try:
        print("🌐 Резолвим IPv4 адрес...")
        ipv4_address = socket.gethostbyname(host)
        print(f"✅ IPv4 адрес: {ipv4_address}")
    except Exception as e:
        print(f"❌ Не удалось получить IPv4: {e}")
        return

    # Подключаемся к IPv4 адресу вместо хоста
    try:
        import asyncpg

        print(f"🔌 Подключение к {ipv4_address}:{port}...")
        conn = await asyncpg.connect(
            host=ipv4_address,  # Используем IP вместо хоста
            user=user,
            password=password,
            database=db,
            port=port,
            timeout=10
        )

        result = await conn.fetchval("SELECT version()")
        print(f"✅ Подключение по IPv4 успешно!")
        print(f"📋 PostgreSQL: {result[:50]}...")

        await conn.close()

    except Exception as e:
        print(f"❌ Ошибка подключения к IPv4:")
        print(f"   Тип: {type(e).__name__}")
        print(f"   Сообщение: {e}")


if __name__ == "__main__":
    asyncio.run(test_supabase_ipv4())
