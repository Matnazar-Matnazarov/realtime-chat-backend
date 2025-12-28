"""
Message admin view.
"""

from fastadmin import register

from app.admin.base import BaseUUIDModelAdmin
from app.db.base import AsyncSessionLocal
from app.models.message import Message


@register(Message, sqlalchemy_sessionmaker=AsyncSessionLocal)
class MessageAdmin(BaseUUIDModelAdmin):
    """Admin configuration for Message model."""

    list_display = (
        "id",
        "content",
        "sender_id",
        "receiver_id",
        "group_id",
        "is_read",
        "created_at",
    )
    list_display_links = ("id", "content")
    list_filter = ("is_read", "created_at")
    search_fields = ("content",)
    ordering = ("-created_at",)
