"""
Contact schemas.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.user import UserPublic


class ContactCreate(BaseModel):
    """Create contact request."""

    contact_id: UUID = Field(..., description="ID of the user to add as contact")
    nickname: str | None = Field(None, max_length=100, description="Optional nickname")


class ContactResponse(BaseModel):
    """Contact response."""

    id: UUID
    user_id: UUID
    contact_id: UUID
    nickname: str | None = None
    created_at: datetime
    contact: UserPublic | None = None

    class Config:
        from_attributes = True
