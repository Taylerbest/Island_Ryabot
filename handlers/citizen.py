from aiogram import Router
from utils.message_helper import send_formatted
from database.supabase_models import get_user, create_user, update_user_resources, get_island_stats
router = Router()

# Добавь обработчики жителя здесь
