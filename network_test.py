import asyncio
import socket
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()


async def network_test():
    original_host = "db.fqgcctsvozcoezpfytck.supabase.co"
    fallback_ip = "3.64.163.50"

    print("🌐 ТЕСТ СЕТИ И ПОДКЛЮЧЕНИЯ")
    print("=" * 40)

    # 1. Тест DNS
    print(f"1️⃣ DNS резолюция: {original_host}")
    try:
        ipv4 = socket.gethostbyname(original_host)
        print(f"   ✅ Успех: {ipv4}")
        use_host = ipv4
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        print(f"   🔄 Используем fallback: {fallback_ip}")
        use_host = fallback_ip

    # 2. Тест TCP соединения
    print(f"\n2️⃣ TCP соединение: {use_host}:5432")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((use_host, 5432))
        sock.close()

        if result == 0:
            print("   ✅ Порт открыт")
        else:
            print("   ❌ Порт закрыт или недоступен")
    except Exception as e:
        print(f"   ❌ Ошибка TCP: {e}")

    # 3. Тест PostgreSQL подключения
    print(f"\n3️⃣ PostgreSQL подключение")
    try:
        conn = await asyncpg.connect(
            host=use_host,
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            database=os.getenv("POSTGRES_DB"),
            port=5432,
            ssl='require',
            timeout=15
        )

        result = await conn.fetchval("SELECT current_database()")
        print(f"   ✅ PostgreSQL работает! База: {result}")
        await conn.close()

    except Exception as e:
        print(f"   ❌ PostgreSQL ошибка: {type(e).__name__}: {e}")


if __name__ == "__main__":
    asyncio.run(network_test())
