"""
Group API routes.
"""

from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.dependencies import get_current_user, get_db, get_group_or_404
from app.core.websocket import get_manager
from app.models.group import Group, GroupMember
from app.models.user import User
from app.schemas.group import GroupCreate, GroupMemberResponse, GroupResponse, GroupUpdate

router = APIRouter(prefix="/groups", tags=["groups"])


@router.post("", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
async def create_group(
    group_data: GroupCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GroupResponse:
    """Create a new group."""
    # Create group
    group = Group(
        id=uuid4(),
        name=group_data.name,
        description=group_data.description,
        avatar_url=group_data.avatar_url,
        creator_id=current_user.id,
        is_private=group_data.is_private,
    )

    db.add(group)
    await db.flush()

    # Add creator as admin
    creator_member = GroupMember(
        id=uuid4(),
        group_id=group.id,
        user_id=current_user.id,
        role="admin",
    )
    db.add(creator_member)

    # Add other members
    member_ids = set(group_data.member_ids)
    member_ids.discard(current_user.id)  # Remove creator if present

    for member_id in member_ids:
        # Verify user exists
        result = await db.execute(select(User).where(User.id == member_id))
        user = result.scalar_one_or_none()
        if user:
            member = GroupMember(
                id=uuid4(),
                group_id=group.id,
                user_id=member_id,
                role="member",
            )
            db.add(member)

    await db.commit()
    await db.refresh(group)
    await db.refresh(group, ["creator", "members"])

    # Load members with users
    result = await db.execute(
        select(GroupMember)
        .where(GroupMember.group_id == group.id)
        .options(selectinload(GroupMember.user))
    )
    members = result.scalars().all()

    response = GroupResponse.model_validate(group)
    response.members = [GroupMemberResponse.model_validate(m) for m in members]
    response.member_count = len(members)

    return response


@router.get("", response_model=list[GroupResponse])
async def get_groups(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[GroupResponse]:
    """Get groups for current user."""
    # Get groups where user is a member
    result = await db.execute(
        select(Group)
        .join(GroupMember)
        .where(GroupMember.user_id == current_user.id)
        .order_by(Group.updated_at.desc())
        .limit(limit)
        .offset(offset)
    )
    groups = result.scalars().all()

    # Load relationships
    for group in groups:
        await db.refresh(group, ["creator", "members"])

    return [GroupResponse.model_validate(g) for g in groups]


@router.get("/{group_id}", response_model=GroupResponse)
async def get_group(
    group: Group = Depends(get_group_or_404),
    db: AsyncSession = Depends(get_db),
) -> GroupResponse:
    """Get group by ID."""
    await db.refresh(group, ["creator", "members"])
    result = await db.execute(
        select(GroupMember)
        .where(GroupMember.group_id == group.id)
        .options(selectinload(GroupMember.user))
    )
    members = result.scalars().all()

    response = GroupResponse.model_validate(group)
    response.members = [GroupMemberResponse.model_validate(m) for m in members]
    response.member_count = len(members)

    return response


@router.patch("/{group_id}", response_model=GroupResponse)
async def update_group(
    group_data: GroupUpdate,
    group: Group = Depends(get_group_or_404),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GroupResponse:
    """Update group (only admin/creator can update)."""
    # Check if user is admin or creator
    result = await db.execute(
        select(GroupMember).where(
            GroupMember.group_id == group.id,
            GroupMember.user_id == current_user.id,
            GroupMember.role.in_(["admin"]),
        )
    )
    membership = result.scalar_one_or_none()

    if not membership and group.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only group admin or creator can update the group",
        )

    # Update fields
    if group_data.name is not None:
        group.name = group_data.name
    if group_data.description is not None:
        group.description = group_data.description
    if group_data.avatar_url is not None:
        group.avatar_url = group_data.avatar_url
    if group_data.is_private is not None:
        group.is_private = group_data.is_private

    await db.commit()
    await db.refresh(group, ["creator", "members"])

    return GroupResponse.model_validate(group)


@router.post(
    "/{group_id}/members", response_model=GroupMemberResponse, status_code=status.HTTP_201_CREATED
)
async def add_member(
    group_id: UUID,
    user_id: UUID = Query(..., description="User ID to add"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GroupMemberResponse:
    """Add member to group."""
    group = await get_group_or_404(group_id, db, current_user)

    # Check if user is admin
    result = await db.execute(
        select(GroupMember).where(
            GroupMember.group_id == group_id,
            GroupMember.user_id == current_user.id,
            GroupMember.role.in_(["admin"]),
        )
    )
    membership = result.scalar_one_or_none()

    if not membership and group.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only group admin can add members",
        )

    # Check if user is already a member
    result = await db.execute(
        select(GroupMember).where(GroupMember.group_id == group_id, GroupMember.user_id == user_id)
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member",
        )

    # Verify user exists
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Add member
    member = GroupMember(
        id=uuid4(),
        group_id=group_id,
        user_id=user_id,
        role="member",
    )
    db.add(member)
    await db.commit()
    await db.refresh(member, ["user"])

    return GroupMemberResponse.model_validate(member)


@router.delete("/{group_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    group_id: UUID,
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Remove member from group."""
    group = await get_group_or_404(group_id, db, current_user)

    # Check permissions
    result = await db.execute(
        select(GroupMember).where(
            GroupMember.group_id == group_id,
            GroupMember.user_id == current_user.id,
            GroupMember.role.in_(["admin"]),
        )
    )
    membership = result.scalar_one_or_none()

    if not membership and group.creator_id != current_user.id and user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only group admin or the user themselves can remove members",
        )

    # Remove member
    result = await db.execute(
        select(GroupMember).where(GroupMember.group_id == group_id, GroupMember.user_id == user_id)
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found",
        )

    await db.delete(member)
    await db.commit()

    # Remove from WebSocket room
    manager = await get_manager()
    await manager.leave_group(user_id, group_id)
