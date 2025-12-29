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
# tokenUrl must be absolute path for Swagger UI to work correctly
# Router is mounted at /auth/jwt, so login endpoint is /auth/jwt/login
bearer_transport = BearerTransport(tokenUrl="/auth/jwt/login")


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

    async def authenticate(self, credentials) -> User | None:
        """Authenticate user by email or username.

        Override to support both email and username login.
        credentials is OAuth2PasswordRequestForm object with username and password attributes.
        """
        from fastapi.security import OAuth2PasswordRequestForm
        from sqlalchemy import or_, select

        # OAuth2PasswordRequestForm has username and password attributes
        if isinstance(credentials, OAuth2PasswordRequestForm):
            username_or_email = credentials.username
            password = credentials.password
        elif isinstance(credentials, dict):
            username_or_email = credentials.get("username", "")
            password = credentials.get("password", "")
        else:
            # Fallback: try to get attributes directly
            username_or_email = getattr(credentials, "username", "")
            password = getattr(credentials, "password", "")

        if not username_or_email or not password:
            return None

        # Get user by email or username using user_db session
        session = self.user_db.session
        result = await session.execute(
            select(User).where(
                or_(User.email == username_or_email, User.username == username_or_email)
            )
        )
        user = result.scalar_one_or_none()

        if not user:
            return None

        # Verify password using pwdlib (same as fastapi-users)
        from pwdlib import PasswordHash
        from pwdlib.hashers.argon2 import Argon2Hasher

        try:
            password_hash = PasswordHash([Argon2Hasher()])
            if not password_hash.verify(password, user.hashed_password):
                return None
        except Exception:
            return None

        # Check if user is active
        if not user.is_active:
            return None

        return user

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
