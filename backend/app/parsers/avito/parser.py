import json
import re
from datetime import datetime, timezone
from urllib.parse import quote

import httpx
from bs4 import BeautifulSoup

from app.core.config import get_settings
from app.core.proxy_manager import get_proxy_manager
from app.parsers.base.parser import BaseParser, RawListing

MOBILE_UA = (
    "Mozilla/5.0 (Linux; Android 13; SM-S918B) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
)

CITY_SLUGS = {
    "moscow": "moskva",
    "saint-petersburg": "sankt-peterburg",
    "novosibirsk": "novosibirsk",
}


class AvitoParser(BaseParser):
    source = "avito"

    async def _get_client(self) -> httpx.AsyncClient:
        proxy_mgr = get_proxy_manager()
        proxy = await proxy_mgr.get_proxy()
        proxies = proxy if proxy else None
        return httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={"User-Agent": MOBILE_UA},
            proxy=proxies,
        )

    async def _fetch_api(self, city: str, limit: int) -> list[RawListing]:
        city_slug = CITY_SLUGS.get(city, city)
        url = (
            f"https://www.avito.ru/web/1/main/items"
            f"?locationId={city_slug}&categoryId=0&limit={limit}"
        )
        async with await self._get_client() as client:
            response = await client.get(url)
            if response.status_code != 200:
                return []
            data = response.json()
            items = data.get("items", data.get("result", {}).get("items", []))
            return self._parse_api_items(items, city)

    def _parse_api_items(self, items: list, city: str) -> list[RawListing]:
        listings = []
        for item in items:
            item_id = str(item.get("id", item.get("item_id", "")))
            if not item_id:
                continue
            title = item.get("title", item.get("name", ""))
            price = item.get("price", item.get("priceDetailed", {}).get("value"))
            url_path = item.get("url", f"/{item_id}")
            url = url_path if url_path.startswith("http") else f"https://www.avito.ru{url_path}"
            images = []
            if item.get("images"):
                for img in item["images"]:
                    if isinstance(img, dict):
                        images.append(img.get("url", img.get("636x476", "")))
                    elif isinstance(img, str):
                        images.append(img)
            listings.append(
                RawListing(
                    source=self.source,
                    external_id=item_id,
                    title=title,
                    url=url,
                    price=float(price) if price else None,
                    city=city,
                    images=[i for i in images if i],
                    raw_data=item,
                )
            )
        return listings

    async def _fetch_mobile_html(self, city: str, limit: int) -> list[RawListing]:
        city_slug = CITY_SLUGS.get(city, city)
        url = f"https://m.avito.ru/{city_slug}/telefony"
        async with await self._get_client() as client:
            response = await client.get(url)
            if response.status_code != 200:
                return []
            return self._parse_html(response.text, city, limit)

    def _parse_html(self, html: str, city: str, limit: int) -> list[RawListing]:
        soup = BeautifulSoup(html, "lxml")
        listings = []
        for card in soup.select("[data-marker='item']")[:limit]:
            link = card.select_one("a[href*='/']")
            if not link:
                continue
            href = link.get("href", "")
            item_id_match = re.search(r"_(\d+)$", href) or re.search(r"/(\d+)$", href)
            item_id = item_id_match.group(1) if item_id_match else href
            title_el = card.select_one("[itemprop='name']") or card.select_one("h3")
            title = title_el.get_text(strip=True) if title_el else ""
            price_el = card.select_one("[itemprop='price']") or card.select_one(
                "[data-marker='item-price']"
            )
            price = None
            if price_el:
                price_text = re.sub(r"[^\d]", "", price_el.get_text())
                price = float(price_text) if price_text else None
            url = href if href.startswith("http") else f"https://www.avito.ru{href}"
            listings.append(
                RawListing(
                    source=self.source,
                    external_id=str(item_id),
                    title=title,
                    url=url,
                    price=price,
                    city=city,
                )
            )
        return listings

    async def fetch_new(self, city: str = "moscow", limit: int = 20) -> list[RawListing]:
        listings = await self._fetch_api(city, limit)
        if listings:
            return listings
        listings = await self._fetch_mobile_html(city, limit)
        if listings:
            return listings
        return await self._fetch_playwright_fallback(city, limit)

    async def _fetch_playwright_fallback(self, city: str, limit: int) -> list[RawListing]:
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            return []

        city_slug = CITY_SLUGS.get(city, city)
        url = f"https://m.avito.ru/{city_slug}/telefony"
        proxy_mgr = get_proxy_manager()
        proxy = await proxy_mgr.get_proxy()

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context_kwargs = {"user_agent": MOBILE_UA}
            if proxy:
                context_kwargs["proxy"] = {"server": proxy}
            context = await browser.new_context(**context_kwargs)
            page = await context.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            html = await page.content()
            await browser.close()
        return self._parse_html(html, city, limit)
