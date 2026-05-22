from datetime import datetime

from pydantic import BaseModel


class SubscriptionStatus(BaseModel):
    is_premium: bool
    premium_expires_at: datetime | None
    daily_notifications_used: int
    daily_notifications_limit: int | None
    notifications_remaining: int | None
    max_searches: int
    active_searches: int
