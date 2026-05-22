from fastapi import APIRouter

from app.core.config import get_settings
from app.core.deps import CurrentUser, DbSession
from app.repositories.search_repository import SearchRepository
from app.schemas.user import UserProfile
from app.services.limit_service import LimitService
from app.repositories.user_repository import UserRepository

router = APIRouter()


@router.get("", response_model=UserProfile)
async def get_profile(user: CurrentUser, db: DbSession):
    settings = get_settings()
    search_repo = SearchRepository(db)
    limit_service = LimitService(UserRepository(db))
    active = await search_repo.count_active_by_user(user.id)

    return UserProfile(
        id=user.id,
        telegram_id=user.telegram_id,
        username=user.username,
        first_name=user.first_name,
        is_premium=user.is_premium,
        premium_expires_at=user.premium_expires_at,
        daily_notifications_used=user.daily_notifications_used,
        notifications_remaining=limit_service.notifications_remaining(user),
        max_searches=999 if user.is_premium else settings.free_max_searches,
        active_searches=active,
        created_at=user.created_at,
    )
