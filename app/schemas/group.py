"""
Group schemas.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.user import UserPublic


class GroupCreate(BaseModel):
    """Create group request."""

    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
    avatar_url: str | None = None
    is_private: bool = False
    member_ids: list[UUID] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Project Team",
                "description": "Team chat for project discussions",
                "is_private": False,
                "member_ids": ["123e4567-e89b-12d3-a456-426614174000"],
            }
        }


class GroupUpdate(BaseModel):
    """Update group request."""

    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
    avatar_url: str | None = None
    is_private: bool | None = None


class GroupMemberResponse(BaseModel):
    """Group member response."""

    id: UUID
    group_id: UUID
    user_id: UUID
    role: str
    joined_at: datetime
    user: UserPublic | None = None

    class Config:
        from_attributes = True


class GroupResponse(BaseModel):
    """Group response."""

    id: UUID
    name: str
    description: str | None = None
    avatar_url: str | None = None
    creator_id: UUID
    is_private: bool = False
    created_at: datetime
    updated_at: datetime
    creator: UserPublic | None = None
    members: list[GroupMemberResponse] = []
    member_count: int = 0

    class Config:
        from_attributes = True
