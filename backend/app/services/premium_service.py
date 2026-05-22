from datetime import datetime, timezone

import httpx
import structlog

from app.core.config import get_settings
from app.models.user import User
from app.repositories.user_repository import UserRepository

logger = structlog.get_logger(__name__)


class PremiumService:
    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo
        self.settings = get_settings()

    async def check_channel_membership(self, telegram_id: int) -> bool:
        channel_id = self.settings.premium_channel_id
        token = self.settings.bot_token
        if not channel_id or not token:
            return False

        url = f"https://api.telegram.org/bot{token}/getChatMember"
        params = {"chat_id": channel_id, "user_id": telegram_id}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                data = response.json()
        except Exception as exc:
            logger.error("premium_check_failed", error=str(exc))
            return False

        if not data.get("ok"):
            return False

        status = data.get("result", {}).get("status", "")
        return status in ("member", "administrator", "creator")

    async def sync_user_premium(self, user: User) -> User:
        is_member = await self.check_channel_membership(user.telegram_id)
        expires = user.premium_expires_at
        if expires and expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if expires and expires < datetime.now(timezone.utc):
            is_member = False
        return await self.user_repo.update_premium(user, is_member, expires)
