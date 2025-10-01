import socket
import requests


def get_ipv4_for_supabase():
    host = "db.fqgcctsvozcoezpfytck.supabase.co"

    # Метод 1: Через socket с принудительным IPv4
    try:
        # Принудительно используем IPv4
        result = socket.getaddrinfo(host, 5432, socket.AF_INET)
        if result:
            ipv4 = result[0][4][0]
            print(f"✅ IPv4 через socket: {ipv4}")
            return ipv4
    except Exception as e:
        print(f"❌ Socket метод не работает: {e}")

    # Метод 2: Через внешний DNS API
    try:
        # Используем CloudFlare DNS over HTTPS
        url = f"https://cloudflare-dns.com/dns-query?name={host}&type=A"
        headers = {'Accept': 'application/dns-json'}

        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()

        if 'Answer' in data and data['Answer']:
            ipv4 = data['Answer'][0]['data']
            print(f"✅ IPv4 через CloudFlare DNS: {ipv4}")
            return ipv4

    except Exception as e:
        print(f"❌ CloudFlare DNS не работает: {e}")

    # Метод 3: Известный IPv4 для Supabase (может устареть)
    fallback_ip = "3.64.163.50"
    print(f"⚠️ Используем fallback IP: {fallback_ip}")
    return fallback_ip


if __name__ == "__main__":
    ipv4 = get_ipv4_for_supabase()
    print(f"\n📋 Обнови .env файл:")
    print(f"POSTGRES_HOST={ipv4}")
