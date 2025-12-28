"""
Message schemas.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.user import UserPublic


class MessageCreate(BaseModel):
    """Create message request."""

    content: str = Field(..., min_length=1, max_length=5000)
    receiver_id: UUID | None = None
    group_id: UUID | None = None
    media_url: str | None = None
    media_type: str | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "content": "Hello!",
                "receiver_id": "123e4567-e89b-12d3-a456-426614174000",
            }
        }


class MessageResponse(BaseModel):
    """Message response."""

    id: UUID
    content: str
    sender_id: UUID
    receiver_id: UUID | None = None
    group_id: UUID | None = None
    media_url: str | None = None
    media_type: str | None = None
    is_read: bool = False
    created_at: datetime
    sender: UserPublic | None = None

    class Config:
        from_attributes = True
