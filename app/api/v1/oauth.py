"""
OAuth2 authentication endpoints (Google, GitHub).

Provides OAuth2 authentication with cookie-based tokens.
"""

from fastapi import APIRouter, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.oauth import google_oauth_client
from app.auth.users import UserManager, get_user_manager
from app.core.config import settings
from app.core.utils import (
    create_token_pair,
    set_refresh_token_cookie,
    user_to_dict,
)
from app.db.base import get_db
from app.models.user import User
from app.schemas.user import UserCreate

router = APIRouter()


@router.get("/google/authorize", tags=["auth", "oauth"])
async def google_authorize(request: Request):
    """Initiate Google OAuth flow."""
    if not google_oauth_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth is not configured",
        )

    redirect_url = request.query_params.get(
        "redirect_url", "http://localhost:3000/auth/callback/google"
    )
    authorization_url = await google_oauth_client.get_authorization_url(
        redirect_uri=redirect_url,
        state=None,
    )

    return {"authorization_url": authorization_url}


@router.get("/google/callback", tags=["auth", "oauth"])
async def google_callback(
    request: Request,
    response: Response,
    code: str | None = None,
    error: str | None = None,
):
    """Handle Google OAuth callback.

    Exchanges authorization code for access token, gets user info,
    creates/updates user, and returns tokens.
    """
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth error: {error}",
        )

    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization code not provided",
        )

    if not google_oauth_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth is not configured",
        )

    redirect_url = request.query_params.get(
        "redirect_url", "http://localhost:3000/auth/callback/google"
    )

    try:
        access_token_response = await google_oauth_client.get_access_token(code, redirect_url)
        access_token = access_token_response["access_token"]

        user_id, user_email, user_name = await google_oauth_client.get_id_email(access_token)

        if not user_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not retrieve email from Google",
            )

        async for session in get_db():
            db_session: AsyncSession = session

            result = await db_session.execute(select(User).where(User.email == user_email))
            user = result.scalar_one_or_none()

            if not user:
                async for manager in get_user_manager():
                    user_manager: UserManager = manager

                    user_create = UserCreate(
                        email=user_email,
                        password="",
                        username=user_email.split("@")[0],
                        first_name=user_name.split()[0] if user_name else None,
                        last_name=" ".join(user_name.split()[1:])
                        if user_name and len(user_name.split()) > 1
                        else None,
                    )

                    user = await user_manager.create(user_create, safe=True)
                    user.is_verified = True
                    await db_session.commit()
                    await db_session.refresh(user)
            else:
                if not user.is_verified:
                    user.is_verified = True
                    await db_session.commit()
                    await db_session.refresh(user)

            access_token_jwt, refresh_token_jwt = create_token_pair(user)
            set_refresh_token_cookie(response, refresh_token_jwt)

            return {
                "access_token": access_token_jwt,
                "refresh_token": refresh_token_jwt,
                "token_type": "bearer",
                "user": user_to_dict(user),
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth authentication failed: {str(e)}",
        ) from e


@router.get("/google/status", tags=["auth", "oauth"])
async def google_oauth_status():
    """Check if Google OAuth is configured."""
    return {
        "configured": google_oauth_client is not None,
        "client_id": settings.GOOGLE_CLIENT_ID if settings.GOOGLE_CLIENT_ID else None,
    }
