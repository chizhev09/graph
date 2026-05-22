from redis import asyncio as aioredis

from app.core.redis import get_redis
from app.repositories.listing_repository import ListingRepository
from app.utils.hashing import listing_hash


class DedupService:
    DEDUP_TTL = 7 * 24 * 3600

    def __init__(self, listing_repo: ListingRepository) -> None:
        self.listing_repo = listing_repo

    async def is_duplicate(
        self,
        source: str,
        external_id: str,
        title: str,
        price: str | None = None,
    ) -> bool:
        h = listing_hash(source, external_id, title, price)
        existing = await self.listing_repo.get_by_hash(h)
        if existing:
            return True

        redis = await get_redis()
        if redis is not None:
            cache_key = f"dedup:{h}"
            if await redis.exists(cache_key):
                return True

        by_external = await self.listing_repo.get_by_source_external(source, external_id)
        return by_external is not None

    async def mark_seen(
        self,
        source: str,
        external_id: str,
        title: str,
        price: str | None = None,
    ) -> str:
        h = listing_hash(source, external_id, title, price)
        redis = await get_redis()
        if redis is not None:
            await redis.setex(f"dedup:{h}", self.DEDUP_TTL, "1")
        return h
