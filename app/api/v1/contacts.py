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
