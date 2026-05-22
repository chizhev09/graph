import re

import httpx
from bs4 import BeautifulSoup

from app.core.proxy_manager import get_proxy_manager
from app.parsers.base.parser import BaseParser, RawListing

MOBILE_UA = (
    "Mozilla/5.0 (Linux; Android 13; Pixel 7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
)


class YoulaParser(BaseParser):
    source = "youla"

    async def _get_client(self) -> httpx.AsyncClient:
        proxy_mgr = get_proxy_manager()
        proxy = await proxy_mgr.get_proxy()
        return httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={"User-Agent": MOBILE_UA},
            proxy=proxy if proxy else None,
        )

    async def _fetch_api(self, city: str, limit: int) -> list[RawListing]:
        url = f"https://youla.ru/web-api/products?city={city}&category=elektronika&limit={limit}"
        async with await self._get_client() as client:
            response = await client.get(url)
            if response.status_code != 200:
                return []
            try:
                data = response.json()
            except Exception:
                return []
            products = data.get("data", data.get("products", []))
            listings = []
            for p in products[:limit]:
                pid = str(p.get("id", p.get("_id", "")))
                if not pid:
                    continue
                listings.append(
                    RawListing(
                        source=self.source,
                        external_id=pid,
                        title=p.get("name", p.get("title", "")),
                        url=p.get("url", f"https://youla.ru/product/{pid}"),
                        price=float(p.get("price", 0) or 0) or None,
                        city=city,
                        images=p.get("images", []),
                        raw_data=p,
                    )
                )
            return listings

    async def _fetch_mobile_html(self, city: str, limit: int) -> list[RawListing]:
        url = f"https://youla.ru/{city}/elektronika"
        async with await self._get_client() as client:
            response = await client.get(url)
            if response.status_code != 200:
                return []
            soup = BeautifulSoup(response.text, "lxml")
            listings = []
            for card in soup.select("[data-test-component='ProductOrAdCard']")[:limit]:
                link = card.select_one("a[href]")
                if not link:
                    continue
                href = link.get("href", "")
                pid_match = re.search(r"product/([a-f0-9-]+)", href)
                pid = pid_match.group(1) if pid_match else href
                title = card.get_text(strip=True)[:200]
                listings.append(
                    RawListing(
                        source=self.source,
                        external_id=str(pid),
                        title=title,
                        url=href if href.startswith("http") else f"https://youla.ru{href}",
                        city=city,
                    )
                )
            return listings

    async def fetch_new(self, city: str = "moscow", limit: int = 20) -> list[RawListing]:
        listings = await self._fetch_api(city, limit)
        if listings:
            return listings
        return await self._fetch_mobile_html(city, limit)
