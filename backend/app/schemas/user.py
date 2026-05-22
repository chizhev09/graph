from datetime import datetime

from pydantic import BaseModel


class UserProfile(BaseModel):
    id: int
    telegram_id: int
    username: str | None
    first_name: str | None
    is_premium: bool
    premium_expires_at: datetime | None
    daily_notifications_used: int
    notifications_remaining: int | None
    max_searches: int
    active_searches: int
    created_at: datetime

    model_config = {"from_attributes": True}
