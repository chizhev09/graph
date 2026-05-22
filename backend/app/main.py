from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.core.redis import close_redis
from app.db.init_db import init_database
from app.middleware.request_logging import RequestLoggingMiddleware

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    try:
        await init_database()
    except Exception as exc:
        logger.error("database_init_failed", error=str(exc))
        raise
    logger.info(
        "app_started",
        environment=settings.environment,
        database="sqlite" if settings.database_url.startswith("sqlite") else "postgresql",
    )
    yield
    await close_redis()


def create_app() -> FastAPI:
    settings = get_settings()
    setup_logging(settings.debug)

    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)

    @app.get("/api/health")
    async def health():
        return {"status": "ok", "environment": settings.environment}

    return app


app = create_app()
