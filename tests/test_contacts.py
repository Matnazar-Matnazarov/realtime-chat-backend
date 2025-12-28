"""
Tests for contact endpoints.
"""

from uuid import uuid4

import pytest
from fastapi import status
from httpx import AsyncClient

from app.models.user import User


@pytest.mark.asyncio
async def test_create_contact(async_client: AsyncClient, test_user: User, db_session):
    """Test creating a contact."""
    # Create another user
    from fastapi_users.password import PasswordHelper

    password_helper = PasswordHelper()
    contact_user = User(
        id=uuid4(),
        email="contact@example.com",
        username="contactuser",
        hashed_password=password_helper.hash("password123"),
        is_active=True,
        is_verified=True,
    )
    db_session.add(contact_user)
    await db_session.commit()

    # Login
    login_response = await async_client.post(
        "/auth/jwt/login",
        data={
            "username": test_user.email,
            "password": "testpassword123",
        },
    )
    token = _extract_token(login_response)

    # Create contact
    response = await async_client.post(
        "/api/v1/contacts",
        json={"contact_id": str(contact_user.id), "nickname": "Friend"},
        headers={"Authorization": f"Bearer {token}"} if token else {},
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["contact_id"] == str(contact_user.id)
    assert data["user_id"] == str(test_user.id)


@pytest.mark.asyncio
async def test_get_contacts(async_client: AsyncClient, test_user: User, db_session):
    """Test getting contacts."""
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
        "/api/v1/contacts",
        headers={"Authorization": f"Bearer {token}"} if token else {},
    )
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


# Import extract_token from conftest (avoid circular import)
def _extract_token(response) -> str | None:
    """Extract token from login response."""
    from tests.conftest import extract_token

    return extract_token(response)
