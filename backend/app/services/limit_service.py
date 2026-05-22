from datetime import datetime, timezone

from app.core.config import get_settings
from app.models.user import User
from app.repositories.user_repository import UserRepository


class LimitService:
    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo
        self.settings = get_settings()

    def _needs_reset(self, user: User) -> bool:
        if user.last_limit_reset_at is None:
            return True
        now = datetime.now(timezone.utc)
        last = user.last_limit_reset_at
        if last.tzinfo is None:
            last = last.replace(tzinfo=timezone.utc)
        return now.date() > last.date()

    async def ensure_reset(self, user: User) -> User:
        if self._needs_reset(user):
            return await self.user_repo.reset_daily_limits(user)
        return user

    async def can_send_notification(self, user: User) -> bool:
        user = await self.ensure_reset(user)
        if user.is_premium:
            return True
        return user.daily_notifications_used < self.settings.free_daily_notifications

    def notifications_remaining(self, user: User) -> int | None:
        if user.is_premium:
            return None
        remaining = self.settings.free_daily_notifications - user.daily_notifications_used
        return max(0, remaining)

    async def record_notification(self, user: User) -> User:
        user = await self.ensure_reset(user)
        if not user.is_premium:
            return await self.user_repo.increment_notifications(user)
        return user

    def can_create_search(self, user: User, active_count: int) -> bool:
        if user.is_premium:
            return True
        return active_count < self.settings.free_max_searches
