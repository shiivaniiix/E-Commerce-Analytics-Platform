"""
Cart service layer for ecommerce operations.
Handles adding to cart, updating quantities, removing items, and retrieving cart contents.
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models import Cart, CartItem, Product


class CartService:
    """Service layer for cart operations."""

    @staticmethod
    def get_or_create_cart(db: Session, customer_id: int) -> Cart:
        cart = db.query(Cart).filter(Cart.customer_id == customer_id).first()
        if not cart:
            cart = Cart(customer_id=customer_id)
            db.add(cart)
            db.commit()
            db.refresh(cart)
        return cart

    @staticmethod
    def add_product_to_cart(db: Session, customer_id: int, product_id: int, quantity: int = 1) -> CartItem:
        if quantity < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quantity must be at least 1"
            )

        product = db.query(Product).filter(Product.product_id == product_id, Product.is_active == True).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        if product.stock_quantity < quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Requested quantity exceeds available stock"
            )

        cart = CartService.get_or_create_cart(db, customer_id)
        cart_item = db.query(CartItem).filter(
            CartItem.cart_id == cart.cart_id,
            CartItem.product_id == product_id
        ).first()

        if cart_item:
            new_quantity = cart_item.quantity + quantity
            if new_quantity > product.stock_quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Requested quantity exceeds available stock"
                )
            cart_item.quantity = new_quantity
        else:
            cart_item = CartItem(
                cart_id=cart.cart_id,
                product_id=product_id,
                quantity=quantity
            )
            db.add(cart_item)

        db.commit()
        db.refresh(cart_item)
        return cart_item

    @staticmethod
    def update_cart_item_quantity(db: Session, cart_item_id: int, quantity: int) -> CartItem:
        if quantity < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quantity must be at least 1"
            )

        cart_item = db.query(CartItem).filter(CartItem.cart_item_id == cart_item_id).first()
        if not cart_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart item not found"
            )

        product = db.query(Product).filter(Product.product_id == cart_item.product_id).first()
        if not product or not product.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Associated product not found"
            )

        if quantity > product.stock_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Requested quantity exceeds available stock"
            )

        cart_item.quantity = quantity
        db.commit()
        db.refresh(cart_item)
        return cart_item

    @staticmethod
    def remove_cart_item(db: Session, cart_item_id: int) -> bool:
        cart_item = db.query(CartItem).filter(CartItem.cart_item_id == cart_item_id).first()
        if not cart_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart item not found"
            )

        db.delete(cart_item)
        db.commit()
        return True

    @staticmethod
    def get_cart_by_customer(db: Session, customer_id: int) -> Cart:
        cart = db.query(Cart).filter(Cart.customer_id == customer_id).first()
        if not cart:
            cart = CartService.get_or_create_cart(db, customer_id)
        return cart

    @staticmethod
    def clear_cart(db: Session, customer_id: int) -> None:
        cart = db.query(Cart).filter(Cart.customer_id == customer_id).first()
        if not cart:
            return
        db.query(CartItem).filter(CartItem.cart_id == cart.cart_id).delete(synchronize_session=False)
        db.commit()
