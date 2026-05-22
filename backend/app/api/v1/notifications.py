from fastapi import APIRouter

from app.core.config import get_settings
from app.core.deps import CurrentUser, DbSession
from app.repositories.user_repository import UserRepository
from app.services.limit_service import LimitService

router = APIRouter()


@router.get("/status")
async def notification_status(user: CurrentUser, db: DbSession):
    settings = get_settings()
    limit_service = LimitService(UserRepository(db))
    user = await limit_service.ensure_reset(user)
    remaining = limit_service.notifications_remaining(user)
    return {
        "daily_notifications_used": user.daily_notifications_used,
        "daily_notifications_limit": None if user.is_premium else settings.free_daily_notifications,
        "notifications_remaining": remaining,
        "is_premium": user.is_premium,
    }
