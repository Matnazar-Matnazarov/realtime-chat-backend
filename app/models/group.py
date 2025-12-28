"""
Group model.
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.message import Message
    from app.models.user import User


class Group(Base):
    """Group/Chat room model."""

    __tablename__ = "groups"

    id: Mapped[UUID] = mapped_column(primary_key=True, unique=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    creator_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    is_private: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    creator: Mapped["User"] = relationship(
        "User", foreign_keys=[creator_id], back_populates="created_groups"
    )
    members: Mapped[list["GroupMember"]] = relationship(
        "GroupMember", back_populates="group", cascade="all, delete-orphan"
    )
    messages: Mapped[list["Message"]] = relationship(
        "Message", back_populates="group", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Group {self.name} ({self.id})>"


class GroupMember(Base):
    """Group membership model (Many-to-Many relationship)."""

    __tablename__ = "group_members"

    id: Mapped[UUID] = mapped_column(primary_key=True, unique=True, default=uuid4)
    group_id: Mapped[UUID] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(20), default="member", nullable=False)  # member, admin
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    group: Mapped["Group"] = relationship("Group", back_populates="members")
    user: Mapped["User"] = relationship("User", back_populates="group_memberships")

    def __repr__(self) -> str:
        return f"<GroupMember {self.user_id} in {self.group_id}>"
