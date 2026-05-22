from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Graph API"
    debug: bool = False
    environment: str = "development"

    database_url: str = Field(
        default="postgresql+asyncpg://graph:graph@localhost:5432/graph",
        alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    bot_token: str = Field(default="", alias="BOT_TOKEN")
    web_app_url: str = Field(default="https://pushes.su", alias="WEB_APP_URL")
    telegram_api_id: int = Field(default=0, alias="TELEGRAM_API_ID")
    telegram_api_hash: str = Field(default="", alias="TELEGRAM_API_HASH")
    premium_channel_id: str = Field(default="", alias="PREMIUM_CHANNEL_ID")

    jwt_secret: str = Field(default="change-me-in-production", alias="JWT_SECRET")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 30

    webshare_proxies: str = Field(default="", alias="WEBSHARE_PROXIES")
    vk_access_token: str = Field(default="", alias="VK_ACCESS_TOKEN")

    cors_origins: str = Field(
        default="http://localhost:5173,http://localhost:3000",
        alias="CORS_ORIGINS",
    )

    free_daily_notifications: int = 5
    free_max_searches: int = 3

    parser_avito_interval_seconds: int = 120
    parser_youla_interval_seconds: int = 120
    parser_vk_interval_seconds: int = 180
    parser_concurrency_limit: int = 5

    default_city: str = "moscow"

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def proxy_list(self) -> List[str]:
        if not self.webshare_proxies.strip():
            return []
        return [p.strip() for p in self.webshare_proxies.split(",") if p.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
