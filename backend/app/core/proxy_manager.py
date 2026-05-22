import asyncio
import random
import time
from dataclasses import dataclass, field

import structlog

from app.core.config import get_settings

logger = structlog.get_logger(__name__)


@dataclass
class ProxyState:
    url: str
    failures: int = 0
    blacklisted_until: float = 0.0
    last_used: float = 0.0


class ProxyManager:
    """Rotate Webshare proxies with cooldown and blacklist."""

    def __init__(self, proxies: list[str] | None = None) -> None:
        settings = get_settings()
        urls = proxies or settings.proxy_list
        self._proxies: dict[str, ProxyState] = {u: ProxyState(url=u) for u in urls}
        self._lock = asyncio.Lock()
        self._cooldown_seconds = 60
        self._max_failures = 3
        self._blacklist_seconds = 300

    @property
    def has_proxies(self) -> bool:
        return bool(self._proxies)

    def _available(self) -> list[ProxyState]:
        now = time.monotonic()
        return [
            p
            for p in self._proxies.values()
            if p.blacklisted_until <= now
        ]

    async def get_proxy(self) -> str | None:
        async with self._lock:
            available = self._available()
            if not available:
                logger.warning("proxy_pool_exhausted")
                return None
            chosen = min(available, key=lambda p: p.last_used)
            chosen.last_used = time.monotonic()
            return chosen.url

    async def report_success(self, proxy_url: str) -> None:
        async with self._lock:
            if proxy_url in self._proxies:
                self._proxies[proxy_url].failures = 0

    async def report_failure(self, proxy_url: str) -> None:
        async with self._lock:
            state = self._proxies.get(proxy_url)
            if state is None:
                return
            state.failures += 1
            if state.failures >= self._max_failures:
                state.blacklisted_until = time.monotonic() + self._blacklist_seconds
                state.failures = 0
                logger.warning("proxy_blacklisted", proxy=proxy_url)

    async def health_check(self, check_fn) -> int:
        """Run check_fn(proxy_url) for each proxy; return healthy count."""
        healthy = 0
        for url in list(self._proxies.keys()):
            try:
                ok = await check_fn(url)
                if ok:
                    await self.report_success(url)
                    healthy += 1
                else:
                    await self.report_failure(url)
            except Exception:
                await self.report_failure(url)
        return healthy


_proxy_manager: ProxyManager | None = None


def get_proxy_manager() -> ProxyManager:
    global _proxy_manager
    if _proxy_manager is None:
        _proxy_manager = ProxyManager()
    return _proxy_manager
