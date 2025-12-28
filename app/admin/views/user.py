"""
User admin view with authentication support.
"""

from uuid import UUID

from fastadmin import register

from app.admin.base import BaseUUIDModelAdmin
from app.db.base import AsyncSessionLocal
from app.models.user import User


@register(User, sqlalchemy_sessionmaker=AsyncSessionLocal)
class UserAdmin(BaseUUIDModelAdmin):
    """Admin configuration for User model.

    Provides user management with authentication support for admin access.
    Only superusers can log into the admin panel.
    """

    exclude = ("hashed_password",)
    list_display = (
        "id",
        "username",
        "email",
        "is_active",
        "is_verified",
        "is_superuser",
        "is_online",
        "created_at",
    )
    list_display_links = ("id", "username")
    list_filter = ("is_active", "is_verified", "is_superuser", "is_online")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("-created_at",)

    async def authenticate(self, username: str, password: str) -> UUID | None:
        """Authenticate admin user for panel access.

        Args:
            username: Admin username
            password: Admin password

        Returns:
            User ID if authenticated successfully, None otherwise
        """
        from pwdlib import PasswordHash
        from pwdlib.hashers.argon2 import Argon2Hasher
        from sqlalchemy import select

        sessionmaker = self.get_sessionmaker()
        async with sessionmaker() as session:
            result = await session.execute(select(User).where(User.username == username))
            user = result.scalar_one_or_none()

            if not user:
                return None

            # Verify password using pwdlib (same as fastapi-users)
            try:
                password_hash = PasswordHash([Argon2Hasher()])
                if not password_hash.verify(password, user.hashed_password):
                    return None
            except Exception:
                return None

            if not user.is_superuser:
                return None

            if not user.is_active:
                return None

            return user.id
