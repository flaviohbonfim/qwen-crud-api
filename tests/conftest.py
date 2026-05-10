import uuid
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, AsyncConnection, create_async_engine

from app.api.deps import get_db
from main import app
from app.models.user import Base


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine: AsyncEngine = create_async_engine(TEST_DATABASE_URL, echo=False)


@pytest_asyncio.fixture
async def test_engine_instance() -> AsyncEngine:
    return test_engine


@pytest_asyncio.fixture
async def test_db_session(test_engine_instance: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    async with test_engine_instance.begin() as conn:
        session = AsyncSession(conn, expire_on_commit=False)
        yield session
        await session.rollback()


@pytest_asyncio.fixture(autouse=True)
async def setup_database(test_engine_instance: AsyncEngine) -> AsyncGenerator[None, None]:
    async with test_engine_instance.connect() as conn:
        await conn.run_sync(Base.metadata.create_all)
        yield
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def user_data() -> dict:
    return {
        "name": "John Doe",
        "email": "john@example.com",
        "password": "Password123",
    }


@pytest.fixture
def valid_update_data() -> dict:
    return {
        "name": "Jane Doe",
        "email": "jane@example.com",
    }


@pytest_asyncio.fixture
async def api_client(test_db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield test_db_session

    app.dependency_overrides[get_db] = _override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
