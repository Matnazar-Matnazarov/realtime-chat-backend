"""
API dependencies.
"""

from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.users import current_active_user
from app.db.base import get_db
from app.models.group import Group, GroupMember
from app.models.user import User


async def get_current_user(
    user: User = Depends(current_active_user),
) -> User:
    """Get current authenticated user."""
    return user


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

    # Check if user is a member
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
