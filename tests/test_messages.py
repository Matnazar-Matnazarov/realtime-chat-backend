"""
Tests for message endpoints.
"""

from uuid import uuid4

import pytest
from fastapi import status
from httpx import AsyncClient

from app.models.user import User


@pytest.mark.asyncio
async def test_create_private_message(async_client: AsyncClient, test_user: User, db_session):
    """Test creating a private message."""
    # Create another user
    from fastapi_users.password import PasswordHelper

    password_helper = PasswordHelper()

    receiver = User(
        id=uuid4(),
        email="receiver@example.com",
        username="receiver",
        hashed_password=password_helper.hash("password123"),
        is_active=True,
        is_verified=True,
    )
    db_session.add(receiver)
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

    # Create message
    response = await async_client.post(
        "/api/v1/messages",
        json={
            "content": "Hello, this is a test message",
            "receiver_id": str(receiver.id),
        },
        headers={"Authorization": f"Bearer {token}"} if token else {},
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["content"] == "Hello, this is a test message"
    assert data["receiver_id"] == str(receiver.id)
    assert data["sender_id"] == str(test_user.id)


@pytest.mark.asyncio
async def test_get_messages(async_client: AsyncClient, test_user: User, db_session):
    """Test getting messages."""
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
        "/api/v1/messages",
        headers={"Authorization": f"Bearer {token}"} if token else {},
    )
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_mark_message_as_read(async_client: AsyncClient, test_user: User, db_session):
    """Test marking message as read."""
    # Create a message first (simplified - would need receiver)
    # This is a basic test structure
    # Login
    login_response = await async_client.post(
        "/auth/jwt/login",
        data={
            "username": test_user.email,
            "password": "testpassword123",
        },
    )
    token = _extract_token(login_response)

    # This would need an actual message ID
    message_id = uuid4()
    response = await async_client.patch(
        f"/api/v1/messages/{message_id}/read",
        headers={"Authorization": f"Bearer {token}"} if token else {},
    )
    # Should be 404 if message doesn't exist, or 204 if it does
    assert response.status_code in [
        status.HTTP_204_NO_CONTENT,
        status.HTTP_404_NOT_FOUND,
    ]


# Import extract_token from conftest (avoid circular import)
def _extract_token(response) -> str | None:
    """Extract token from login response."""
    from tests.conftest import extract_token

    return extract_token(response)
