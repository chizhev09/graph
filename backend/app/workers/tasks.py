import asyncio
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select

from app.core.config import get_settings
from app.db.session import async_session_factory
from app.models.listing import Listing
from app.models.parser_health import ParserHealth
from app.models.user import User
from app.parsers.avito.parser import AvitoParser
from app.parsers.youla.parser import YoulaParser
from app.parsers.vk.parser import VKParser
from app.repositories.user_repository import UserRepository
from app.services.listing_ingest_service import ListingIngestService
from app.services.premium_service import PremiumService
from app.workers.celery_app import celery_app


def run_async(coro):
    return asyncio.run(coro)


async def _update_parser_health(session, source: str, status: str, count: int, error: str | None = None):
    result = await session.execute(
        select(ParserHealth).where(ParserHealth.source == source)
    )
    health = result.scalar_one_or_none()
    if health is None:
        health = ParserHealth(source=source)
        session.add(health)
    health.status = status
    health.last_run_at = datetime.now(timezone.utc)
    health.listings_found = count
    health.last_error = error
    await session.flush()


async def _run_parser(parser_cls, source: str, city: str = "moscow"):
    settings = get_settings()
    parser = parser_cls()
    async with async_session_factory() as session:
        try:
            listings = await parser.run_with_retries(city=city, limit=20)
            ingest = ListingIngestService(session)
            ingested = 0
            for raw in listings:
                result = await ingest.ingest(raw)
                if result:
                    ingested += 1
            await _update_parser_health(session, source, "ok", ingested)
            await session.commit()
            return ingested
        except Exception as exc:
            await _update_parser_health(session, source, "error", 0, str(exc))
            await session.commit()
            raise


@celery_app.task(name="app.workers.tasks.run_avito_parser")
def run_avito_parser(city: str = "moscow"):
    return run_async(_run_parser(AvitoParser, "avito", city))


@celery_app.task(name="app.workers.tasks.run_youla_parser")
def run_youla_parser(city: str = "moscow"):
    return run_async(_run_parser(YoulaParser, "youla", city))


@celery_app.task(name="app.workers.tasks.run_vk_parser")
def run_vk_parser(city: str = "moscow"):
    return run_async(_run_parser(VKParser, "vk", city))


@celery_app.task(name="app.workers.tasks.process_listing")
def process_listing(listing_data: dict):
    from app.parsers.base.parser import RawListing

    raw = RawListing(**listing_data)

    async def _process():
        async with async_session_factory() as session:
            ingest = ListingIngestService(session)
            await ingest.ingest(raw)
            await session.commit()

    return run_async(_process())


@celery_app.task(name="app.workers.tasks.reset_daily_limits")
def reset_daily_limits():
    async def _reset():
        async with async_session_factory() as session:
            repo = UserRepository(session)
            result = await session.execute(select(User))
            users = result.scalars().all()
            for user in users:
                await repo.reset_daily_limits(user)
            await session.commit()

    return run_async(_reset())


@celery_app.task(name="app.workers.tasks.sync_premium_membership")
def sync_premium_membership():
    async def _sync():
        async with async_session_factory() as session:
            repo = UserRepository(session)
            premium = PremiumService(repo)
            result = await session.execute(select(User))
            users = result.scalars().all()
            for user in users:
                await premium.sync_user_premium(user)
            await session.commit()

    return run_async(_sync())


@celery_app.task(name="app.workers.tasks.cleanup_old_listings")
def cleanup_old_listings():
    async def _cleanup():
        cutoff = datetime.now(timezone.utc) - timedelta(days=30)
        async with async_session_factory() as session:
            await session.execute(delete(Listing).where(Listing.created_at < cutoff))
            await session.commit()

    return run_async(_cleanup())
