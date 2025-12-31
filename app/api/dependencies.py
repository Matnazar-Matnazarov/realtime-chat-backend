"""
API dependencies for authentication and authorization.
"""

from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_user_id_from_token
from app.db.base import get_db
from app.models.group import Group, GroupMember
from app.models.user import User


async def get_current_user_from_token(request: Request, db: AsyncSession = Depends(get_db)) -> User:
    """Get current user from JWT token.

    Supports token from:
    1. HttpOnly cookie (access_token)
    2. Authorization header (Bearer token)
    """
    # Try to get token from cookie first
    access_token = request.cookies.get("access_token")

    # If not in cookie, try Authorization header
    if not access_token:
        authorization = request.headers.get("Authorization")
        if authorization and authorization.startswith("Bearer "):
            access_token = authorization.replace("Bearer ", "").strip()

    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = get_user_id_from_token(access_token, is_refresh=False)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    return user


async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)) -> User:
    """Get current authenticated user.

    Supports both cookie-based and Bearer token authentication.
    """
    from app.auth.users import current_active_user

    try:
        user = await current_active_user(request)
        if user:
            return user
    except Exception:
        pass

    return await get_current_user_from_token(request, db)


async def get_group_or_404(
    group_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Group:
    """Get group by ID or raise 404."""
    result = await db.execute(select(Group).where(Group.id == group_id))
    group = result.scalar_one_or_none()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found",
        )

    result = await db.execute(
        select(GroupMember).where(
            GroupMember.group_id == group_id, GroupMember.user_id == current_user.id
        )
    )
    membership = result.scalar_one_or_none()

    if not membership and not group.is_private:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this group",
        )

    return group
