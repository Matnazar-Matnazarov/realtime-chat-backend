"""
User schemas.
"""

from datetime import datetime
from uuid import UUID

from fastapi_users import schemas
from pydantic import BaseModel, EmailStr, Field


class UserRead(schemas.BaseUser[UUID]):
    """User read schema for fastapi-users."""

    username: str
    first_name: str | None = None
    last_name: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
    is_online: bool = False
    last_seen: datetime | None = None

    class Config:
        from_attributes = True


class UserCreate(schemas.BaseUserCreate):
    """User create schema for fastapi-users."""

    username: str = Field(..., min_length=3, max_length=50)
    first_name: str | None = Field(None, max_length=100)
    last_name: str | None = Field(None, max_length=100)


class UserUpdate(schemas.BaseUserUpdate):
    """User update schema for fastapi-users."""

    username: str | None = Field(None, min_length=3, max_length=50)
    first_name: str | None = Field(None, max_length=100)
    last_name: str | None = Field(None, max_length=100)
    avatar_url: str | None = Field(None, max_length=500)
    bio: str | None = Field(None, max_length=500)


class UserPublic(BaseModel):
    """Public user information."""

    id: UUID
    email: EmailStr
    username: str
    first_name: str | None = None
    last_name: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
    is_online: bool = False
    last_seen: datetime | None = None
    is_superuser: bool = False

    class Config:
        from_attributes = True


class UserSearchResponse(BaseModel):
    """User search response."""

    users: list[UserPublic]
    total: int
