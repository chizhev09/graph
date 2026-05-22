import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class RawListing:
    source: str
    external_id: str
    title: str
    url: str
    description: str | None = None
    price: float | None = None
    city: str | None = None
    images: list[str] = field(default_factory=list)
    category: str | None = None
    brand: str | None = None
    published_at: datetime | None = None
    raw_data: dict[str, Any] | None = None


class BaseParser(ABC):
    source: str = "unknown"
    max_retries: int = 3

    def __init__(self) -> None:
        self.log = logger.bind(source=self.source)

    @abstractmethod
    async def fetch_new(self, city: str = "moscow", limit: int = 20) -> list[RawListing]:
        pass

    async def run_with_retries(
        self, city: str = "moscow", limit: int = 20
    ) -> list[RawListing]:
        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                listings = await self.fetch_new(city=city, limit=limit)
                self.log.info("parser_success", count=len(listings), attempt=attempt)
                return listings
            except Exception as exc:
                last_error = exc
                self.log.warning("parser_retry", attempt=attempt, error=str(exc))
                await asyncio.sleep(2 ** attempt)
        if last_error:
            raise last_error
        return []
