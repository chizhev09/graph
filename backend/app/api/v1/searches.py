from fastapi import APIRouter, HTTPException, status

from app.core.config import get_settings
from app.core.deps import CurrentUser, DbSession
from app.models.search import Search
from app.repositories.search_repository import SearchRepository
from app.repositories.user_repository import UserRepository
from app.schemas.search import SearchCreate, SearchResponse, SearchUpdate
from app.services.limit_service import LimitService

router = APIRouter()


@router.get("", response_model=list[SearchResponse])
async def list_searches(user: CurrentUser, db: DbSession):
    repo = SearchRepository(db)
    searches = await repo.list_by_user(user.id)
    return searches


@router.post("", response_model=SearchResponse, status_code=status.HTTP_201_CREATED)
async def create_search(
    body: SearchCreate, user: CurrentUser, db: DbSession
):
    settings = get_settings()
    search_repo = SearchRepository(db)
    user_repo = UserRepository(db)
    limit_service = LimitService(user_repo)

    active_count = await search_repo.count_active_by_user(user.id)
    if body.active and not limit_service.can_create_search(user, active_count):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Active search limit reached. Upgrade to premium.",
        )

    search = Search(
        user_id=user.id,
        city=body.city or settings.default_city,
        category=body.category,
        brands=body.brands,
        exclusions=body.exclusions,
        min_price=body.min_price,
        max_price=body.max_price,
        keywords=body.keywords,
        exclude_keywords=body.exclude_keywords,
        condition=body.condition,
        source_types=body.source_types or ["avito", "youla", "telegram", "vk"],
        active=body.active,
    )
    search = await search_repo.create(search)
    return search


@router.patch("/{search_id}", response_model=SearchResponse)
async def update_search(
    search_id: int, body: SearchUpdate, user: CurrentUser, db: DbSession
):
    repo = SearchRepository(db)
    search = await repo.get_by_id(search_id)
    if search is None or search.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Search not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(search, field, value)
    await db.flush()
    return search


@router.delete("/{search_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_search(search_id: int, user: CurrentUser, db: DbSession):
    repo = SearchRepository(db)
    search = await repo.get_by_id(search_id)
    if search is None or search.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Search not found")
    await repo.delete(search)
