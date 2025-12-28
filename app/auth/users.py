"""
User management with fastapi-users.
"""

import uuid
from typing import Any

from fastapi import Depends
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

from app.auth.database import get_user_db
from app.core.config import settings
from app.models.user import User

# JWT Strategy
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    """Get JWT authentication strategy."""
    return JWTStrategy(
        secret=settings.SECRET_KEY, lifetime_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


# Authentication backend
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    """Custom user manager."""

    reset_password_token_secret = settings.SECRET_KEY
    verification_token_secret = settings.SECRET_KEY

    async def create(self, user_create, safe: bool = False, request: Any | None = None) -> User:
        """Create a new user with username."""
        from app.schemas.user import UserCreate

        if isinstance(user_create, UserCreate):
            # Create user with username and additional fields
            user_dict = {
                "email": user_create.email,
                "hashed_password": self.password_helper.hash(user_create.password),
                "username": user_create.username,
                "first_name": user_create.first_name,
                "last_name": user_create.last_name,
                "is_superuser": False,
                "is_active": True,
                "is_verified": False,
            }
            created_user = await self.user_db.create(user_dict)
        else:
            # Fallback to default behavior
            created_user = await super().create(user_create, safe=safe, request=request)

        await self.on_after_register(created_user, request)
        return created_user

    async def on_after_register(self, user: User, request: Any | None = None) -> None:
        """Called after user registration."""
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Any | None = None
    ) -> None:
        """Called after forgot password request."""
        print(f"User {user.id} has requested password reset. Token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Any | None = None
    ) -> None:
        """Called after verification request."""
        print(f"User {user.id} has requested verification. Token: {token}")


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)) -> UserManager:
    """Get user manager."""
    yield UserManager(user_db)


# FastAPI Users instance
fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

# Current user dependencies
current_active_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)
