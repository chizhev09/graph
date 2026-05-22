from datetime import datetime, timezone
from decimal import Decimal

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.matcher.engine import MatcherEngine
from app.models.listing import Listing
from app.notifications.telegram_bot import TelegramNotificationService
from app.parsers.base.parser import RawListing
from app.repositories.listing_repository import ListingRepository
from app.repositories.user_repository import UserRepository
from app.services.categorization_service import CategorizationService
from app.services.dedup_service import DedupService
from app.services.limit_service import LimitService

logger = structlog.get_logger(__name__)


class ListingIngestService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.listing_repo = ListingRepository(session)
        self.user_repo = UserRepository(session)
        self.dedup = DedupService(self.listing_repo)
        self.categorizer = CategorizationService()
        self.matcher = MatcherEngine(session)
        self.notifier = TelegramNotificationService()
        self.limit_service = LimitService(self.user_repo)

    async def ingest(self, raw: RawListing) -> Listing | None:
        price_str = str(raw.price) if raw.price is not None else None
        if await self.dedup.is_duplicate(raw.source, raw.external_id, raw.title, price_str):
            logger.debug("duplicate_skipped", source=raw.source, id=raw.external_id)
            return None

        h = await self.dedup.mark_seen(raw.source, raw.external_id, raw.title, price_str)
        cat = self.categorizer.categorize(raw.title, raw.description)

        listing = Listing(
            source=raw.source,
            external_id=raw.external_id,
            title=raw.title,
            description=raw.description,
            price=Decimal(str(raw.price)) if raw.price is not None else None,
            city=raw.city,
            url=raw.url,
            images=raw.images or [],
            category=cat.get("category") or raw.category,
            subcategory=cat.get("subcategory"),
            brand=cat.get("brand") or raw.brand,
            model=cat.get("model"),
            published_at=raw.published_at,
            hash=h,
            raw_data=raw.raw_data,
        )
        listing = await self.listing_repo.create(listing)
        matches = await self.matcher.process_listing(listing)

        for match in matches:
            user = await self.user_repo.get_by_id(match.user_id)
            if user is None:
                continue
            sent = await self.notifier.send_listing(user.telegram_id, listing)
            if sent:
                match.notified_at = datetime.now(timezone.utc)
                await self.limit_service.record_notification(user)

        await self.session.flush()
        return listing
