"""
Order service layer for ecommerce checkout operations.
Handles creating orders from cart, inventory updates, payment records, and order retrieval.
"""

from datetime import datetime
from uuid import uuid4
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models import (
    Cart,
    CartItem,
    Order,
    OrderItem,
    Payment,
    Product,
    Address,
    InventoryLog,
    PaymentStatus,
    OrderStatus,
    InventoryChangeType,
)
from app.services.cart_service import CartService


class OrderService:
    """Service layer for order creation and management."""

    @staticmethod
    def create_order_from_cart(
        db: Session,
        customer_id: int,
        address_id: int,
        payment_method: str,
        tax_amount: float = 0,
        discount_amount: float = 0,
        shipping_fee: float = 0,
    ) -> Order:
        if tax_amount < 0 or discount_amount < 0 or shipping_fee < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tax, discount, and shipping fees must be non-negative"
            )

        cart = db.query(Cart).filter(Cart.customer_id == customer_id).first()
        if not cart or not cart.cart_items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cart is empty"
            )

        address = db.query(Address).filter(
            Address.address_id == address_id,
            Address.customer_id == customer_id
        ).first()
        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shipping address not found"
            )

        # Validate inventory and calculate totals
        subtotal = 0
        for item in cart.cart_items:
            if not item.product or not item.product.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product {item.product_id} is unavailable"
                )
            if item.quantity > item.product.stock_quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient inventory for product {item.product_id}"
                )
            subtotal += float(item.quantity) * float(item.product.selling_price)

        total_amount = subtotal + tax_amount + shipping_fee - discount_amount
        if total_amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Total amount must be greater than 0"
            )

        try:
            with db.begin():
                order = Order(
                    customer_id=customer_id,
                    address_id=address_id,
                    payment_method=payment_method,
                    payment_status=PaymentStatus.COMPLETED,
                    order_status=OrderStatus.CONFIRMED,
                    subtotal=subtotal,
                    tax_amount=tax_amount,
                    discount_amount=discount_amount,
                    shipping_fee=shipping_fee,
                    total_amount=total_amount,
                )
                db.add(order)
                db.flush()

                for item in cart.cart_items:
                    order_item = OrderItem(
                        order_id=order.order_id,
                        product_id=item.product_id,
                        quantity=item.quantity,
                        unit_price=item.product.selling_price,
                    )
                    db.add(order_item)

                    item.product.stock_quantity -= item.quantity
                    if item.product.stock_quantity < 0:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Negative inventory prevented for product {item.product_id}"
                        )

                    inventory_log = InventoryLog(
                        product_id=item.product_id,
                        change_type=InventoryChangeType.PURCHASE,
                        quantity_changed=-item.quantity,
                        reason="Checkout order created"
                    )
                    db.add(inventory_log)

                payment = Payment(
                    order_id=order.order_id,
                    payment_method=payment_method,
                    payment_status=PaymentStatus.COMPLETED,
                    transaction_reference=f"PAY-{uuid4().hex}",
                    amount=total_amount,
                    paid_at=datetime.utcnow(),
                )
                db.add(payment)

                db.query(CartItem).filter(CartItem.cart_id == cart.cart_id).delete(synchronize_session=False)

                db.flush()
                db.refresh(order)

            return order
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to create order from cart"
            )

    @staticmethod
    def get_order_by_id(db: Session, order_id: int, customer_id: int) -> Order:
        order = db.query(Order).filter(
            Order.order_id == order_id,
            Order.customer_id == customer_id
        ).first()
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        return order
