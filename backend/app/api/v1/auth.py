from fastapi import APIRouter, HTTPException, status

from app.core.config import get_settings
from app.core.deps import DbSession
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.integrations.telegram.auth import verify_telegram_init_data
from app.repositories.user_repository import UserRepository
from app.schemas.auth import RefreshRequest, TelegramAuthRequest, TokenResponse

router = APIRouter()

DEV_TELEGRAM_ID = 900000001


@router.post("/dev", response_model=TokenResponse)
async def auth_dev(db: DbSession):
    """Local development login (browser without Telegram)."""
    settings = get_settings()
    if settings.environment not in ("development", "dev", "local"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    repo = UserRepository(db)
    user = await repo.upsert_telegram_user(
        telegram_id=DEV_TELEGRAM_ID,
        username="dev_user",
        first_name="Dev",
    )
    return TokenResponse(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
    )


@router.post("/telegram", response_model=TokenResponse)
async def auth_telegram(body: TelegramAuthRequest, db: DbSession):
    settings = get_settings()
    if not settings.bot_token or settings.bot_token == "your_bot_token_here":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Bot token not configured. Use POST /auth/dev in development.",
        )
    user_data = verify_telegram_init_data(body.init_data, settings.bot_token)
    if not user_data or not user_data.get("telegram_id"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Telegram init data",
        )

    repo = UserRepository(db)
    user = await repo.upsert_telegram_user(
        telegram_id=int(user_data["telegram_id"]),
        username=user_data.get("username"),
        first_name=user_data.get("first_name"),
    )

    access = create_access_token(str(user.id))
    refresh = create_refresh_token(str(user.id))
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(body: RefreshRequest, db: DbSession):
    try:
        payload = decode_token(body.refresh_token)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        ) from exc

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    user_id = payload.get("sub")
    repo = UserRepository(db)
    user = await repo.get_by_id(int(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return TokenResponse(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
    )
