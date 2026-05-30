"""
Order API endpoints for ecommerce checkout operations.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.core.security import get_current_user
from app.models import Order
from app.schemas import OrderFromCartRequest, OrderResponse
from app.services.order_service import OrderService

router = APIRouter()


@router.post("/checkout", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order_from_cart(
    order_data: OrderFromCartRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create an order from the authenticated user's cart."""
    customer_id = int(current_user["user_id"])
    try:
        order = OrderService.create_order_from_cart(
            db=db,
            customer_id=customer_id,
            address_id=order_data.address_id,
            payment_method=order_data.payment_method,
            tax_amount=order_data.tax_amount,
            discount_amount=order_data.discount_amount,
            shipping_fee=order_data.shipping_fee,
        )
        return OrderResponse.model_validate(order)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to complete order checkout"
        )


@router.get("", response_model=List[OrderResponse])
async def list_orders(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List orders for the authenticated user."""
    customer_id = int(current_user["user_id"])
    try:
        orders = db.query(Order).filter(
            Order.customer_id == customer_id
        ).order_by(Order.created_at.desc()).all()
        return [OrderResponse.model_validate(order) for order in orders]
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to fetch orders"
        )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get an order by ID for the authenticated user."""
    customer_id = int(current_user["user_id"])
    try:
        order = OrderService.get_order_by_id(db=db, order_id=order_id, customer_id=customer_id)
        return OrderResponse.model_validate(order)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to fetch order"
        )
