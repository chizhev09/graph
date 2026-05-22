import re
from decimal import Decimal

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.listing import Listing, ListingMatch
from app.models.search import Search
from app.repositories.listing_repository import ListingRepository
from app.repositories.search_repository import SearchRepository
from app.services.limit_service import LimitService
from app.repositories.user_repository import UserRepository

logger = structlog.get_logger(__name__)

EXCLUSION_PATTERNS = {
    "resellers": [r"перекуп", r"trade.?in", r"обмен"],
    "shops": [r"магазин", r"салон", r"официальн"],
    "companies": [r"ооо", r"ип\s", r"компания"],
    "wholesale": [r"оптом", r"опт\b", r"партия"],
    "dealers": [r"дилер", r"дистрибьютор"],
    "delivery-only": [r"только доставк", r"доставка по"],
}


class MatcherEngine:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.search_repo = SearchRepository(session)
        self.listing_repo = ListingRepository(session)
        self.user_repo = UserRepository(session)
        self.limit_service = LimitService(self.user_repo)

    def _text(self, listing: Listing) -> str:
        return f"{listing.title} {listing.description or ''}".lower()

    def _matches_exclusions(self, text: str, exclusions: list) -> bool:
        for exc_id in exclusions:
            patterns = EXCLUSION_PATTERNS.get(exc_id, [])
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return True
        return False

    def _matches_keywords(self, text: str, keywords: str | None, exclude: str | None) -> bool:
        if keywords:
            for kw in keywords.lower().split(","):
                kw = kw.strip()
                if kw and kw not in text:
                    return False
        if exclude:
            for kw in exclude.lower().split(","):
                kw = kw.strip()
                if kw and kw in text:
                    return False
        return True

    def _matches_price(
        self, price: Decimal | None, min_p: Decimal | None, max_p: Decimal | None
    ) -> bool:
        if price is None:
            return min_p is None and max_p is None
        if min_p is not None and price < min_p:
            return False
        if max_p is not None and price > max_p:
            return False
        return True

    def _matches_search(self, listing: Listing, search: Search) -> bool:
        if search.city and listing.city and search.city != listing.city:
            return False
        if search.category and listing.category and search.category != listing.category:
            return False
        if search.brands and listing.brand:
            brand_slugs = [b.lower().replace(" ", "_") for b in search.brands]
            if listing.brand.lower() not in brand_slugs and listing.brand not in search.brands:
                normalized = listing.brand.replace("_", " ").lower()
                if not any(b.lower() in normalized for b in search.brands):
                    return False
        elif search.brands and not listing.brand:
            return False
        if search.source_types and listing.source not in search.source_types:
            return False
        text = self._text(listing)
        if self._matches_exclusions(text, search.exclusions or []):
            return False
        if not self._matches_keywords(text, search.keywords, search.exclude_keywords):
            return False
        if not self._matches_price(listing.price, search.min_price, search.max_price):
            return False
        return True

    async def find_matches(self, listing: Listing) -> list[tuple[Search, int]]:
        city = listing.city or ""
        searches = await self.search_repo.list_active_by_city_category(
            city, listing.category
        )
        if not searches and city:
            searches = await self.search_repo.list_active_by_city_category(city, None)

        matches = []
        for search in searches:
            if self._matches_search(listing, search):
                matches.append((search, search.user_id))
        return matches

    async def process_listing(self, listing: Listing) -> list[ListingMatch]:
        matches = await self.find_matches(listing)
        created = []
        for search, user_id in matches:
            user = await self.user_repo.get_by_id(user_id)
            if user is None:
                continue
            if not await self.limit_service.can_send_notification(user):
                logger.info("notification_limit_reached", user_id=user_id)
                continue
            match = ListingMatch(
                listing_id=listing.id,
                search_id=search.id,
                user_id=user_id,
            )
            created.append(await self.listing_repo.create_match(match))
        return created
