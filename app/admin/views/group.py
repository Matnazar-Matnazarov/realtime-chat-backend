"""
Group and GroupMember admin views.
"""

from fastadmin import register

from app.admin.base import BaseUUIDModelAdmin
from app.db.base import AsyncSessionLocal
from app.models.group import Group, GroupMember


@register(Group, sqlalchemy_sessionmaker=AsyncSessionLocal)
class GroupAdmin(BaseUUIDModelAdmin):
    """Admin configuration for Group model."""

    list_display = (
        "id",
        "name",
        "description",
        "creator_id",
        "is_private",
        "created_at",
    )
    list_display_links = ("id", "name")
    list_filter = ("is_private", "created_at")
    search_fields = ("name", "description")
    ordering = ("-created_at",)


@register(GroupMember, sqlalchemy_sessionmaker=AsyncSessionLocal)
class GroupMemberAdmin(BaseUUIDModelAdmin):
    """Admin configuration for GroupMember model."""

    list_display = (
        "id",
        "group_id",
        "user_id",
        "role",
        "joined_at",
    )
    list_display_links = ("id",)
    list_filter = ("role", "joined_at")
    ordering = ("-joined_at",)
