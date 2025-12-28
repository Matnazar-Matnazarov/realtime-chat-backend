"""
Contact admin view.
"""

from fastadmin import register

from app.admin.base import BaseUUIDModelAdmin
from app.db.base import AsyncSessionLocal
from app.models.contact import Contact


@register(Contact, sqlalchemy_sessionmaker=AsyncSessionLocal)
class ContactAdmin(BaseUUIDModelAdmin):
    """Admin configuration for Contact model."""

    list_display = (
        "id",
        "user_id",
        "contact_id",
        "nickname",
        "created_at",
    )
    list_display_links = ("id",)
    list_filter = ("created_at",)
    search_fields = ("nickname",)
    ordering = ("-created_at",)
