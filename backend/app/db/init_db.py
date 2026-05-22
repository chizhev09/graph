import structlog

from app.db.base import Base
from app.db.session import engine
from app.models import Listing, ListingMatch, ParserHealth, Search, User  # noqa: F401

logger = structlog.get_logger(__name__)


async def init_database() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("database_tables_ready")
