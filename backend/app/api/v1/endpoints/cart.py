"""
Cart API endpoints for ecommerce cart operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.core.security import get_current_user
from app.schemas import CartItemCreate, CartItemUpdate, CartResponse, CartItemResponse
from app.services.cart_service import CartService

router = APIRouter()


@router.post("/items", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED)
async def add_product_to_cart(
    item_data: CartItemCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a product to the current user's cart."""
    customer_id = int(current_user["user_id"])
    try:
        cart_item = CartService.add_product_to_cart(
            db=db,
            customer_id=customer_id,
            product_id=item_data.product_id,
            quantity=item_data.quantity,
        )
        return CartItemResponse.model_validate(cart_item)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to add product to cart"
        )


@router.put("/items/{cart_item_id}", response_model=CartItemResponse)
async def update_cart_quantity(
    cart_item_id: int,
    item_update: CartItemUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update quantity of an existing cart item."""
    try:
        cart_item = CartService.update_cart_item_quantity(
            db=db,
            cart_item_id=cart_item_id,
            quantity=item_update.quantity,
        )
        return CartItemResponse.model_validate(cart_item)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to update cart item"
        )


@router.delete("/items/{cart_item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_cart_item(
    cart_item_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove a cart item from the current user's cart."""
    try:
        CartService.remove_cart_item(db=db, cart_item_id=cart_item_id)
        return None
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to remove cart item"
        )


@router.get("", response_model=CartResponse)
async def view_cart(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """View the current user's cart."""
    customer_id = int(current_user["user_id"])
    try:
        cart = CartService.get_cart_by_customer(db=db, customer_id=customer_id)
        return CartResponse.model_validate(cart)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to fetch cart"
        )
