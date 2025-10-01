"""
Middleware для защиты от спама в Ryabot Island v2.0
Полная поддержка Supabase архитектуры с улучшенной защитой и логированием
"""
import time
import logging
from typing import Callable, Dict, Any, Awaitable, Optional
from collections import defaultdict, deque
from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, Update
from config import config

logger = logging.getLogger(__name__)


class ThrottlingMiddleware(BaseMiddleware):
    """
    Продвинутый middleware для защиты от спама и флуда
    Поддерживает разные лимиты для разных типов действий
    """

    def __init__(self,
                 rate_limit: float = 0.3,
                 burst_protection: bool = True,
                 admin_bypass: bool = True,
                 enable_stats: bool = True):
        """
        Args:
            rate_limit: базовый лимит между действиями (секунды)
            burst_protection: защита от burst-атак
            admin_bypass: админы обходят ограничения
            enable_stats: включить сбор статистики
        """
        self.rate_limit = rate_limit
        self.burst_protection = burst_protection
        self.admin_bypass = admin_bypass
        self.enable_stats = enable_stats

        # Хранилища для пользователей
        self.user_last_action = {}  # user_id -> timestamp последнего действия
        self.user_action_history = defaultdict(lambda: deque(maxlen=10))  # История действий для burst защиты
        self.user_violations = defaultdict(int)  # Количество нарушений
        self.blocked_users = {}  # Временно заблокированные пользователи

        # Статистика
        self.stats = {
            'total_requests': 0,
            'throttled_requests': 0,
            'blocked_requests': 0,
            'unique_users': set(),
            'start_time': time.time()
        }

        # Настройки лимитов по типам действий
        self.action_limits = {
            'callback_query': 0.3,  # Кнопки
            'message': 0.5,  # Сообщения
            'command': 0.8,  # Команды
            'premium_action': 0.1  # Премиум действия (меньше лимит)
        }

        # Настройки burst защиты
        self.burst_window = 10  # секунд
        self.burst_limit = 8  # максимум действий в окне
        self.block_duration = 60  # секунд блокировки при превышении

        logger.info(f"✅ ThrottlingMiddleware инициализирован (rate_limit={rate_limit}s)")

    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any]
    ) -> Any:
        """Основная логика middleware"""

        # Определяем пользователя и тип события
        user_id, action_type = self._extract_user_info(event)

        if user_id is None:
            # Событие без пользователя - пропускаем
            return await handler(event, data)

        # Обновляем статистику
        if self.enable_stats:
            self._update_stats(user_id, action_type)

        # Проверяем админские права
        if self.admin_bypass and self._is_admin(user_id):
            logger.debug(f"Admin {user_id} bypass throttling")
            return await handler(event, data)

        # Проверяем блокировку
        if await self._check_user_blocked(user_id):
            logger.warning(f"User {user_id} is temporarily blocked")
            await self._send_blocked_message(event)
            return None

        # Проверяем основной rate limit
        if not await self._check_rate_limit(user_id, action_type):
            await self._handle_throttling(event, user_id, action_type)
            return None

        # Проверяем burst защиту
        if self.burst_protection and not await self._check_burst_protection(user_id):
            await self._handle_burst_violation(event, user_id)
            return None

        # Обновляем время последнего действия
        self._update_user_activity(user_id, action_type)

        # Выполняем обработчик
        try:
            return await handler(event, data)
        except Exception as e:
            logger.error(f"Handler error for user {user_id}: {e}")
            raise

    def _extract_user_info(self, event: Update) -> tuple[Optional[int], str]:
        """Извлекает информацию о пользователе и типе события"""
        user_id = None
        action_type = "unknown"

        # ИСПРАВЛЕНИЕ: правильная проверка типа события
        if isinstance(event, CallbackQuery):
            # Если event - это CallbackQuery напрямую
            user_id = event.from_user.id
            action_type = "callback_query"
        elif isinstance(event, Message):
            # Если event - это Message напрямую
            user_id = event.from_user.id
            if event.text and event.text.startswith('/'):
                action_type = "command"
            else:
                action_type = "message"
        elif hasattr(event, 'callback_query') and event.callback_query:
            # Если event - это Update с callback_query
            user_id = event.callback_query.from_user.id
            action_type = "callback_query"
        elif hasattr(event, 'message') and event.message:
            # Если event - это Update с message
            user_id = event.message.from_user.id
            if event.message.text and event.message.text.startswith('/'):
                action_type = "command"
            else:
                action_type = "message"
        elif hasattr(event, 'from_user') and event.from_user:
            # Прямой доступ к from_user
            user_id = event.from_user.id
            action_type = "other"

        return user_id, action_type

    def _is_admin(self, user_id: int) -> bool:
        """Проверяет, является ли пользователь администратором"""
        try:
            return config.bot.is_admin(user_id)
        except:
            return False

    async def _check_user_blocked(self, user_id: int) -> bool:
        """Проверяет, заблокирован ли пользователь"""
        if user_id in self.blocked_users:
            block_time = self.blocked_users[user_id]
            if time.time() - block_time < self.block_duration:
                return True
            else:
                # Разблокируем пользователя
                del self.blocked_users[user_id]
                self.user_violations[user_id] = 0
                logger.info(f"User {user_id} unblocked after timeout")

        return False

    async def _check_rate_limit(self, user_id: int, action_type: str) -> bool:
        """Проверяет основной rate limit"""
        current_time = time.time()

        # Получаем лимит для типа действия
        limit = self.action_limits.get(action_type, self.rate_limit)

        # Проверяем последнее действие пользователя
        if user_id in self.user_last_action:
            time_diff = current_time - self.user_last_action[user_id]
            if time_diff < limit:
                logger.debug(f"Rate limit hit for user {user_id}: {time_diff:.2f}s < {limit}s")
                return False

        return True

    async def _check_burst_protection(self, user_id: int) -> bool:
        """Проверяет burst защиту"""
        current_time = time.time()
        history = self.user_action_history[user_id]

        # Добавляем текущее действие
        history.append(current_time)

        # Удаляем старые действия из окна
        while history and current_time - history[0] > self.burst_window:
            history.popleft()

        # Проверяем лимит
        if len(history) > self.burst_limit:
            logger.warning(f"Burst limit exceeded for user {user_id}: {len(history)} actions in {self.burst_window}s")
            return False

        return True

    async def _handle_throttling(self, event: Update, user_id: int, action_type: str):
        """Обработка нарушения rate limit"""
        self.user_violations[user_id] += 1

        if self.enable_stats:
            self.stats['throttled_requests'] += 1

        logger.debug(f"Throttling user {user_id} (violations: {self.user_violations[user_id]})")

        # Отправляем предупреждение
        try:
            if event.callback_query:
                await event.callback_query.answer("⏱️ Слишком быстро! Подождите немного.", show_alert=False)
            elif event.message:
                # Для сообщений отправляем реакцию или ничего не делаем (чтобы не спамить)
                pass
        except Exception as e:
            logger.debug(f"Failed to send throttling message: {e}")

    async def _handle_burst_violation(self, event: Update, user_id: int):
        """Обработка нарушения burst защиты"""
        self.user_violations[user_id] += 3  # Более серьезное нарушение

        # Блокируем пользователя на время
        self.blocked_users[user_id] = time.time()

        if self.enable_stats:
            self.stats['blocked_requests'] += 1

        logger.warning(f"User {user_id} blocked for burst violation (violations: {self.user_violations[user_id]})")

        # Отправляем строгое предупреждение
        try:
            if event.callback_query:
                await event.callback_query.answer(
                    "🚫 Слишком много действий! Вы временно заблокированы на 1 минуту.",
                    show_alert=True
                )
        except Exception as e:
            logger.debug(f"Failed to send burst violation message: {e}")

    async def _send_blocked_message(self, event: Update):
        """Отправляет сообщение заблокированному пользователю"""
        try:
            if event.callback_query:
                await event.callback_query.answer(
                    "🚫 Вы временно заблокированы за спам. Подождите 1 минуту.",
                    show_alert=True
                )
        except Exception as e:
            logger.debug(f"Failed to send blocked message: {e}")

    def _update_user_activity(self, user_id: int, action_type: str):
        """Обновляет время последнего действия пользователя"""
        self.user_last_action[user_id] = time.time()

    def _update_stats(self, user_id: int, action_type: str):
        """Обновляет статистику использования"""
        self.stats['total_requests'] += 1
        self.stats['unique_users'].add(user_id)

    def get_stats(self) -> dict:
        """Возвращает статистику middleware"""
        current_time = time.time()
        uptime = current_time - self.stats['start_time']

        return {
            'uptime_seconds': int(uptime),
            'total_requests': self.stats['total_requests'],
            'throttled_requests': self.stats['throttled_requests'],
            'blocked_requests': self.stats['blocked_requests'],
            'unique_users': len(self.stats['unique_users']),
            'currently_blocked': len(self.blocked_users),
            'requests_per_minute': int(self.stats['total_requests'] / (uptime / 60)) if uptime > 0 else 0,
            'throttle_rate': f"{(self.stats['throttled_requests'] / max(self.stats['total_requests'], 1)) * 100:.1f}%"
        }

    def reset_stats(self):
        """Сбрасывает статистику"""
        self.stats = {
            'total_requests': 0,
            'throttled_requests': 0,
            'blocked_requests': 0,
            'unique_users': set(),
            'start_time': time.time()
        }
        logger.info("📊 Статистика throttling сброшена")

    def unblock_user(self, user_id: int) -> bool:
        """Принудительно разблокировать пользователя (для админов)"""
        if user_id in self.blocked_users:
            del self.blocked_users[user_id]
            self.user_violations[user_id] = 0
            logger.info(f"User {user_id} manually unblocked")
            return True
        return False

    def block_user(self, user_id: int, duration: int = None) -> bool:
        """Принудительно заблокировать пользователя (для админов)"""
        if duration:
            # Блокировка на определенное время (не реализовано в этой версии)
            pass

        self.blocked_users[user_id] = time.time()
        self.user_violations[user_id] += 10  # Серьезное нарушение
        logger.info(f"User {user_id} manually blocked")
        return True

    def get_user_info(self, user_id: int) -> dict:
        """Получить информацию о пользователе"""
        current_time = time.time()

        is_blocked = user_id in self.blocked_users
        block_remaining = 0

        if is_blocked:
            block_time = self.blocked_users[user_id]
            block_remaining = max(0, self.block_duration - (current_time - block_time))

        last_action = self.user_last_action.get(user_id, 0)
        time_since_last = current_time - last_action if last_action > 0 else -1

        return {
            'user_id': user_id,
            'is_blocked': is_blocked,
            'block_remaining_seconds': int(block_remaining),
            'violations_count': self.user_violations[user_id],
            'last_action_seconds_ago': int(time_since_last) if time_since_last >= 0 else None,
            'recent_actions': len(self.user_action_history[user_id])
        }


