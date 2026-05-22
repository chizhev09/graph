import asyncio
import os
from collections.abc import AsyncGenerator
from typing import Any

import fakeredis.aioredis
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core import redis as redis_module
from app.core.config import get_settings
from app.core.deps import get_db
from app.db.base import Base
from app.main import create_app

os.environ.setdefault("BOT_TOKEN", "test-bot-token-for-pytest")
os.environ.setdefault("JWT_SECRET", "test-jwt-secret-key")
get_settings.cache_clear()

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def fake_redis():
    redis_module._redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
    yield
    await redis_module.close_redis()


@pytest_asyncio.fixture
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    app = create_app()

    async def override_get_db():
        yield db_session
        await db_session.commit()

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def mock_telegram_user() -> dict[str, Any]:
    return {
        "telegram_id": 123456789,
        "username": "testuser",
        "first_name": "Test",
    }
