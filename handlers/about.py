from aiogram import Router
from utils.message_helper import send_formatted
from database.models import get_user, create_user, update_user_resources, get_island_stats
import logging

logger = logging.getLogger(__name__)

router = Router()

# Добавьте обработчики прочего здесь

logger.info("✅ About handler загружен (Supabase версия)")
