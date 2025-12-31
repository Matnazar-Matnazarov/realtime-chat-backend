"""
Contact API routes.
"""

from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.dependencies import get_current_user, get_db
from app.models.contact import Contact
from app.models.user import User
from app.schemas.contact import ContactCreate, ContactResponse

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.post("", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    contact_data: ContactCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ContactResponse:
    """Add a contact."""
    # Cannot add yourself
    if contact_data.contact_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot add yourself as a contact",
        )

    # Verify user exists
    result = await db.execute(select(User).where(User.id == contact_data.contact_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Check if already a contact
    result = await db.execute(
        select(Contact).where(
            Contact.user_id == current_user.id, Contact.contact_id == contact_data.contact_id
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already in your contacts",
        )

    # Create contact
    contact = Contact(
        id=uuid4(),
        user_id=current_user.id,
        contact_id=contact_data.contact_id,
        nickname=contact_data.nickname,
    )

    db.add(contact)
    await db.commit()
    await db.refresh(contact, ["contact"])

    return ContactResponse.model_validate(contact)


@router.get("", response_model=list[ContactResponse])
async def get_contacts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ContactResponse]:
    """Get all contacts for current user."""
    result = await db.execute(
        select(Contact)
        .where(Contact.user_id == current_user.id)
        .options(selectinload(Contact.contact))
    )
    contacts = result.scalars().all()

    return [ContactResponse.model_validate(c) for c in contacts]


@router.get("/chats", response_model=list[dict])
async def get_chat_list(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[dict]:
    """Get chat list with all users who have exchanged messages (Telegram-like).
    
    Returns list of users with:
    - User information
    - Last message
    - Unread message count
    - Sorted by last message time (most recent first)
    """
    from app.models.message import Message
    from sqlalchemy import func, or_, and_, case
    from app.schemas.user import UserPublic
    
    # Get all unique user IDs that have messages with current user
    # (both as sender and receiver)
    other_user_expr = case(
        (Message.sender_id == current_user.id, Message.receiver_id),
        else_=Message.sender_id
    )
    
    subquery = (
        select(
            other_user_expr.label("other_user_id"),
            func.max(Message.created_at).label("last_message_time"),
            func.count(
                case(
                    (and_(
                        Message.receiver_id == current_user.id,
                        Message.is_read == False
                    ), Message.id),
                    else_=None
                )
            ).label("unread_count")
        )
        .where(
            or_(
                Message.sender_id == current_user.id,
                Message.receiver_id == current_user.id
            )
        )
        .group_by(other_user_expr)
        .subquery()
    )
    
    # Get user details and join with subquery
    result = await db.execute(
        select(
            User,
            subquery.c.last_message_time,
            subquery.c.unread_count
        )
        .join(subquery, User.id == subquery.c.other_user_id)
        .where(User.id != current_user.id)
        .order_by(subquery.c.last_message_time.desc())
    )
    
    rows = result.all()
    
    # Get last message for each user
    chat_list = []
    for user, last_message_time, unread_count in rows:
        # Get last message
        last_message_result = await db.execute(
            select(Message)
            .where(
                or_(
                    and_(Message.sender_id == current_user.id, Message.receiver_id == user.id),
                    and_(Message.sender_id == user.id, Message.receiver_id == current_user.id)
                )
            )
            .order_by(Message.created_at.desc())
            .limit(1)
        )
        last_message = last_message_result.scalar_one_or_none()
        
        # Get contact if exists
        contact_result = await db.execute(
            select(Contact)
            .where(
                Contact.user_id == current_user.id,
                Contact.contact_id == user.id
            )
        )
        contact = contact_result.scalar_one_or_none()
        
        chat_item = {
            "id": str(user.id),
            "user": UserPublic.model_validate(user).model_dump(),
            "last_message": {
                "id": str(last_message.id),
                "content": last_message.content,
                "sender_id": str(last_message.sender_id),
                "receiver_id": str(last_message.receiver_id) if last_message.receiver_id else None,
                "media_url": last_message.media_url,
                "media_type": last_message.media_type,
                "is_read": last_message.is_read,
                "created_at": last_message.created_at.isoformat(),
            } if last_message else None,
            "unread_count": unread_count or 0,
            "is_contact": contact is not None,
        }
        chat_list.append(chat_item)
    
    return chat_list


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Remove a contact."""
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id, Contact.user_id == current_user.id)
    )
    contact = result.scalar_one_or_none()

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )

    await db.delete(contact)
    await db.commit()
