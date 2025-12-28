"""
Message model.
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.group import Group
    from app.models.user import User


class Message(Base):
    """Message model for private and group chats."""

    __tablename__ = "messages"

    id: Mapped[UUID] = mapped_column(primary_key=True, unique=True, default=uuid4)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sender_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    receiver_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )
    group_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE"), nullable=True, index=True
    )
    media_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    media_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_read: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    # Relationships
    sender: Mapped["User"] = relationship(
        "User", foreign_keys=[sender_id], back_populates="sent_messages"
    )
    receiver: Mapped["User | None"] = relationship(
        "User", foreign_keys=[receiver_id], back_populates="received_messages"
    )
    group: Mapped["Group | None"] = relationship(
        "Group", back_populates="messages", foreign_keys=[group_id]
    )

    def __repr__(self) -> str:
        return f"<Message {self.id} from {self.sender_id}>"
