"""
SQLAlchemy ORM models for E-Commerce Analytics Platform
Implements all database tables with proper relationships and constraints
"""

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean, Text, 
    ForeignKey, Enum, Numeric, Index
)
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from app.db.base import Base


# ==================== Enums ====================

class AccountStatus(str, PyEnum):
    """Customer account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class OrderStatus(str, PyEnum):
    """Order status"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    RETURNED = "returned"


class PaymentStatus(str, PyEnum):
    """Payment status"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class InventoryChangeType(str, PyEnum):
    """Type of inventory change"""
    PURCHASE = "purchase"
    RETURN = "return"
    RESTOCK = "restock"
    DAMAGED = "damaged"
    ADJUSTMENT = "adjustment"


# ==================== Models ====================

class Customer(Base):
    """Customer model - main customer information"""
    __tablename__ = "customers"
    __table_args__ = (
        Index('idx_customer_email', 'email'),
        Index('idx_customer_phone', 'phone_number'),
    )

    customer_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=True)
    account_created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    account_status = Column(
        Enum(AccountStatus),
        default=AccountStatus.ACTIVE,
        nullable=False
    )

    # Relationships
    addresses = relationship(
        "Address",
        back_populates="customer",
        cascade="all, delete-orphan",
        lazy="select"
    )
    carts = relationship(
        "Cart",
        back_populates="customer",
        cascade="all, delete-orphan",
        lazy="select"
    )
    orders = relationship(
        "Order",
        back_populates="customer",
        cascade="all, delete-orphan",
        lazy="select"
    )

    def __repr__(self):
        return f"<Customer(customer_id={self.customer_id}, email={self.email})>"


class Address(Base):
    """Address model - customer addresses"""
    __tablename__ = "addresses"
    __table_args__ = (
        Index('idx_address_customer', 'customer_id'),
    )

    address_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(
        Integer,
        ForeignKey("customers.customer_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    address_line1 = Column(String(255), nullable=False)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False)
    pincode = Column(String(20), nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="addresses")
    orders = relationship(
        "Order",
        back_populates="address",
        cascade="all, delete-orphan",
        lazy="select"
    )

    def __repr__(self):
        return f"<Address(address_id={self.address_id}, customer_id={self.customer_id})>"


class Category(Base):
    """Category model - product categories"""
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String(150), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    products = relationship(
        "Product",
        back_populates="category",
        cascade="all, delete-orphan",
        lazy="select"
    )

    def __repr__(self):
        return f"<Category(category_id={self.category_id}, category_name={self.category_name})>"


class Product(Base):
    """Product model - product information"""
    __tablename__ = "products"
    __table_args__ = (
        Index('idx_product_category', 'category_id'),
        Index('idx_product_is_active', 'is_active'),
    )

    product_id = Column(Integer, primary_key=True, autoincrement=True)
    product_name = Column(String(255), nullable=False, index=True)
    category_id = Column(
        Integer,
        ForeignKey("categories.category_id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    brand = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    selling_price = Column(Numeric(10, 2), nullable=False)
    cost_price = Column(Numeric(10, 2), nullable=False)
    stock_quantity = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    category = relationship("Category", back_populates="products")
    cart_items = relationship(
        "CartItem",
        back_populates="product",
        cascade="all, delete-orphan",
        lazy="select"
    )
    order_items = relationship(
        "OrderItem",
        back_populates="product",
        cascade="all, delete-orphan",
        lazy="select"
    )
    inventory_logs = relationship(
        "InventoryLog",
        back_populates="product",
        cascade="all, delete-orphan",
        lazy="select"
    )

    def __repr__(self):
        return f"<Product(product_id={self.product_id}, product_name={self.product_name})>"


class Cart(Base):
    """Cart model - shopping cart"""
    __tablename__ = "carts"
    __table_args__ = (
        Index('idx_cart_customer', 'customer_id'),
    )

    cart_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(
        Integer,
        ForeignKey("customers.customer_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="carts")
    cart_items = relationship(
        "CartItem",
        back_populates="cart",
        cascade="all, delete-orphan",
        lazy="select"
    )

    def __repr__(self):
        return f"<Cart(cart_id={self.cart_id}, customer_id={self.customer_id})>"


class CartItem(Base):
    """Cart Item model - items in shopping cart"""
    __tablename__ = "cart_items"
    __table_args__ = (
        Index('idx_cart_item_cart', 'cart_id'),
        Index('idx_cart_item_product', 'product_id'),
    )

    cart_item_id = Column(Integer, primary_key=True, autoincrement=True)
    cart_id = Column(
        Integer,
        ForeignKey("carts.cart_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    product_id = Column(
        Integer,
        ForeignKey("products.product_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    quantity = Column(Integer, nullable=False, default=1)
    added_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    cart = relationship("Cart", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")

    def __repr__(self):
        return f"<CartItem(cart_item_id={self.cart_item_id}, product_id={self.product_id})>"


class Order(Base):
    """Order model - customer orders"""
    __tablename__ = "orders"
    __table_args__ = (
        Index('idx_order_customer', 'customer_id'),
        Index('idx_order_address', 'address_id'),
        Index('idx_order_status', 'order_status'),
        Index('idx_order_placed_at', 'placed_at'),
    )

    order_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(
        Integer,
        ForeignKey("customers.customer_id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    address_id = Column(
        Integer,
        ForeignKey("addresses.address_id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    payment_method = Column(String(50), nullable=False)  # credit_card, debit_card, upi, wallet
    payment_status = Column(
        Enum(PaymentStatus),
        default=PaymentStatus.PENDING,
        nullable=False
    )
    order_status = Column(
        Enum(OrderStatus),
        default=OrderStatus.PENDING,
        nullable=False
    )
    subtotal = Column(Numeric(12, 2), nullable=False)
    tax_amount = Column(Numeric(12, 2), default=0, nullable=False)
    discount_amount = Column(Numeric(12, 2), default=0, nullable=False)
    shipping_fee = Column(Numeric(12, 2), default=0, nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False)
    placed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    shipped_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="orders")
    address = relationship("Address", back_populates="orders")
    order_items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="select"
    )
    payments = relationship(
        "Payment",
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="select"
    )

    def __repr__(self):
        return f"<Order(order_id={self.order_id}, customer_id={self.customer_id})>"


class OrderItem(Base):
    """Order Item model - items in an order"""
    __tablename__ = "order_items"
    __table_args__ = (
        Index('idx_order_item_order', 'order_id'),
        Index('idx_order_item_product', 'product_id'),
    )

    order_item_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(
        Integer,
        ForeignKey("orders.order_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    product_id = Column(
        Integer,
        ForeignKey("products.product_id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")

    def __repr__(self):
        return f"<OrderItem(order_item_id={self.order_item_id}, order_id={self.order_id})>"


class Payment(Base):
    """Payment model - payment transactions"""
    __tablename__ = "payments"
    __table_args__ = (
        Index('idx_payment_order', 'order_id'),
        Index('idx_payment_status', 'payment_status'),
    )

    payment_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(
        Integer,
        ForeignKey("orders.order_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    payment_method = Column(String(50), nullable=False)
    payment_status = Column(
        Enum(PaymentStatus),
        default=PaymentStatus.PENDING,
        nullable=False
    )
    transaction_reference = Column(String(255), nullable=True, unique=True, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    paid_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    order = relationship("Order", back_populates="payments")

    def __repr__(self):
        return f"<Payment(payment_id={self.payment_id}, order_id={self.order_id})>"


class InventoryLog(Base):
    """Inventory Log model - tracks inventory changes"""
    __tablename__ = "inventory_logs"
    __table_args__ = (
        Index('idx_inventory_log_product', 'product_id'),
        Index('idx_inventory_log_changed_at', 'changed_at'),
    )

    inventory_log_id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(
        Integer,
        ForeignKey("products.product_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    change_type = Column(
        Enum(InventoryChangeType),
        nullable=False
    )
    quantity_changed = Column(Integer, nullable=False)
    reason = Column(String(255), nullable=True)
    changed_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    product = relationship("Product", back_populates="inventory_logs")

    def __repr__(self):
        return f"<InventoryLog(inventory_log_id={self.inventory_log_id}, product_id={self.product_id})>"
