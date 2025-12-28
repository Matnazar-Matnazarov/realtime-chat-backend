"""
User API routes.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.core.config import settings
from app.models.user import User
from app.schemas.user import UserPublic, UserSearchResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserPublic)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> UserPublic:
    """Get current user information."""
    return UserPublic.model_validate(current_user)


@router.get("/search", response_model=UserSearchResponse)
async def search_users(
    query: str = Query(..., min_length=1, description="Search query (username or email)"),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserSearchResponse:
    """Search users by username or email."""
    search_pattern = f"%{query}%"
    result = await db.execute(
        select(User)
        .where(
            (User.username.ilike(search_pattern) | User.email.ilike(search_pattern))
            & (User.id != current_user.id)  # Exclude current user
        )
        .limit(limit)
    )
    users = result.scalars().all()

    return UserSearchResponse(users=[UserPublic.model_validate(u) for u in users], total=len(users))


@router.get("/{user_id}", response_model=UserPublic)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserPublic:
    """Get user by ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserPublic.model_validate(user)


@router.patch("/me/online", status_code=status.HTTP_204_NO_CONTENT)
async def update_online_status(
    is_online: bool = Query(..., description="Online status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Update user online status."""
    current_user.is_online = is_online
    current_user.last_seen = datetime.now(settings.TZ_INFO) if not is_online else None

    await db.commit()

    # Broadcast status change
    from app.core.websocket import get_manager

    manager = await get_manager()
    await manager.broadcast_online_status(
        current_user.id, is_online, exclude_user_id=current_user.id
    )
