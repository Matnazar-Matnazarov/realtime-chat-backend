"""
User model.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.contact import Contact
    from app.models.group import Group, GroupMember
    from app.models.message import Message


class User(SQLAlchemyBaseUserTableUUID, Base):
    """User model with additional fields."""

    __tablename__ = "users"

    # Additional fields
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    bio: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_online: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
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
    sent_messages: Mapped[list["Message"]] = relationship(
        "Message",
        foreign_keys="Message.sender_id",
        back_populates="sender",
        cascade="all, delete-orphan",
    )
    received_messages: Mapped[list["Message"]] = relationship(
        "Message",
        foreign_keys="Message.receiver_id",
        back_populates="receiver",
        cascade="all, delete-orphan",
    )
    group_memberships: Mapped[list["GroupMember"]] = relationship(
        "GroupMember",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    created_groups: Mapped[list["Group"]] = relationship(
        "Group",
        foreign_keys="Group.creator_id",
        back_populates="creator",
        cascade="all, delete-orphan",
    )
    contacts: Mapped[list["Contact"]] = relationship(
        "Contact",
        foreign_keys="Contact.user_id",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    contact_of: Mapped[list["Contact"]] = relationship(
        "Contact",
        foreign_keys="Contact.contact_id",
        back_populates="contact",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User {self.username} ({self.email})>"
