from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.listing import Listing, ListingMatch


class ListingRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_hash(self, listing_hash: str) -> Listing | None:
        result = await self.session.execute(
            select(Listing).where(Listing.hash == listing_hash)
        )
        return result.scalar_one_or_none()

    async def get_by_source_external(
        self, source: str, external_id: str
    ) -> Listing | None:
        result = await self.session.execute(
            select(Listing).where(
                Listing.source == source, Listing.external_id == external_id
            )
        )
        return result.scalar_one_or_none()

    async def create(self, listing: Listing) -> Listing:
        self.session.add(listing)
        await self.session.flush()
        return listing

    async def list_recent(self, limit: int = 50, offset: int = 0) -> list[Listing]:
        result = await self.session.execute(
            select(Listing).order_by(Listing.created_at.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def create_match(self, match: ListingMatch) -> ListingMatch:
        self.session.add(match)
        await self.session.flush()
        return match

    async def mark_sent(self, listing: Listing) -> Listing:
        listing.is_sent = True
        await self.session.flush()
        return listing
