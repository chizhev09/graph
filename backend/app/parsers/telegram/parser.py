import json
import re
from pathlib import Path

from app.parsers.base.parser import BaseParser, RawListing

DATA_DIR = Path(__file__).resolve().parents[3] / "data"


class TelegramMessageParser:
    """Parse Telegram message text into RawListing."""

    @staticmethod
    def parse_message(
        text: str,
        message_id: int,
        channel: str,
        images: list[str] | None = None,
    ) -> RawListing | None:
        if not text or len(text) < 10:
            return None
        price = TelegramMessageParser._extract_price(text)
        url = TelegramMessageParser._extract_url(text) or f"https://t.me/{channel}/{message_id}"
        title = text.split("\n")[0][:200]
        city = TelegramMessageParser._extract_city(text)
        return RawListing(
            source="telegram",
            external_id=f"{channel}_{message_id}",
            title=title,
            description=text,
            url=url,
            price=price,
            city=city,
            images=images or [],
            raw_data={"text": text, "channel": channel},
        )

    @staticmethod
    def _extract_price(text: str) -> float | None:
        patterns = [
            r"(\d[\d\s]{2,})\s*₽",
            r"(\d[\d\s]{2,})\s*руб",
            r"price[:\s]+(\d+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return float(re.sub(r"\s", "", match.group(1)))
        return None

    @staticmethod
    def _extract_url(text: str) -> str | None:
        match = re.search(r"https?://[^\s]+", text)
        return match.group(0) if match else None

    @staticmethod
    def _extract_city(text: str) -> str | None:
        match = re.search(
            r"(москва|спб|санкт-петербург|новосибирск|екатеринбург|казань)",
            text,
            re.IGNORECASE,
        )
        if match:
            cities = {
                "москва": "moscow",
                "спб": "saint-petersburg",
                "санкт-петербург": "saint-petersburg",
                "новосибирск": "novosibirsk",
                "екатеринбург": "yekaterinburg",
                "казань": "kazan",
            }
            return cities.get(match.group(1).lower())
        return None


def load_telegram_sources() -> list[str]:
    path = DATA_DIR / "telegram_sources.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))
