"""
Profile endpoints
Handles retrieving, updating, and deleting the authenticated user's profile.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.core.security import get_current_user
from app.models import Customer
from app.schemas import CustomerResponse, ProfileUpdate

logger = logging.getLogger(__name__)

router = APIRouter()


def _get_current_customer(db: Session, current_user: dict) -> Customer:
    """Resolve the Customer row for the authenticated user or raise 404."""
    customer = db.query(Customer).filter(
        Customer.customer_id == int(current_user["user_id"])
    ).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return customer


@router.get("", response_model=CustomerResponse)
async def get_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the authenticated user's profile."""
    customer = _get_current_customer(db, current_user)
    return CustomerResponse.model_validate(customer)


@router.put("", response_model=CustomerResponse)
async def update_profile(
    payload: ProfileUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update the authenticated user's profile fields."""
    customer = _get_current_customer(db, current_user)

    update_data = payload.model_dump(exclude_unset=True)

    # Guard against email collisions with another account
    new_email = update_data.get("email")
    if new_email and new_email != customer.email:
        existing = db.query(Customer).filter(Customer.email == new_email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already in use by another account.",
            )

    for key, value in update_data.items():
        setattr(customer, key, value)

    try:
        db.commit()
        db.refresh(customer)
    except Exception:
        db.rollback()
        logger.exception("Failed to update profile for user %s", customer.customer_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the profile",
        )

    return CustomerResponse.model_validate(customer)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Permanently delete the authenticated user's account and related data."""
    customer = _get_current_customer(db, current_user)
    try:
        db.delete(customer)  # cascades to addresses, carts, orders via ORM relationships
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Failed to delete account for user %s", customer.customer_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the account",
        )
    return None
