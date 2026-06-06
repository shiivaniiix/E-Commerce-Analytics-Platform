"""
Address endpoints
Full CRUD for the authenticated user's addresses, including default handling.
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.core.security import get_current_user
from app.models import Address
from app.schemas import AddressCreate, AddressUpdate, AddressResponse

logger = logging.getLogger(__name__)

router = APIRouter()


def _current_user_id(current_user: dict) -> int:
    return int(current_user["user_id"])


def _get_owned_address(db: Session, address_id: int, user_id: int) -> Address:
    """Fetch an address that belongs to the user, or raise 404."""
    address = db.query(Address).filter(
        Address.address_id == address_id,
        Address.customer_id == user_id,
    ).first()
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found",
        )
    return address


def _clear_other_defaults(db: Session, user_id: int, keep_address_id: Optional[int] = None) -> None:
    """Unset is_default on all other addresses for this user."""
    query = db.query(Address).filter(
        Address.customer_id == user_id,
        Address.is_default == True,  # noqa: E712
    )
    if keep_address_id is not None:
        query = query.filter(Address.address_id != keep_address_id)
    for addr in query.all():
        addr.is_default = False


@router.get("", response_model=List[AddressResponse])
async def list_addresses(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all addresses for the authenticated user (default first)."""
    user_id = _current_user_id(current_user)
    addresses = (
        db.query(Address)
        .filter(Address.customer_id == user_id)
        .order_by(Address.is_default.desc(), Address.created_at.desc())
        .all()
    )
    return [AddressResponse.model_validate(a) for a in addresses]


@router.post("", response_model=AddressResponse, status_code=status.HTTP_201_CREATED)
async def create_address(
    payload: AddressCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new address for the authenticated user."""
    user_id = _current_user_id(current_user)

    # If this is the user's first address, force it to be default.
    has_any = db.query(Address).filter(Address.customer_id == user_id).count() > 0
    make_default = payload.is_default or not has_any

    address = Address(
        customer_id=user_id,
        **payload.model_dump(exclude={"is_default"}),
        is_default=make_default,
    )

    try:
        if make_default:
            _clear_other_defaults(db, user_id)
        db.add(address)
        db.commit()
        db.refresh(address)
    except Exception:
        db.rollback()
        logger.exception("Failed to create address for user %s", user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the address",
        )

    return AddressResponse.model_validate(address)


@router.put("/{address_id}", response_model=AddressResponse)
async def update_address(
    payload: AddressUpdate,
    address_id: int = Path(..., ge=1),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update an existing address owned by the authenticated user."""
    user_id = _current_user_id(current_user)
    address = _get_owned_address(db, address_id, user_id)

    update_data = payload.model_dump(exclude_unset=True)
    setting_default = update_data.get("is_default") is True

    for key, value in update_data.items():
        setattr(address, key, value)

    try:
        if setting_default:
            _clear_other_defaults(db, user_id, keep_address_id=address.address_id)
            address.is_default = True
        db.commit()
        db.refresh(address)
    except Exception:
        db.rollback()
        logger.exception("Failed to update address %s", address_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the address",
        )

    return AddressResponse.model_validate(address)


@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_address(
    address_id: int = Path(..., ge=1),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete an address owned by the authenticated user."""
    user_id = _current_user_id(current_user)
    address = _get_owned_address(db, address_id, user_id)
    was_default = address.is_default

    try:
        db.delete(address)
        db.flush()
        # Promote another address to default if we removed the default one.
        if was_default:
            replacement = (
                db.query(Address)
                .filter(Address.customer_id == user_id)
                .order_by(Address.created_at.desc())
                .first()
            )
            if replacement:
                replacement.is_default = True
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Failed to delete address %s", address_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the address",
        )
    return None
