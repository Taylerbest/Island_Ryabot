import asyncio
import socket
import os
from dotenv import load_dotenv

load_dotenv()


async def quick_dns_test():
    host = os.getenv("POSTGRES_HOST")
    print(f"🔍 Тестируем хост: {host}")

    # Тест DNS резолюции
    try:
        ipv4 = socket.gethostbyname(host)
        print(f"✅ DNS работает: {host} → {ipv4}")

        # Тест подключения к PostgreSQL
        try:
            import asyncpg
            conn = await asyncpg.connect(
                host=ipv4,  # Используем IP
                user=os.getenv("POSTGRES_USER"),
                password=os.getenv("POSTGRES_PASSWORD"),
                database=os.getenv("POSTGRES_DB"),
                port=int(os.getenv("POSTGRES_PORT")),
                timeout=10
            )

            result = await conn.fetchval("SELECT 1")
            print(f"✅ PostgreSQL подключение работает! Результат: {result}")
            await conn.close()

        except Exception as e:
            print(f"❌ Ошибка PostgreSQL: {e}")

    except Exception as e:
        print(f"❌ Ошибка DNS: {e}")


asyncio.run(quick_dns_test())
