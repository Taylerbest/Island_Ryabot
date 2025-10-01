"""
Energy Middleware для Ryabot Island v2.0
Списывает энергию за любые действия + система восстановления рекламой/конюшней
"""
import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from database.models import get_user, update_user_resources

logger = logging.getLogger(__name__)

class EnergyMiddleware(BaseMiddleware):
    """Middleware для автоматического списания энергии за действия"""

    # Стоимость энергии за различные действия
    ENERGY_COSTS = {
        # Навигация между разделами - 1 энергия
        'navigation_actions': {
            '🏠 Ферма': 1,
            '🏢 Город': 1,
            '👤 Житель': 1,
            '💼 ₽ябота': 1,
            '🎒 Рюкзак': 1,
            '👥 Друзья': 1,
            '🏆 Лидеры': 1,
            '🗄️ Прочее': 1,
        },

        # Callback кнопки навигации - 1 энергия
        'navigation_callbacks': {
            'academy': 1,
            'town': 1,
            'farm': 1,
            'work': 1,
            'citizen': 1,
            'storage': 1,
            'rankings': 1,
            'referral': 1,
            'about': 1,
        },

        # Игровые действия - 1 энергия
        'game_actions': {
            'hire_worker': 1,
            'start_training': 1,
            'collect_resources': 1,
            'feed_animals': 1,
            'harvest_crops': 1,
            'market_purchase': 1,
            'build_construction': 1,
            'upgrade_building': 1,
            # Экспедиции и мини-игры дороже
            'start_expedition': 2,
            'rooster_fight': 2,
            'horse_race': 2,
        },

        # Бесплатные действия (не тратят энергию)
        'free_actions': {
            'back', 'cancel', 'help', 'settings', 'info_',
            'lang_', 'tutorial_', 'back_to_', 'menu',
            'watch_ad',  # Просмотр рекламы бесплатный
            'claim_stable_energy'  # Сбор энергии из конюшни
        }
    }

    async def __call__(
        self,
        handler: Callable,
        event,
        data: Dict[str, Any]
    ) -> Any:
        """Основная логика middleware"""

        user_id = None
        action_type = None

        # Определяем пользователя и действие
        if isinstance(event, Message):
            user_id = event.from_user.id
            action_type = event.text
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            action_type = event.data

        if not user_id or not action_type:
            return await handler(event, data)

        # Определяем стоимость энергии
        energy_cost = self._calculate_energy_cost(action_type)

        # Если действие бесплатное - пропускаем
        if energy_cost == 0:
            return await handler(event, data)

        # Проверяем и списываем энергию
        if not await self._consume_energy(user_id, energy_cost, event):
            return None  # Останавливаем выполнение

        # Выполняем основной обработчик
        return await handler(event, data)

    def _calculate_energy_cost(self, action: str) -> int:
        """Рассчитывает стоимость энергии для действия"""
        if not action:
            return 0

        # Проверяем бесплатные действия
        for free_action in self.ENERGY_COSTS['free_actions']:
            if free_action in action:
                return 0

        # Проверяем навигацию по тексту сообщения
        if action in self.ENERGY_COSTS['navigation_actions']:
            return self.ENERGY_COSTS['navigation_actions'][action]

        # Проверяем навигацию по callback
        if action in self.ENERGY_COSTS['navigation_callbacks']:
            return self.ENERGY_COSTS['navigation_callbacks'][action]

        # Проверяем игровые действия
        for game_action in self.ENERGY_COSTS['game_actions']:
            if game_action in action:
                return self.ENERGY_COSTS['game_actions'][game_action]

        # По умолчанию любое другое действие стоит 1 энергию
        return 1

    async def _consume_energy(self, user_id: int, cost: int, event) -> bool:
        """Списывает энергию у пользователя"""
        try:
            user = await get_user(user_id)
            if not user:
                return True  # Новые пользователи проходят

            # Проверяем хватает ли энергии
            if user.energy < cost:
                await self._send_low_energy_message(event, user.energy, cost)
                return False

            # Списываем энергию
            success = await update_user_resources(user_id, energy=-cost)
            if success:
                logger.info(f"💡 Энергия списана: -{cost} у пользователя {user_id} (осталось: {user.energy - cost})")
                return True
            else:
                logger.error(f"❌ Не удалось списать энергию у пользователя {user_id}")
                return True  # При ошибке пропускаем

        except Exception as e:
            logger.error(f"Ошибка списания энергии: {e}")
            return True  # При ошибке пропускаем

    async def _send_low_energy_message(self, event, current_energy: int, required_energy: int):
        """Отправляет сообщение о нехватке энергии с вариантами восстановления"""
        message = f"""⚡ **Недостаточно энергии!**

🔋 У вас: {current_energy} энергии
💡 Требуется: {required_energy} энергии

🎯 **Способы восстановления энергии:**

📺 **Бесплатная реклама:**
• Посмотрите рекламу → получите +20 энергии
• Доступно каждые 30 минут
• Нажмите 👇 чтобы посмотреть

🐴 **Конюшня (когда построите):**
• Лошади автоматически производят энергию
• Собирайте каждые 4 часа
• Улучшайте для большей эффективности

💎 **Премиум способы:**
• Quantum Keys - мгновенное восстановление
• Premium подписка - в 2 раза быстрее

💡 **Совет:** Планируйте действия и изучайте вики!"""

        try:
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

            # Кнопка для просмотра рекламы
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📺 Посмотреть рекламу (+20 энергии)", callback_data="watch_ad")]
            ])

            if isinstance(event, CallbackQuery):
                await event.answer("⚡ Недостаточно энергии!", show_alert=True)
                await event.message.answer(message, reply_markup=keyboard, parse_mode="Markdown")
            else:
                await event.answer(message, reply_markup=keyboard, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения об энергии: {e}")

logger.info("✅ Energy middleware загружен (Supabase версия)")
