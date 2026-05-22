from fastapi import APIRouter

from app.core.config import get_settings
from app.core.deps import CurrentUser, DbSession
from app.repositories.search_repository import SearchRepository
from app.repositories.user_repository import UserRepository
from app.schemas.subscription import SubscriptionStatus
from app.services.limit_service import LimitService
from app.services.premium_service import PremiumService

router = APIRouter()


@router.get("/status", response_model=SubscriptionStatus)
async def subscription_status(user: CurrentUser, db: DbSession):
    settings = get_settings()
    search_repo = SearchRepository(db)
    limit_service = LimitService(UserRepository(db))
    user = await limit_service.ensure_reset(user)
    active = await search_repo.count_active_by_user(user.id)

    return SubscriptionStatus(
        is_premium=user.is_premium,
        premium_expires_at=user.premium_expires_at,
        daily_notifications_used=user.daily_notifications_used,
        daily_notifications_limit=None if user.is_premium else settings.free_daily_notifications,
        notifications_remaining=limit_service.notifications_remaining(user),
        max_searches=999 if user.is_premium else settings.free_max_searches,
        active_searches=active,
    )


@router.post("/check")
async def check_subscription(user: CurrentUser, db: DbSession):
    repo = UserRepository(db)
    premium = PremiumService(repo)
    user = await premium.sync_user_premium(user)
    return {
        "is_premium": user.is_premium,
        "message": "Premium active" if user.is_premium else "Join premium channel for unlimited access",
    }


@router.post("/upgrade")
async def upgrade_info():
    return {
        "message": "Join the premium Telegram channel to unlock unlimited notifications",
        "price_rub": 2990,
        "period": "monthly",
    }
