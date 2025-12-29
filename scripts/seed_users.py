"""
Script to seed database with initial users (admin and test users).
"""

import asyncio
from uuid import uuid4

from fastapi_users.password import PasswordHelper
from sqlalchemy import select

from app.core.config import settings
from app.db.base import AsyncSessionLocal
from app.models.user import User


async def create_superuser() -> User:
    """Create or update superuser."""
    password_helper = PasswordHelper()

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.email == settings.ADMIN_EMAIL))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print(f"✓ Superuser already exists: {settings.ADMIN_EMAIL}")
            if not existing_user.is_superuser:
                existing_user.is_superuser = True
                existing_user.is_active = True
                existing_user.is_verified = True
                await session.commit()
                print("  Updated existing user to superuser.")
            return existing_user

        hashed_password = password_helper.hash(settings.ADMIN_PASSWORD)
        superuser = User(
            id=uuid4(),
            email=settings.ADMIN_EMAIL,
            username=settings.ADMIN_USERNAME,
            hashed_password=hashed_password,
            is_superuser=True,
            is_active=True,
            is_verified=True,
            first_name="Admin",
            last_name="User",
        )

        session.add(superuser)
        await session.commit()
        await session.refresh(superuser)
        print(f"✓ Superuser created: {settings.ADMIN_EMAIL}")
        return superuser


async def create_test_users() -> list[User]:
    """Create test users for development."""
    password_helper = PasswordHelper()
    test_users_data = [
        {
            "email": "test1@example.com",
            "username": "testuser1",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User One",
        },
        {
            "email": "test2@example.com",
            "username": "testuser2",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User Two",
        },
    ]

    created_users = []
    async with AsyncSessionLocal() as session:
        for user_data in test_users_data:
            result = await session.execute(select(User).where(User.email == user_data["email"]))
            existing_user = result.scalar_one_or_none()

            if existing_user:
                print(f"✓ Test user already exists: {user_data['email']}")
                continue

            hashed_password = password_helper.hash(user_data["password"])
            user = User(
                id=uuid4(),
                email=user_data["email"],
                username=user_data["username"],
                hashed_password=hashed_password,
                is_superuser=False,
                is_active=True,
                is_verified=True,
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
            )

            session.add(user)
            await session.commit()
            await session.refresh(user)
            created_users.append(user)
            print(f"✓ Test user created: {user_data['email']}")

    return created_users


async def main() -> None:
    """Main function to seed users."""
    print("=" * 60)
    print("SEED USERS SCRIPT")
    print("=" * 60)
    print()

    try:
        # Create superuser
        print("Creating superuser...")
        superuser = await create_superuser()
        print(f"  Email: {superuser.email}")
        print(f"  Username: {superuser.username}")
        print(f"  Password: {settings.ADMIN_PASSWORD}")
        print()

        # Create test users
        print("Creating test users...")
        test_users = await create_test_users()
        if test_users:
            for user in test_users:
                print(f"  - {user.email} ({user.username})")
        print()

        print("=" * 60)
        print("✅ SEEDING COMPLETE!")
        print("=" * 60)
        print("\nYou can now login with:")
        print(f"  Admin: {settings.ADMIN_EMAIL} / {settings.ADMIN_PASSWORD}")
        if test_users:
            print("  Test: test1@example.com / testpass123")
        print()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
