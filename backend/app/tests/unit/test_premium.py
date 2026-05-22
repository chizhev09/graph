import pytest
from unittest.mock import AsyncMock, patch

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.premium_service import PremiumService


@pytest.mark.asyncio
async def test_premium_channel_check(db_session):
    user = User(telegram_id=666, is_premium=False)
    db_session.add(user)
    await db_session.flush()

    service = PremiumService(UserRepository(db_session))
    with patch.object(service, "check_channel_membership", new_callable=AsyncMock) as mock:
        mock.return_value = True
        user = await service.sync_user_premium(user)
    assert user.is_premium is True