# Расширенный middleware для специфичных игровых действий
class GameActionThrottlingMiddleware(ThrottlingMiddleware):
    """
    Специализированный middleware для игровых действий
    Учитывает особенности игровой механики Ryabot Island
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Специальные лимиты для игровых действий
        self.game_action_limits = {
            'hire_worker': 2.0,  # Найм работника
            'start_training': 1.5,  # Начало обучения
            'collect_resources': 1.0,  # Сбор ресурсов
            'farm_action': 0.8,  # Действия на ферме
            'expedition_start': 3.0,  # Начало экспедиции
            'battle_action': 0.5,  # Боевые действия
            'market_purchase': 1.2  # Покупки на рынке
        }

    async def _check_rate_limit(self, user_id: int, action_type: str) -> bool:
        """Переопределенная проверка с игровыми лимитами"""
        current_time = time.time()

        # Определяем лимит
        if action_type in self.game_action_limits:
            limit = self.game_action_limits[action_type]
        else:
            limit = self.action_limits.get(action_type, self.rate_limit)

        # Проверяем последнее действие
        if user_id in self.user_last_action:
            time_diff = current_time - self.user_last_action[user_id]
            if time_diff < limit:
                logger.debug(f"Game rate limit hit for user {user_id}: {action_type} {time_diff:.2f}s < {limit}s")
                return False

        return True


# Создание экземпляров middleware
def create_throttling_middleware() -> ThrottlingMiddleware:
    """Создает настроенный экземпляр throttling middleware"""
    return ThrottlingMiddleware(
        rate_limit=config.server.throttle_rate,
        burst_protection=True,
        admin_bypass=True,
        enable_stats=True
    )


def create_game_throttling_middleware() -> GameActionThrottlingMiddleware:
    """Создает игровой throttling middleware"""
    return GameActionThrottlingMiddleware(
        rate_limit=config.server.throttle_rate,
        burst_protection=True,
        admin_bypass=True,
        enable_stats=True
    )


logger.info("✅ Throttling middleware загружен (Supabase версия)")
