from decimal import Decimal

import httpx
import structlog

from app.core.config import get_settings
from app.models.listing import Listing

logger = structlog.get_logger(__name__)

SOURCE_EMOJI = {
    "avito": "🟢",
    "youla": "🔵",
    "telegram": "✈️",
    "vk": "🟦",
}


def format_listing_message(listing: Listing) -> str:
    emoji = SOURCE_EMOJI.get(listing.source, "📢")
    price_str = "Цена не указана"
    if listing.price is not None:
        price_str = f"{listing.price:,.0f} ₽".replace(",", " ")
    lines = [
        f"{emoji} <b>{listing.title}</b>",
        f"💰 {price_str}",
        f"📍 {listing.city or 'Город не указан'}",
        f"🔗 Источник: {listing.source.capitalize()}",
    ]
    if listing.brand:
        lines.append(f"🏷 {listing.brand}")
    return "\n".join(lines)


class TelegramNotificationService:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def send_listing(
        self, telegram_id: int, listing: Listing
    ) -> bool:
        token = self.settings.bot_token
        if not token:
            logger.warning("bot_token_missing")
            return False

        text = format_listing_message(listing)
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": telegram_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": False,
        }

        inline_keyboard = {
            "inline_keyboard": [[{"text": "Открыть объявление", "url": listing.url}]]
        }
        payload["reply_markup"] = inline_keyboard

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(url, json=payload)
            if response.status_code != 200:
                logger.error("send_message_failed", body=response.text)
                return False

            if listing.images:
                photo_url = listing.images[0] if isinstance(listing.images, list) else None
                if photo_url:
                    photo_resp = await client.post(
                        f"https://api.telegram.org/bot{token}/sendPhoto",
                        json={
                            "chat_id": telegram_id,
                            "photo": photo_url,
                            "caption": listing.title[:1024],
                        },
                    )
                    if photo_resp.status_code != 200:
                        logger.warning("send_photo_failed", body=photo_resp.text)

        return True
