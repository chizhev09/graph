import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.core.config import get_settings
from bot.handlers import start_router

logger = logging.getLogger(__name__)


async def _run() -> None:
    settings = get_settings()
    if not settings.bot_token or settings.bot_token.startswith("your_"):
        logger.error("BOT_TOKEN is not configured")
        sys.exit(1)

    if not settings.web_app_url.strip():
        logger.error("WEB_APP_URL is not configured")
        sys.exit(1)

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp.include_router(start_router)

    logger.info("bot_polling_started web_app_url=%s", settings.web_app_url)
    await dp.start_polling(bot)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    asyncio.run(_run())


if __name__ == "__main__":
    main()
