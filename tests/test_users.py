"""
Tests for user endpoints.
"""

import pytest
from fastapi import status
from httpx import AsyncClient

from app.models.user import User


@pytest.mark.asyncio
async def test_search_users(async_client: AsyncClient, test_user: User, db_session):
    """Test user search."""
    # Login first
    login_response = await async_client.post(
        "/auth/jwt/login",
        data={
            "username": test_user.email,
            "password": "testpassword123",
        },
    )
    token = _extract_token(login_response)

    response = await async_client.get(
        "/api/v1/users/search",
        params={"query": "test"},
        headers={"Authorization": f"Bearer {token}"} if token else {},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "users" in data
    assert "total" in data
    assert isinstance(data["users"], list)


@pytest.mark.asyncio
async def test_get_user_by_id(async_client: AsyncClient, test_user: User, db_session):
    """Test getting user by ID."""
    # Login first
    login_response = await async_client.post(
        "/auth/jwt/login",
        data={
            "username": test_user.email,
            "password": "testpassword123",
        },
    )
    token = _extract_token(login_response)

    response = await async_client.get(
        f"/api/v1/users/{test_user.id}",
        headers={"Authorization": f"Bearer {token}"} if token else {},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(test_user.id)
    assert data["email"] == test_user.email


@pytest.mark.asyncio
async def test_update_online_status(async_client: AsyncClient, test_user: User, db_session):
    """Test updating online status."""
    # Login first
    login_response = await async_client.post(
        "/auth/jwt/login",
        data={
            "username": test_user.email,
            "password": "testpassword123",
        },
    )
    token = _extract_token(login_response)

    response = await async_client.patch(
        "/api/v1/users/me/online",
        params={"is_online": True},
        headers={"Authorization": f"Bearer {token}"} if token else {},
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


# Import extract_token from conftest (avoid circular import)
def _extract_token(response) -> str | None:
    """Extract token from login response."""
    from tests.conftest import extract_token

    return extract_token(response)
