import json
import re
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

from app.core.config import get_settings
from app.parsers.base.parser import BaseParser, RawListing

DATA_DIR = Path(__file__).resolve().parents[3] / "data"


class VKParser(BaseParser):
    source = "vk"

    def _load_sources(self) -> list[str]:
        path = DATA_DIR / "vk_sources.json"
        if not path.exists():
            return []
        return json.loads(path.read_text(encoding="utf-8"))

    def _extract_group_id(self, url: str) -> str | None:
        match = re.search(r"club(\d+)|public(\d+)|vk\.com/([\w.]+)", url)
        if match:
            return match.group(1) or match.group(2) or match.group(3)
        return None

    async def _fetch_api_posts(self, group_id: str, limit: int) -> list[RawListing]:
        settings = get_settings()
        token = settings.vk_access_token
        if not token:
            return []

        url = "https://api.vk.com/method/wall.get"
        params = {
            "access_token": token,
            "v": "5.131",
            "count": limit,
            "domain": group_id if not group_id.isdigit() else None,
            "owner_id": f"-{group_id}" if group_id.isdigit() else None,
        }
        params = {k: v for k, v in params.items() if v is not None}

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            data = response.json()
            posts = data.get("response", {}).get("items", [])
            listings = []
            for post in posts:
                text = post.get("text", "")
                if not text or len(text) < 10:
                    continue
                price = self._extract_price(text)
                post_id = f"{post.get('owner_id')}_{post.get('id')}"
                listings.append(
                    RawListing(
                        source=self.source,
                        external_id=post_id,
                        title=text[:120],
                        description=text,
                        url=f"https://vk.com/wall{post_id}",
                        price=price,
                        raw_data=post,
                    )
                )
            return listings

    def _extract_price(self, text: str) -> float | None:
        match = re.search(r"(\d[\d\s]{2,})\s*₽", text)
        if match:
            return float(re.sub(r"\s", "", match.group(1)))
        return None

    async def _fetch_html_fallback(self, url: str, limit: int) -> list[RawListing]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            if response.status_code != 200:
                return []
            soup = BeautifulSoup(response.text, "lxml")
            listings = []
            for post in soup.select(".wall_item")[:limit]:
                text_el = post.select_one(".wall_post_text")
                text = text_el.get_text(strip=True) if text_el else ""
                if len(text) < 10:
                    continue
                listings.append(
                    RawListing(
                        source=self.source,
                        external_id=text[:32],
                        title=text[:120],
                        description=text,
                        url=url,
                        price=self._extract_price(text),
                    )
                )
            return listings

    async def fetch_new(self, city: str = "moscow", limit: int = 10) -> list[RawListing]:
        all_listings: list[RawListing] = []
        for source_url in self._load_sources():
            group_id = self._extract_group_id(source_url)
            if not group_id:
                continue
            items = await self._fetch_api_posts(group_id, limit)
            if not items:
                items = await self._fetch_html_fallback(source_url, limit)
            for item in items:
                item.city = city
            all_listings.extend(items)
        return all_listings[:limit * 5]
