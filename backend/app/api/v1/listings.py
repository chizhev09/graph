from fastapi import APIRouter, Query

from app.core.deps import CurrentUser, DbSession
from app.repositories.listing_repository import ListingRepository
from app.schemas.listing import ListingResponse

router = APIRouter()


@router.get("", response_model=list[ListingResponse])
async def list_listings(
    user: CurrentUser,
    db: DbSession,
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
):
    repo = ListingRepository(db)
    listings = await repo.list_recent(limit=limit, offset=offset)
    return listings
