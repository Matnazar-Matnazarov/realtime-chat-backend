"""
Pytest configuration and fixtures.

Professional async database setup with proper transaction handling.
All fixtures are properly scoped and isolated for test reliability.
"""

import asyncio
import os
import sys
import time
from collections.abc import AsyncGenerator, Generator
from uuid import uuid4

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from fastapi_users.password import PasswordHelper
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

# Disable uvloop for pytest to avoid event loop conflicts
# Tests use standard asyncio event loop for better compatibility
# This ensures pytest-asyncio works correctly without uvloop interference
# Set PYTEST_CURRENT_TEST environment variable BEFORE importing app.main
# This prevents uvloop from being configured in app/main.py
os.environ["PYTEST_CURRENT_TEST"] = "1"

# Set event loop policy to default (not uvloop) before any imports
asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

# Remove uvloop from sys.modules if already imported
if "uvloop" in sys.modules:
    del sys.modules["uvloop"]

from app.core.config import settings  # noqa: E402
from app.db.base import AsyncSessionLocal, Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models.user import User  # noqa: E402


@pytest.fixture(scope="session")
def anyio_backend():
    """Use asyncio backend for anyio."""
    return "asyncio"


def pytest_configure(config):
    """Configure pytest to use standard asyncio event loop instead of uvloop."""
    # Force use of default event loop policy (not uvloop)
    asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
    # Ensure PYTEST_CURRENT_TEST is set
    os.environ["PYTEST_CURRENT_TEST"] = "1"
    # Remove uvloop from sys.modules if imported
    if "uvloop" in sys.modules:
        del sys.modules["uvloop"]


# Test database URL
TEST_DATABASE_URL = settings.DATABASE_URL.replace("/chatdb", "/test_chatdb")

# Create test engine
engine_test = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database() -> AsyncGenerator[None]:
    """Prepare database for tests - drop and create all tables."""
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine_test.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(prepare_database) -> AsyncGenerator[AsyncSession]:
    """Create a test database session with transaction rollback.

    Each test gets a fresh session that rolls back after the test,
    ensuring test isolation without dropping/recreating tables.
    """
    # Ensure engine_test is initialized (prepare_database fixture should have done this)
    if engine_test is None:
        pytest.fail("engine_test is not initialized. prepare_database fixture may have failed.")

    # Create a connection and start a transaction
    connection = await engine_test.connect()
    # Start a transaction that will be rolled back
    transaction = await connection.begin()
    # Bind session to this connection
    session = AsyncSessionLocal(bind=connection)
    try:
        yield session
    finally:
        # Clean up: rollback transaction to undo all changes
        try:
            await session.close()
        except Exception:
            pass
        try:
            await transaction.rollback()
        except Exception:
            pass
        try:
            await connection.close()
        except Exception:
            pass


@pytest.fixture(scope="function")
def sync_client(db_session: AsyncSession) -> Generator[TestClient]:
    """Create a test client for synchronous tests."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient]:
    """Create async test client for async tests."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        timeout=30.0,
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def async_client(client: AsyncClient) -> AsyncGenerator[AsyncClient]:
    """Alias for client fixture for backward compatibility."""
    yield client


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user with unique email."""
    password_helper = PasswordHelper()
    hashed_password = password_helper.hash("testpassword123")

    # Use timestamp to ensure uniqueness
    unique_id = str(int(time.time() * 1000000))
    user = User(
        id=uuid4(),
        email=f"test_{unique_id}@example.com",
        username=f"testuser_{unique_id}",
        hashed_password=hashed_password,
        is_active=True,
        is_verified=True,
        is_superuser=False,
    )

    db_session.add(user)
    await db_session.flush()  # Flush to get ID, transaction will be rolled back at test end
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_superuser(client: AsyncClient, db_session: AsyncSession) -> User:
    """Create a test superuser with unique email."""
    password_helper = PasswordHelper()
    hashed_password = password_helper.hash("admin123")

    # Use timestamp to ensure uniqueness
    unique_id = str(int(time.time() * 1000000))
    user = User(
        id=uuid4(),
        email=f"admin_{unique_id}@test.com",
        username=f"admin_{unique_id}",
        hashed_password=hashed_password,
        is_active=True,
        is_verified=True,
        is_superuser=True,
    )

    db_session.add(user)
    await db_session.flush()  # Flush to get ID, transaction will be rolled back at test end
    await db_session.refresh(user)
    return user


def extract_token(response) -> str | None:
    """Extract JWT token from login response.

    BearerTransport returns token in response body as JSON with 'access_token' key.

    Args:
        response: HTTP response from login endpoint

    Returns:
        JWT token string or None if not found
    """
    # BearerTransport returns token in response body
    if response.status_code == 200:
        try:
            data = response.json()
            if isinstance(data, dict) and "access_token" in data:
                return data["access_token"]
        except Exception:
            pass

    # Try to get token from cookies (for CookieTransport)
    if hasattr(response, "cookies") and response.cookies:
        if "access_token" in response.cookies:
            return response.cookies["access_token"]

    # Try to get token from set-cookie header
    set_cookie = response.headers.get("set-cookie", "")
    if isinstance(set_cookie, list):
        for cookie in set_cookie:
            if "access_token" in cookie:
                parts = cookie.split("access_token=")
                if len(parts) > 1:
                    token = parts[1].split(";")[0]
                    return token.strip()
    elif isinstance(set_cookie, str):
        for cookie in set_cookie.split(","):
            if "access_token" in cookie:
                parts = cookie.split("access_token=")
                if len(parts) > 1:
                    token = parts[1].split(";")[0]
                    return token.strip()

    # Try Authorization header
    auth_header = response.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header.replace("Bearer ", "").strip()

    return None
