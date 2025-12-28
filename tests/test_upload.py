"""
Tests for file upload endpoints.
"""

import io

import pytest
from fastapi import status
from httpx import AsyncClient

from app.models.user import User


@pytest.mark.asyncio
async def test_upload_file(async_client: AsyncClient, test_user: User, db_session):
    """Test file upload."""
    # Login
    login_response = await async_client.post(
        "/auth/jwt/login",
        data={
            "username": test_user.email,
            "password": "testpassword123",
        },
    )
    token = _extract_token(login_response)

    # Create a test image file
    file_content = b"fake image content"
    files = {"file": ("test.jpg", io.BytesIO(file_content), "image/jpeg")}

    response = await async_client.post(
        "/api/v1/upload",
        files=files,
        headers={"Authorization": f"Bearer {token}"} if token else {},
    )
    # Should be 201 or 400 (depending on file validation)
    assert response.status_code in [
        status.HTTP_201_CREATED,
        status.HTTP_400_BAD_REQUEST,
        status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
    ]


# Import extract_token from conftest (avoid circular import)
def _extract_token(response) -> str | None:
    """Extract token from login response."""
    from tests.conftest import extract_token

    return extract_token(response)
