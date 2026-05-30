"""
Examples of how to use SQLAlchemy models

This file demonstrates common database operations and queries
for the E-Commerce platform.
"""

from sqlalchemy.orm import Session, joinedload
from app.db.base import SessionLocal
from app.models import (
    Customer, Address, Category, Product, Cart, CartItem,
    Order, OrderItem, Payment, InventoryLog,
    AccountStatus, OrderStatus, PaymentStatus, InventoryChangeType
)
from app.core.security import hash_password, verify_password
from datetime import datetime, timedelta


# ==================== Customer Examples ====================

def create_customer_example(db: Session):
    """Example: Create a new customer"""
    customer = Customer(
        first_name="John",
        last_name="Doe",
        email="johndoe@example.com",
        password_hash=hash_password("secure_password_123"),
        phone_number="+1-555-0101",
        account_status=AccountStatus.ACTIVE
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    print(f"Created customer: {customer}")
    return customer


def get_customer_by_email_example(db: Session, email: str):
    """Example: Retrieve customer by email"""
    customer = db.query(Customer).filter(
        Customer.email == email
    ).first()
    
    if customer:
        print(f"Found customer: {customer.first_name} {customer.last_name}")
    else:
        print("Customer not found")
    
    return customer


def get_customer_with_relations_example(db: Session, customer_id: int):
    """Example: Retrieve customer with all related data"""
    customer = db.query(Customer).options(
        joinedload(Customer.addresses),
        joinedload(Customer.orders),
        joinedload(Customer.carts)
    ).filter(Customer.customer_id == customer_id).first()
    
    if customer:
        print(f"Customer: {customer.first_name}")
        print(f"Addresses: {len(customer.addresses)}")
        print(f"Orders: {len(customer.orders)}")
        print(f"Carts: {len(customer.carts)}")
    
    return customer


def update_customer_example(db: Session, customer_id: int):
    """Example: Update customer information"""
    customer = db.query(Customer).filter(
        Customer.customer_id == customer_id
    ).first()
    
    if customer:
        customer.phone_number = "+1-555-9999"
        customer.account_status = AccountStatus.ACTIVE
        db.commit()
        print(f"Updated customer: {customer}")
    
    return customer


def list_active_customers_example(db: Session):
    """Example: List all active customers"""
    customers = db.query(Customer).filter(
        Customer.account_status == AccountStatus.ACTIVE
    ).all()
    
    print(f"Total active customers: {len(customers)}")
    for customer in customers:
        print(f"  - {customer.first_name} {customer.last_name}")
    
    return customers


# ==================== Address Examples ====================

def add_address_to_customer_example(db: Session, customer_id: int):
    """Example: Add address to customer"""
    address = Address(
        customer_id=customer_id,
        address_line1="123 Main Street",
        address_line2="Apt 4B",
        city="New York",
        state="NY",
        country="USA",
        pincode="10001",
        is_default=True
    )
    db.add(address)
    db.commit()
    db.refresh(address)
    print(f"Created address: {address}")
    return address


def get_customer_addresses_example(db: Session, customer_id: int):
    """Example: Get all addresses for a customer"""
    addresses = db.query(Address).filter(
        Address.customer_id == customer_id
    ).all()
    
    print(f"Customer has {len(addresses)} addresses:")
    for addr in addresses:
        print(f"  - {addr.address_line1}, {addr.city}, {addr.state}")
    
    return addresses


def get_default_address_example(db: Session, customer_id: int):
    """Example: Get default address for a customer"""
    address = db.query(Address).filter(
        Address.customer_id == customer_id,
        Address.is_default == True
    ).first()
    
    if address:
        print(f"Default address: {address.address_line1}")
    
    return address


# ==================== Category Examples ====================

def create_category_example(db: Session):
    """Example: Create a product category"""
    category = Category(
        category_name="Electronics",
        description="Electronic devices and accessories"
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    print(f"Created category: {category}")
    return category


def list_categories_example(db: Session):
    """Example: List all categories"""
    categories = db.query(Category).all()
    
    print(f"Total categories: {len(categories)}")
    for cat in categories:
        print(f"  - {cat.category_name}")
    
    return categories


# ==================== Product Examples ====================

def create_product_example(db: Session, category_id: int):
    """Example: Create a product"""
    product = Product(
        product_name="Laptop",
        category_id=category_id,
        brand="TechBrand",
        description="High-performance laptop for professionals",
        selling_price=999.99,
        cost_price=700.00,
        stock_quantity=50,
        is_active=True
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    print(f"Created product: {product}")
    return product


def get_products_by_category_example(db: Session, category_id: int):
    """Example: Get all products in a category"""
    products = db.query(Product).filter(
        Product.category_id == category_id,
        Product.is_active == True
    ).all()
    
    print(f"Found {len(products)} products in category {category_id}")
    for product in products:
        print(f"  - {product.product_name}: ${product.selling_price}")
    
    return products


def search_products_example(db: Session, search_term: str):
    """Example: Search products by name"""
    products = db.query(Product).filter(
        Product.product_name.ilike(f"%{search_term}%"),
        Product.is_active == True
    ).all()
    
    print(f"Search results for '{search_term}': {len(products)} products")
    return products


def get_low_stock_products_example(db: Session, threshold: int = 10):
    """Example: Get products with low stock"""
    products = db.query(Product).filter(
        Product.stock_quantity < threshold,
        Product.is_active == True
    ).all()
    
    print(f"Products with stock below {threshold}: {len(products)}")
    for product in products:
        print(f"  - {product.product_name}: {product.stock_quantity} units")
    
    return products


def update_product_price_example(db: Session, product_id: int, new_price: float):
    """Example: Update product price"""
    product = db.query(Product).filter(
        Product.product_id == product_id
    ).first()
    
    if product:
        old_price = product.selling_price
        product.selling_price = new_price
        db.commit()
        print(f"Updated {product.product_name}: ${old_price} -> ${new_price}")
    
    return product


# ==================== Cart Examples ====================

def create_cart_example(db: Session, customer_id: int):
    """Example: Create a shopping cart"""
    cart = Cart(customer_id=customer_id)
    db.add(cart)
    db.commit()
    db.refresh(cart)
    print(f"Created cart: {cart}")
    return cart


def add_item_to_cart_example(db: Session, cart_id: int, product_id: int, quantity: int):
    """Example: Add item to cart"""
    # Check if item already exists
    cart_item = db.query(CartItem).filter(
        CartItem.cart_id == cart_id,
        CartItem.product_id == product_id
    ).first()
    
    if cart_item:
        cart_item.quantity += quantity
        print(f"Updated cart item quantity to {cart_item.quantity}")
    else:
        cart_item = CartItem(
            cart_id=cart_id,
            product_id=product_id,
            quantity=quantity
        )
        db.add(cart_item)
        print(f"Added item to cart")
    
    db.commit()
    return cart_item


def get_cart_total_example(db: Session, cart_id: int):
    """Example: Calculate cart total"""
    cart_items = db.query(CartItem).options(
        joinedload(CartItem.product)
    ).filter(CartItem.cart_id == cart_id).all()
    
    total = 0
    for item in cart_items:
        subtotal = item.quantity * item.product.selling_price
        total += subtotal
        print(f"  {item.product.product_name} x{item.quantity}: ${subtotal}")
    
    print(f"Cart Total: ${total}")
    return total


def clear_cart_example(db: Session, cart_id: int):
    """Example: Clear cart"""
    db.query(CartItem).filter(CartItem.cart_id == cart_id).delete()
    db.commit()
    print(f"Cart {cart_id} cleared")


# ==================== Order Examples ====================

def create_order_example(db: Session, customer_id: int, address_id: int, items_data: list):
    """Example: Create an order from cart"""
    # Calculate totals
    subtotal = 0
    for item_data in items_data:
        product = db.query(Product).get(item_data['product_id'])
        subtotal += product.selling_price * item_data['quantity']
    
    tax_amount = subtotal * 0.1  # 10% tax
    total_amount = subtotal + tax_amount
    
    # Create order
    order = Order(
        customer_id=customer_id,
        address_id=address_id,
        payment_method="credit_card",
        payment_status=PaymentStatus.PENDING,
        order_status=OrderStatus.PENDING,
        subtotal=subtotal,
        tax_amount=tax_amount,
        discount_amount=0,
        shipping_fee=10,
        total_amount=total_amount + 10
    )
    db.add(order)
    db.flush()  # Get the order_id without committing
    
    # Add order items
    for item_data in items_data:
        product = db.query(Product).get(item_data['product_id'])
        order_item = OrderItem(
            order_id=order.order_id,
            product_id=item_data['product_id'],
            quantity=item_data['quantity'],
            unit_price=product.selling_price
        )
        db.add(order_item)
        
        # Update inventory
        product.stock_quantity -= item_data['quantity']
        
        # Log inventory change
        inventory_log = InventoryLog(
            product_id=item_data['product_id'],
            change_type=InventoryChangeType.PURCHASE,
            quantity_changed=-item_data['quantity'],
            reason=f"Order #{order.order_id}"
        )
        db.add(inventory_log)
    
    db.commit()
    print(f"Created order: {order}")
    return order


def get_customer_orders_example(db: Session, customer_id: int):
    """Example: Get all orders for a customer"""
    orders = db.query(Order).options(
        joinedload(Order.order_items).joinedload(OrderItem.product),
        joinedload(Order.address)
    ).filter(
        Order.customer_id == customer_id
    ).order_by(Order.placed_at.desc()).all()
    
    print(f"Customer has {len(orders)} orders:")
    for order in orders:
        print(f"  - Order #{order.order_id}: ${order.total_amount} ({order.order_status.value})")
    
    return orders


def update_order_status_example(db: Session, order_id: int, new_status: OrderStatus):
    """Example: Update order status"""
    order = db.query(Order).filter(Order.order_id == order_id).first()
    
    if order:
        old_status = order.order_status
        order.order_status = new_status
        
        # Update timestamps based on status
        if new_status == OrderStatus.SHIPPED:
            order.shipped_at = datetime.utcnow()
        elif new_status == OrderStatus.DELIVERED:
            order.delivered_at = datetime.utcnow()
        elif new_status == OrderStatus.CANCELLED:
            order.cancelled_at = datetime.utcnow()
        
        db.commit()
        print(f"Updated order status: {old_status.value} -> {new_status.value}")
    
    return order


def get_pending_orders_example(db: Session):
    """Example: Get all pending orders"""
    orders = db.query(Order).filter(
        Order.order_status == OrderStatus.PENDING
    ).order_by(Order.placed_at.asc()).all()
    
    print(f"Pending orders: {len(orders)}")
    return orders


# ==================== Payment Examples ====================

def create_payment_example(db: Session, order_id: int, amount: float):
    """Example: Record a payment"""
    payment = Payment(
        order_id=order_id,
        payment_method="credit_card",
        payment_status=PaymentStatus.COMPLETED,
        transaction_reference="TXN-20260530-001",
        amount=amount,
        paid_at=datetime.utcnow()
    )
    db.add(payment)
    
    # Update order payment status
    order = db.query(Order).get(order_id)
    if order:
        order.payment_status = PaymentStatus.COMPLETED
    
    db.commit()
    print(f"Created payment: {payment}")
    return payment


def get_order_payment_history_example(db: Session, order_id: int):
    """Example: Get payment history for an order"""
    payments = db.query(Payment).filter(
        Payment.order_id == order_id
    ).order_by(Payment.created_at.desc()).all()
    
    print(f"Payment history for order {order_id}:")
    for payment in payments:
        print(f"  - ${payment.amount} ({payment.payment_status.value})")
    
    return payments


# ==================== Inventory Examples ====================

def log_inventory_adjustment_example(db: Session, product_id: int, quantity_change: int, reason: str):
    """Example: Log inventory adjustment"""
    product = db.query(Product).get(product_id)
    
    if product:
        product.stock_quantity += quantity_change
        
        log = InventoryLog(
            product_id=product_id,
            change_type=InventoryChangeType.ADJUSTMENT,
            quantity_changed=quantity_change,
            reason=reason
        )
        db.add(log)
        db.commit()
        print(f"Logged inventory adjustment: {reason}")
    
    return log


def get_inventory_history_example(db: Session, product_id: int):
    """Example: Get inventory change history"""
    logs = db.query(InventoryLog).filter(
        InventoryLog.product_id == product_id
    ).order_by(InventoryLog.changed_at.desc()).limit(10).all()
    
    print(f"Inventory history for product {product_id}:")
    for log in logs:
        print(f"  - {log.change_type.value}: {log.quantity_changed}")
    
    return logs


# ==================== Analytics Examples ====================

def get_sales_summary_example(db: Session, days: int = 30):
    """Example: Get sales summary for the last N days"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    orders = db.query(Order).filter(
        Order.placed_at >= start_date,
        Order.order_status == OrderStatus.DELIVERED
    ).all()
    
    total_revenue = sum(order.total_amount for order in orders)
    total_orders = len(orders)
    
    print(f"Sales Summary (last {days} days):")
    print(f"  Total Orders: {total_orders}")
    print(f"  Total Revenue: ${total_revenue}")
    if total_orders > 0:
        print(f"  Average Order Value: ${total_revenue / total_orders}")


def get_top_products_example(db: Session, limit: int = 5):
    """Example: Get top selling products"""
    from sqlalchemy import func, desc
    
    top_products = db.query(
        Product,
        func.sum(OrderItem.quantity).label('total_quantity')
    ).join(OrderItem).group_by(Product.product_id).order_by(
        desc('total_quantity')
    ).limit(limit).all()
    
    print(f"Top {limit} Selling Products:")
    for product, qty in top_products:
        print(f"  - {product.product_name}: {qty} units")


def get_customer_spending_example(db: Session, customer_id: int):
    """Example: Get customer total spending"""
    from sqlalchemy import func
    
    total_spending = db.query(
        func.sum(Order.total_amount)
    ).filter(
        Order.customer_id == customer_id,
        Order.order_status == OrderStatus.DELIVERED
    ).scalar() or 0
    
    order_count = db.query(Order).filter(
        Order.customer_id == customer_id,
        Order.order_status == OrderStatus.DELIVERED
    ).count()
    
    print(f"Customer Spending:")
    print(f"  Total Spent: ${total_spending}")
    print(f"  Total Orders: {order_count}")


if __name__ == "__main__":
    # Example usage
    db = SessionLocal()
    
    # Create category
    category = create_category_example(db)
    
    # Create product
    product = create_product_example(db, category.category_id)
    
    # Create customer
    customer = create_customer_example(db)
    
    # Add address
    address = add_address_to_customer_example(db, customer.customer_id)
    
    # Create cart and add items
    cart = create_cart_example(db, customer.customer_id)
    add_item_to_cart_example(db, cart.cart_id, product.product_id, 2)
    
    # View cart total
    get_cart_total_example(db, cart.cart_id)
    
    # Create order
    order = create_order_example(db, customer.customer_id, address.address_id, [
        {'product_id': product.product_id, 'quantity': 2}
    ])
    
    # Update order status
    update_order_status_example(db, order.order_id, OrderStatus.CONFIRMED)
    
    # Record payment
    create_payment_example(db, order.order_id, order.total_amount)
    
    db.close()
