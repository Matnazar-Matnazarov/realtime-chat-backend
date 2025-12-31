"""
Message API routes.
"""

from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.core.websocket import get_manager
from app.models.group import GroupMember
from app.models.message import Message
from app.models.user import User
from app.schemas.message import MessageCreate, MessageResponse

router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_message(
    message_data: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    """Create a new message."""
    # Validate: either receiver_id or group_id must be provided
    if not message_data.receiver_id and not message_data.group_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either receiver_id or group_id must be provided",
        )

    # If group message, verify user is a member
    if message_data.group_id:
        result = await db.execute(
            select(GroupMember).where(
                GroupMember.group_id == message_data.group_id,
                GroupMember.user_id == current_user.id,
            )
        )
        membership = result.scalar_one_or_none()
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this group",
            )

    # Auto-create contact if private message and contact doesn't exist
    if message_data.receiver_id:
        from app.models.contact import Contact

        # Check if contact exists for sender (current_user -> receiver)
        sender_contact_check = await db.execute(
            select(Contact).where(
                Contact.user_id == current_user.id,
                Contact.contact_id == message_data.receiver_id,
            )
        )
        sender_contact = sender_contact_check.scalar_one_or_none()

        # Create contact for sender if doesn't exist
        if not sender_contact:
            sender_contact = Contact(
                id=uuid4(),
                user_id=current_user.id,
                contact_id=message_data.receiver_id,
                nickname=None,
            )
            db.add(sender_contact)
            print(f"✅ Auto-created contact: {current_user.id} -> {message_data.receiver_id}")

        # Check if reverse contact exists (receiver -> current_user)
        receiver_contact_check = await db.execute(
            select(Contact).where(
                Contact.user_id == message_data.receiver_id,
                Contact.contact_id == current_user.id,
            )
        )
        receiver_contact = receiver_contact_check.scalar_one_or_none()

        # Create reverse contact for receiver if doesn't exist
        if not receiver_contact:
            receiver_contact = Contact(
                id=uuid4(),
                user_id=message_data.receiver_id,
                contact_id=current_user.id,
                nickname=None,
            )
            db.add(receiver_contact)
            print(
                f"✅ Auto-created reverse contact: {message_data.receiver_id} -> {current_user.id}"
            )

    # Create message
    message = Message(
        id=uuid4(),
        content=message_data.content,
        sender_id=current_user.id,
        receiver_id=message_data.receiver_id,
        group_id=message_data.group_id,
        media_url=message_data.media_url,
        media_type=message_data.media_type,
    )

    db.add(message)
    await db.commit()
    await db.refresh(message)

    # Load sender for response
    await db.refresh(message, ["sender"])

    # Send via WebSocket
    message_dict = {
        "type": "message",
        "id": str(message.id),
        "content": message.content,
        "sender_id": str(message.sender_id),
        "receiver_id": str(message.receiver_id) if message.receiver_id else None,
        "group_id": str(message.group_id) if message.group_id else None,
        "media_url": message.media_url,
        "media_type": message.media_type,
        "is_read": message.is_read,
        "created_at": message.created_at.isoformat(),
        "sender": {
            "id": str(current_user.id),
            "username": current_user.username,
            "email": current_user.email,
            "avatar_url": current_user.avatar_url,
        },
    }

    manager = await get_manager()
    if message_data.receiver_id:
        # Private message - send to both sender and receiver
        # Send to receiver
        receiver_sent = await manager.send_personal_message(message_dict, message_data.receiver_id)
        # Also send to sender so they see their own message in real-time
        sender_sent = await manager.send_personal_message(message_dict, current_user.id)
        print(
            f"Message sent - Receiver ({message_data.receiver_id}): {receiver_sent}, "
            f"Sender ({current_user.id}): {sender_sent}"
        )
    elif message_data.group_id:
        # Group message
        await manager.broadcast_to_group(
            message_dict, message_data.group_id, exclude_user_id=current_user.id
        )

    return MessageResponse.model_validate(message)


@router.get("", response_model=list[MessageResponse])
async def get_messages(
    receiver_id: UUID | None = Query(None, description="Filter by receiver"),
    group_id: UUID | None = Query(None, description="Filter by group"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[MessageResponse]:
    """Get messages for current user."""
    query = select(Message).where(
        (Message.sender_id == current_user.id) | (Message.receiver_id == current_user.id)
    )

    if receiver_id:
        query = query.where(
            ((Message.sender_id == current_user.id) & (Message.receiver_id == receiver_id))
            | ((Message.sender_id == receiver_id) & (Message.receiver_id == current_user.id))
        )

    if group_id:
        query = query.where(Message.group_id == group_id)

    query = query.order_by(desc(Message.created_at)).limit(limit).offset(offset)

    result = await db.execute(query)
    messages = result.scalars().all()

    # Load senders
    for message in messages:
        await db.refresh(message, ["sender"])

    return [MessageResponse.model_validate(msg) for msg in messages]


@router.patch("/{message_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_message_as_read(
    message_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Mark message as read."""
    result = await db.execute(
        select(Message).where(Message.id == message_id, Message.receiver_id == current_user.id)
    )
    message = result.scalar_one_or_none()

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found",
        )

    message.is_read = True
    await db.commit()
