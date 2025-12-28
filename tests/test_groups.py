"""
Tests for group endpoints.
"""

import pytest
from fastapi import status
from httpx import AsyncClient

from app.models.user import User


@pytest.mark.asyncio
async def test_create_group(async_client: AsyncClient, test_user: User, db_session):
    """Test creating a group."""
    # Login
    login_response = await async_client.post(
        "/auth/jwt/login",
        data={
            "username": test_user.email,
            "password": "testpassword123",
        },
    )
    token = _extract_token(login_response)

    response = await async_client.post(
        "/api/v1/groups",
        json={
            "name": "Test Group",
            "description": "A test group",
            "is_private": False,
            "member_ids": [],
        },
        headers={"Authorization": f"Bearer {token}"} if token else {},
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "Test Group"
    assert data["creator_id"] == str(test_user.id)


@pytest.mark.asyncio
async def test_get_groups(async_client: AsyncClient, test_user: User, db_session):
    """Test getting user's groups."""
    # Login
    login_response = await async_client.post(
        "/auth/jwt/login",
        data={
            "username": test_user.email,
            "password": "testpassword123",
        },
    )
    token = _extract_token(login_response)

    response = await async_client.get(
        "/api/v1/groups",
        headers={"Authorization": f"Bearer {token}"} if token else {},
    )
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


# Import extract_token from conftest (avoid circular import)
def _extract_token(response) -> str | None:
    """Extract token from login response."""
    from tests.conftest import extract_token

    return extract_token(response)
