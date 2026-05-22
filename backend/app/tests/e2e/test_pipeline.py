import pytest
from decimal import Decimal
from unittest.mock import AsyncMock, patch

from app.models.search import Search
from app.models.user import User
from app.parsers.base.parser import RawListing
from app.services.listing_ingest_service import ListingIngestService


@pytest.mark.asyncio
async def test_e2e_listing_to_match(db_session):
    user = User(telegram_id=999001, username="e2e", first_name="E2E", is_premium=True)
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

    raw = RawListing(
        source="avito",
        external_id="e2e-001",
        title="Apple iPhone 15 Pro Max 256GB",
        description="Excellent condition",
        url="https://avito.ru/e2e-001",
        price=85000.0,
        city="moscow",
        brand="apple",
        category="phones",
        images=[],
    )

    with patch(
        "app.services.listing_ingest_service.TelegramNotificationService.send_listing",
        new_callable=AsyncMock,
    ) as mock_send:
        mock_send.return_value = True
        ingest = ListingIngestService(db_session)
        listing = await ingest.ingest(raw)
        await db_session.commit()

    assert listing is not None
    assert listing.category == "phones"
    mock_send.assert_called()
    assert mock_send.call_args[0][0] == user.telegram_id


@pytest.mark.asyncio
async def test_e2e_free_limit_blocks_notification(db_session):
    user = User(
        telegram_id=999002,
        username="free",
        first_name="Free",
        is_premium=False,
        daily_notifications_used=5,
    )
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

    raw = RawListing(
        source="avito",
        external_id="e2e-002",
        title="Apple iPhone 14",
        url="https://avito.ru/e2e-002",
        price=60000.0,
        city="moscow",
    )

    with patch(
        "app.services.listing_ingest_service.TelegramNotificationService.send_listing",
        new_callable=AsyncMock,
    ) as mock_send:
        ingest = ListingIngestService(db_session)
        await ingest.ingest(raw)
        await db_session.commit()
        mock_send.assert_not_called()
