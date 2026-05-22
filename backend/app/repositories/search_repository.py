from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.search import Search


class SearchRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, search_id: int) -> Search | None:
        result = await self.session.execute(select(Search).where(Search.id == search_id))
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: int) -> list[Search]:
        result = await self.session.execute(
            select(Search)
            .where(Search.user_id == user_id)
            .order_by(Search.created_at.desc())
        )
        return list(result.scalars().all())

    async def count_active_by_user(self, user_id: int) -> int:
        result = await self.session.execute(
            select(func.count())
            .select_from(Search)
            .where(Search.user_id == user_id, Search.active.is_(True))
        )
        return result.scalar_one()

    async def list_active_by_city_category(
        self, city: str, category: str | None = None
    ) -> list[Search]:
        query = select(Search).where(Search.active.is_(True), Search.city == city)
        if category:
            query = query.where(Search.category == category)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(self, search: Search) -> Search:
        self.session.add(search)
        await self.session.flush()
        return search

    async def delete(self, search: Search) -> None:
        await self.session.delete(search)
