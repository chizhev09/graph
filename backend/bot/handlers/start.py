from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo

from app.core.config import get_settings

router = Router(name="start")

START_TEXT = (
    "Добро пожаловать в <b>Graph</b>.\n\n"
    "Настройте фильтры по технике и получайте уведомления "
    "о новых объявлениях в Telegram раньше других."
)


def _open_app_keyboard(web_app_url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Открыть",
                    web_app=WebAppInfo(url=web_app_url),
                )
            ]
        ]
    )


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    settings = get_settings()
    await message.answer(
        START_TEXT,
        reply_markup=_open_app_keyboard(settings.web_app_url),
        parse_mode="HTML",
    )
