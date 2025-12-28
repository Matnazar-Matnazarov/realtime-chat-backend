"""
Database adapter for fastapi-users.
"""

from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.models.user import User


async def get_user_db(session: AsyncSession = Depends(get_db)) -> SQLAlchemyUserDatabase:
    """Get user database adapter."""
    yield SQLAlchemyUserDatabase(session, User)
