import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Telegram Bot
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")
    WEBHOOK_PATH = "/webhook"

    # Database
    DB_PATH = os.getenv("DB_PATH", "ryabot_island.db")

    # Game Settings
    MAX_ENERGY = 100
    ENERGY_REGEN_HOURS = 4

    # Server
    HOST = "0.0.0.0"
    PORT = 8000

    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")  # development | production

    # Redis (для будущего использования)
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")


config = Config()
