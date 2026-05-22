from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def upsert_telegram_user(
        self,
        telegram_id: int,
        username: str | None,
        first_name: str | None,
    ) -> User:
        user = await self.get_by_telegram_id(telegram_id)
        if user is None:
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_limit_reset_at=datetime.now(timezone.utc),
            )
            self.session.add(user)
        else:
            user.username = username
            user.first_name = first_name
        await self.session.flush()
        return user

    async def update_premium(
        self, user: User, is_premium: bool, expires_at: datetime | None = None
    ) -> User:
        user.is_premium = is_premium
        user.premium_expires_at = expires_at
        await self.session.flush()
        return user

    async def increment_notifications(self, user: User) -> User:
        user.daily_notifications_used += 1
        await self.session.flush()
        return user

    async def reset_daily_limits(self, user: User) -> User:
        user.daily_notifications_used = 0
        user.last_limit_reset_at = datetime.now(timezone.utc)
        await self.session.flush()
        return user
