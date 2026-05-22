import pytest
from datetime import datetime, timezone

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.limit_service import LimitService


@pytest.mark.asyncio
async def test_free_user_notification_limit(db_session):
    user = User(
        telegram_id=333,
        daily_notifications_used=5,
        last_limit_reset_at=datetime.now(timezone.utc),
    )
    db_session.add(user)
    await db_session.flush()

    service = LimitService(UserRepository(db_session))
    assert await service.can_send_notification(user) is False


@pytest.mark.asyncio
async def test_premium_unlimited(db_session):
    user = User(
        telegram_id=444,
        is_premium=True,
        daily_notifications_used=100,
    )
    db_session.add(user)
    await db_session.flush()

    service = LimitService(UserRepository(db_session))
    assert await service.can_send_notification(user) is True
    assert service.notifications_remaining(user) is None


@pytest.mark.asyncio
async def test_daily_reset(db_session):
    user = User(
        telegram_id=555,
        daily_notifications_used=5,
        last_limit_reset_at=datetime(2020, 1, 1, tzinfo=timezone.utc),
    )
    db_session.add(user)
    await db_session.flush()

    repo = UserRepository(db_session)
    service = LimitService(repo)
    user = await service.ensure_reset(user)
    assert user.daily_notifications_used == 0
