"""
Security utilities for JWT token generation and validation.
"""

from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from jose import JWTError, jwt

from app.core.config import settings


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(settings.TZ_INFO) + expires_delta
    else:
        expire = datetime.now(settings.TZ_INFO) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict[str, Any]) -> str:
    """Create JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.now(settings.TZ_INFO) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.REFRESH_SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Decode JWT access token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "access":
            return None
        return payload
    except JWTError:
        return None


def decode_refresh_token(token: str) -> dict[str, Any] | None:
    """Decode JWT refresh token."""
    try:
        payload = jwt.decode(token, settings.REFRESH_SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "refresh":
            return None
        return payload
    except JWTError:
        return None


def get_user_id_from_token(token: str, is_refresh: bool = False) -> UUID | None:
    """Extract user ID from JWT token."""
    if is_refresh:
        payload = decode_refresh_token(token)
    else:
        payload = decode_access_token(token)

    if not payload:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    try:
        return UUID(user_id)
    except (ValueError, TypeError):
        return None
