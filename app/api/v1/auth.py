"""
Authentication endpoints with JSON and Cookie support.

Provides:
- JSON-based login
- Cookie-based authentication (access + refresh tokens in HttpOnly cookies)
- Token refresh
- Logout
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from pydantic import BaseModel

from app.auth.database import get_user_db
from app.auth.users import UserManager, get_user_manager
from app.core.security import decode_refresh_token, get_user_id_from_token
from app.core.utils import (
    clear_auth_cookies,
    create_token_pair,
    set_access_token_cookie,
    set_refresh_token_cookie,
    user_to_dict,
)
from app.schemas.user import UserCreate

router = APIRouter()


class LoginRequest(BaseModel):
    """Login request schema."""

    username: str
    password: str


class LoginResponse(BaseModel):
    """Login response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""

    refresh_token: str | None = None


class RefreshTokenResponse(BaseModel):
    """Refresh token response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LogoutResponse(BaseModel):
    """Logout response schema."""

    message: str


class RegisterRequest(BaseModel):
    """Register request schema."""

    email: str
    username: str
    password: str
    first_name: str | None = None
    last_name: str | None = None


class RegisterResponse(BaseModel):
    """Register response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


class Credentials:
    """Credentials object for authentication."""

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK, tags=["auth"])
async def login(
    login_data: LoginRequest,
    response: Response,
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
) -> LoginResponse:
    """Login with JSON credentials.

    Sets both access and refresh tokens in HttpOnly cookies.
    Also returns tokens in response body for Bearer token usage.
    """
    credentials = Credentials(login_data.username, login_data.password)
    user = await user_manager.authenticate(credentials)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    access_token, refresh_token = create_token_pair(user)

    # Set tokens in HttpOnly cookies
    set_access_token_cookie(response, access_token)
    set_refresh_token_cookie(response, refresh_token)

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=user_to_dict(user),
    )


@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    status_code=status.HTTP_200_OK,
    tags=["auth"],
)
async def refresh_token(
    request: Request,
    response: Response,
    refresh_data: RefreshTokenRequest | None = None,
    user_db: Annotated[SQLAlchemyUserDatabase, Depends(get_user_db)] = None,
) -> RefreshTokenResponse:
    """Refresh access token.

    Accepts refresh token from HttpOnly cookie or request body.
    Returns new tokens in both cookies and response body.
    """
    refresh_token = request.cookies.get("refresh_token") or (
        refresh_data.refresh_token if refresh_data else None
    )

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not provided",
        )

    payload = decode_refresh_token(refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    user_id = get_user_id_from_token(refresh_token, is_refresh=True)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    if user_db is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        )

    try:
        user = await user_db.get(user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        ) from e

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    new_access_token, new_refresh_token = create_token_pair(user)

    # Set new tokens in HttpOnly cookies
    set_access_token_cookie(response, new_access_token)
    set_refresh_token_cookie(response, new_refresh_token)

    return RefreshTokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
    )


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["auth"],
)
async def register(
    register_data: RegisterRequest,
    response: Response,
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
) -> RegisterResponse:
    """Register a new user.

    Sets both access and refresh tokens in HttpOnly cookies.
    Also returns tokens in response body for Bearer token usage.
    """
    # Check if user with email or username already exists
    from sqlalchemy import or_, select
    from app.models.user import User
    from app.api.dependencies import get_db

    async for db_session in get_db():
        result = await db_session.execute(
            select(User).where(
                or_(User.email == register_data.email, User.username == register_data.username)
            )
        )
        existing_user = result.scalar_one_or_none()
        if existing_user:
            if existing_user.email == register_data.email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered",
                )
            if existing_user.username == register_data.username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken",
                )
        break  # Only check once

    # Create user
    user_create = UserCreate(
        email=register_data.email,
        username=register_data.username,
        password=register_data.password,
        first_name=register_data.first_name,
        last_name=register_data.last_name,
    )

    user = await user_manager.create(user_create, safe=True)

    # Generate tokens
    access_token, refresh_token = create_token_pair(user)

    # Set tokens in HttpOnly cookies
    set_access_token_cookie(response, access_token)
    set_refresh_token_cookie(response, refresh_token)

    return RegisterResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=user_to_dict(user),
    )


@router.post(
    "/logout",
    response_model=LogoutResponse,
    status_code=status.HTTP_200_OK,
    tags=["auth"],
)
async def logout(response: Response) -> LogoutResponse:
    """Logout - clears all auth cookies."""
    clear_auth_cookies(response)
    return LogoutResponse(message="Successfully logged out")
