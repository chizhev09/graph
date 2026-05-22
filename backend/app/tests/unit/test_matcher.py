import pytest
from decimal import Decimal
from unittest.mock import AsyncMock, patch

from app.matcher.engine import MatcherEngine
from app.models.listing import Listing
from app.models.search import Search
from app.models.user import User


@pytest.mark.asyncio
async def test_matcher_matches_brand_and_city(db_session):
    user = User(telegram_id=111, username="u", first_name="U")
    db_session.add(user)
    await db_session.flush()

    search = Search(
        user_id=user.id,
        city="moscow",
        category="phones",
        brands=["Apple"],
        exclusions=[],
        source_types=["avito"],
        active=True,
    )
    db_session.add(search)
    await db_session.flush()

    listing = Listing(
        source="avito",
        external_id="1",
        title="iPhone 15 Pro",
        url="https://avito.ru/1",
        city="moscow",
        category="phones",
        brand="apple",
        price=Decimal("80000"),
        hash="abc123hash",
        images=[],
    )
    db_session.add(listing)
    await db_session.flush()

    engine = MatcherEngine(db_session)
    matches = await engine.find_matches(listing)
    assert len(matches) >= 1


@pytest.mark.asyncio
async def test_matcher_excludes_reseller(db_session):
    user = User(telegram_id=222, username="u2", first_name="U2")
    db_session.add(user)
    await db_session.flush()

    search = Search(
        user_id=user.id,
        city="moscow",
        category="phones",
        brands=["Apple"],
        exclusions=["resellers"],
        source_types=["avito"],
        active=True,
    )
    db_session.add(search)
    await db_session.flush()

    listing = Listing(
        source="avito",
        external_id="2",
        title="iPhone перекуп срочно",
        description="перекуп",
        url="https://avito.ru/2",
        city="moscow",
        category="phones",
        brand="apple",
        hash="def456hash",
        images=[],
    )
    db_session.add(listing)
    await db_session.flush()

    engine = MatcherEngine(db_session)
    matches = await engine.find_matches(listing)
    assert len(matches) == 0
