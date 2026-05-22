"""Telethon realtime listener — run as separate process."""

import asyncio
import json
import re
from pathlib import Path

import structlog
from redis import asyncio as aioredis
from telethon import TelegramClient, events

from app.core.config import get_settings
from app.parsers.telegram.parser import TelegramMessageParser, load_telegram_sources

logger = structlog.get_logger(__name__)
DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def _channel_from_url(url: str) -> str:
    match = re.search(r"t\.me/([\w_]+)", url)
    return match.group(1) if match else url


async def publish_listing(redis: aioredis.Redis, listing_data: dict) -> None:
    await redis.lpush("listings:telegram", json.dumps(listing_data, default=str))


async def main() -> None:
    settings = get_settings()
    if not settings.telegram_api_id or not settings.telegram_api_hash:
        logger.error("telegram_api_credentials_missing")
        return

    session_path = str(DATA_DIR / "telegram_session")
    client = TelegramClient(
        session_path,
        settings.telegram_api_id,
        settings.telegram_api_hash,
    )
    redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    sources = load_telegram_sources()
    channels = [_channel_from_url(u) for u in sources]

    @client.on(events.NewMessage(chats=channels or None))
    async def handler(event):
        text = event.message.message or ""
        channel = _channel_from_url(
            sources[0] if sources else "channel"
        )
        if event.chat:
            username = getattr(event.chat, "username", None)
            if username:
                channel = username
        listing = TelegramMessageParser.parse_message(
            text, event.message.id, channel
        )
        if listing:
            await publish_listing(redis, listing.__dict__)
            logger.info("telegram_listing_queued", channel=channel)

    await client.start()
    logger.info("telegram_listener_started", channels=channels)
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
