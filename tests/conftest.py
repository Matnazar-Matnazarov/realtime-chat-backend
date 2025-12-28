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
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

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
from app.db.base import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models.user import User  # noqa: E402


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

# Create test engine with proper pool settings
# Use smaller pool for tests to avoid connection issues
# Note: Engine is created per test session to avoid event loop conflicts
test_engine = None
TestSessionLocal = None


def get_test_engine():
    """Get or create test engine (lazy initialization)."""
    global test_engine, TestSessionLocal
    if test_engine is None:
        test_engine = create_async_engine(
            TEST_DATABASE_URL,
            echo=False,
            pool_pre_ping=False,  # Disable pre-ping to avoid event loop issues
            pool_size=5,  # Increased for better test reliability
            max_overflow=5,  # Allow some overflow for concurrent tests
            pool_recycle=3600,
        )
        TestSessionLocal = async_sessionmaker(
            test_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return test_engine, TestSessionLocal


def _create_tables(sync_conn):
    """Helper function to create tables synchronously."""
    Base.metadata.create_all(sync_conn, checkfirst=True)


def _drop_tables(sync_conn):
    """Helper function to drop tables synchronously."""
    Base.metadata.drop_all(sync_conn, checkfirst=True)


@pytest_asyncio.fixture(scope="session")
async def setup_database() -> AsyncGenerator[None]:
    """Create all tables once per test session."""
    engine, _ = get_test_engine()
    async with engine.begin() as conn:
        await conn.run_sync(_create_tables)
    yield
    # Clean up: drop all tables after all tests
    # Close all connections before disposing engine
    try:
        # Wait for all connections to close
        await asyncio.sleep(0.1)
        async with engine.begin() as conn:
            await conn.run_sync(_drop_tables)
    except Exception:
        pass  # Ignore errors during teardown
    finally:
        # Dispose engine and wait for cleanup
        await engine.dispose()
        await asyncio.sleep(0.1)


@pytest_asyncio.fixture(scope="function")
async def db_session(setup_database) -> AsyncGenerator[AsyncSession]:
    """Create a test database session with transaction rollback.

    Each test gets a fresh session that rolls back after the test,
    ensuring test isolation without dropping/recreating tables.
    Uses nested transaction (SAVEPOINT) for proper rollback.
    """
    engine, session_local = get_test_engine()
    # Create a connection and start a transaction
    connection = await engine.connect()
    # Start a transaction
    transaction = await connection.begin()
    # Create a nested transaction (SAVEPOINT) for test isolation
    # This allows us to rollback only test data, not the outer transaction
    nested = await connection.begin_nested()
    # Bind session to this connection
    session = session_local(bind=connection)
    try:
        yield session
    finally:
        # Clean up in reverse order
        try:
            await session.close()
        except Exception:
            pass
        try:
            await nested.rollback()
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
def client(db_session: AsyncSession) -> Generator[TestClient]:
    """Create a test client for synchronous tests."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient]:
    """Create an async test client for async tests."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


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
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_superuser(db_session: AsyncSession) -> User:
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
    await db_session.commit()
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
