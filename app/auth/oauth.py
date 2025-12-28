"""
OAuth2 authentication routers.
"""

from typing import TYPE_CHECKING

from fastapi_users import BaseUserManager
from fastapi_users.authentication import CookieTransport
from httpx_oauth.clients.github import GitHubOAuth2
from httpx_oauth.clients.google import GoogleOAuth2

from app.core.config import settings

if TYPE_CHECKING:
    from uuid import UUID

    from app.models.user import User


# Google OAuth
google_oauth_client = (
    GoogleOAuth2(
        settings.GOOGLE_CLIENT_ID,
        settings.GOOGLE_CLIENT_SECRET,
    )
    if settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET
    else None
)

# GitHub OAuth
github_oauth_client = (
    GitHubOAuth2(
        settings.GITHUB_CLIENT_ID,
        settings.GITHUB_CLIENT_SECRET,
    )
    if settings.GITHUB_CLIENT_ID and settings.GITHUB_CLIENT_SECRET
    else None
)


def get_google_oauth_router(
    user_manager: BaseUserManager["User", "UUID"],
    secret: str,
    cookie_transport: CookieTransport,
):
    """Get Google OAuth router."""
    from fastapi_users.router.oauth import get_oauth_router

    if not google_oauth_client:
        raise ValueError("Google OAuth not configured")

    return get_oauth_router(
        google_oauth_client,
        user_manager,
        secret,
        cookie_transport,
        redirect_url="http://localhost:3000/auth/callback/google",
    )


def get_github_oauth_router(
    user_manager: BaseUserManager["User", "UUID"],
    secret: str,
    cookie_transport: CookieTransport,
):
    """Get GitHub OAuth router."""
    from fastapi_users.router.oauth import get_oauth_router

    if not github_oauth_client:
        raise ValueError("GitHub OAuth not configured")

    return get_oauth_router(
        github_oauth_client,
        user_manager,
        secret,
        cookie_transport,
        redirect_url="http://localhost:3000/auth/callback/github",
    )
