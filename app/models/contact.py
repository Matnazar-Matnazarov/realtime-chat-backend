"""
Contact model.
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class Contact(Base):
    """Contact model (Many-to-Many relationship between users)."""

    __tablename__ = "contacts"

    id: Mapped[UUID] = mapped_column(primary_key=True, unique=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    contact_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    nickname: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], back_populates="contacts")
    contact: Mapped["User"] = relationship(
        "User", foreign_keys=[contact_id], back_populates="contact_of"
    )

    # Unique constraint: user cannot add same contact twice
    __table_args__ = (UniqueConstraint("user_id", "contact_id", name="unique_user_contact"),)

    def __repr__(self) -> str:
        return f"<Contact {self.user_id} -> {self.contact_id}>"
