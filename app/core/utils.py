"""
Shared utility functions for authentication and user management.
"""

from fastapi import Response

from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token
from app.models.user import User


def create_token_pair(user: User) -> tuple[str, str]:
    """Create access and refresh token pair for user."""
    user_data = {
        "sub": str(user.id),
        "email": user.email,
        "username": getattr(user, "username", user.email.split("@")[0]),
    }
    access_token = create_access_token(user_data)
    refresh_token = create_refresh_token(user_data)
    return access_token, refresh_token


def user_to_dict(user: User) -> dict:
    """Convert User model to dictionary for response."""
    return {
        "id": str(user.id),
        "email": user.email,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "avatar_url": user.avatar_url,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "is_superuser": user.is_superuser,
    }


def set_access_token_cookie(response: Response, access_token: str) -> None:
    """Set access token in HTTP-only cookie."""
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )


def set_refresh_token_cookie(response: Response, refresh_token: str) -> None:
    """Set refresh token in HTTP-only cookie."""
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/",
    )


def clear_auth_cookies(response: Response) -> None:
    """Clear both access and refresh token cookies."""
    response.delete_cookie(
        key="access_token",
        path="/",
        samesite="lax",
    )
    response.delete_cookie(
        key="refresh_token",
        path="/",
        samesite="lax",
    )


def clear_refresh_token_cookie(response: Response) -> None:
    """Clear refresh token cookie."""
    response.delete_cookie(
        key="refresh_token",
        path="/",
        samesite="lax",
    )
