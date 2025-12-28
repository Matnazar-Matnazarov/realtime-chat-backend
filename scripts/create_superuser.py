"""
Script to create a superuser.
"""

import asyncio
from uuid import uuid4

from fastapi_users.password import PasswordHelper
from sqlalchemy import select

from app.core.config import settings
from app.db.base import AsyncSessionLocal
from app.models.user import User


async def create_superuser() -> None:
    """Create a superuser."""
    password_helper = PasswordHelper()

    async with AsyncSessionLocal() as session:
        # Check if superuser already exists
        result = await session.execute(select(User).where(User.email == settings.ADMIN_EMAIL))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print(f"Superuser with email {settings.ADMIN_EMAIL} already exists.")
            if not existing_user.is_superuser:
                existing_user.is_superuser = True
                await session.commit()
                print("Updated existing user to superuser.")
            return

        # Create new superuser
        hashed_password = password_helper.hash(settings.ADMIN_PASSWORD)
        superuser = User(
            id=uuid4(),
            email=settings.ADMIN_EMAIL,
            username=settings.ADMIN_USERNAME,
            hashed_password=hashed_password,
            is_superuser=True,
            is_active=True,
            is_verified=True,
        )

        session.add(superuser)
        await session.commit()
        print("Superuser created successfully!")
        print(f"Email: {settings.ADMIN_EMAIL}")
        print(f"Username: {settings.ADMIN_USERNAME}")
        print(f"Password: {settings.ADMIN_PASSWORD}")


if __name__ == "__main__":
    asyncio.run(create_superuser())
