"""
User API routes with optimized search.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.core.config import settings
from app.models.user import User
from app.schemas.user import UserPublic, UserSearchResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserPublic)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> UserPublic:
    """Get current user information."""
    return UserPublic.model_validate(current_user)


@router.patch("/me", response_model=UserPublic)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserPublic:
    """Update current user information."""
    # Check if username is being changed and if it's already taken
    if user_update.username and user_update.username != current_user.username:
        result = await db.execute(
            select(User).where(User.username == user_update.username, User.id != current_user.id)
        )
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )

    # Update user fields
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)

    await db.commit()
    await db.refresh(current_user)

    return UserPublic.model_validate(current_user)


@router.get("/search", response_model=UserSearchResponse)
async def search_users(
    query: str = Query(..., min_length=1, description="Search query (username or email)"),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserSearchResponse:
    """Search users by username or email (case-insensitive).

    Returns only active users, excluding the current user.
    Uses optimized case-insensitive search with database indexes.
    """
    query_clean = query.strip()
    if not query_clean:
        return UserSearchResponse(users=[], total=0)

    query_lower = query_clean.lower()
    search_pattern = f"%{query_lower}%"

    result = await db.execute(
        select(User)
        .where(
            (
                func.lower(User.username).like(search_pattern)
                | func.lower(User.email).like(search_pattern)
            )
            & (User.id != current_user.id)
            & User.is_active
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

    from app.core.websocket import get_manager

    manager = await get_manager()
    await manager.broadcast_online_status(
        current_user.id, is_online, exclude_user_id=current_user.id
    )
