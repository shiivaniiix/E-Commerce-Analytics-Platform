"""
Sample data fixtures for testing and development
"""

from app.db.base import SessionLocal, engine, Base
from app.models import (
    Customer, Address, Category, Product, Cart, CartItem,
    Order, OrderItem, Payment, InventoryLog,
    AccountStatus, OrderStatus, PaymentStatus, InventoryChangeType
)
from app.core.security import hash_password
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def load_sample_data():
    """Load sample data into the database"""
    db = SessionLocal()
    
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        
        # Create sample customers
        customers = [
            Customer(
                first_name="John",
                last_name="Doe",
                email="john@example.com",
                password_hash=hash_password("password123"),
                phone_number="+1-555-0101",
                account_status=AccountStatus.ACTIVE
            ),
            Customer(
                first_name="Jane",
                last_name="Smith",
                email="jane@example.com",
                password_hash=hash_password("password123"),
                phone_number="+1-555-0102",
                account_status=AccountStatus.ACTIVE
            ),
            Customer(
                first_name="Bob",
                last_name="Johnson",
                email="bob@example.com",
                password_hash=hash_password("password123"),
                phone_number="+1-555-0103",
                account_status=AccountStatus.ACTIVE
            ),
        ]
        db.add_all(customers)
        db.commit()
        logger.info(f"Created {len(customers)} sample customers")
        
        # Create sample addresses
        addresses = [
            Address(
                customer_id=customers[0].customer_id,
                address_line1="123 Main St",
                city="New York",
                state="NY",
                country="USA",
                pincode="10001",
                is_default=True
            ),
            Address(
                customer_id=customers[0].customer_id,
                address_line1="456 Oak Ave",
                city="Boston",
                state="MA",
                country="USA",
                pincode="02101",
                is_default=False
            ),
            Address(
                customer_id=customers[1].customer_id,
                address_line1="789 Elm St",
                city="Los Angeles",
                state="CA",
                country="USA",
                pincode="90001",
                is_default=True
            ),
        ]
        db.add_all(addresses)
        db.commit()
        logger.info(f"Created {len(addresses)} sample addresses")
        
        # Create sample categories
        categories = [
            Category(category_name="Electronics", description="Electronic devices"),
            Category(category_name="Clothing", description="Apparel and fashion"),
            Category(category_name="Books", description="Physical and digital books"),
            Category(category_name="Food", description="Grocery and food items"),
            Category(category_name="Home & Garden", description="Home and garden products"),
        ]
        db.add_all(categories)
        db.commit()
        logger.info(f"Created {len(categories)} sample categories")
        
        # Create sample products
        products = [
            Product(
                product_name="Laptop",
                category_id=categories[0].category_id,
                brand="TechBrand",
                description="High-performance laptop",
                selling_price=999.99,
                cost_price=700.00,
                stock_quantity=50,
                is_active=True
            ),
            Product(
                product_name="Smartphone",
                category_id=categories[0].category_id,
                brand="PhoneBrand",
                description="Latest smartphone model",
                selling_price=599.99,
                cost_price=400.00,
                stock_quantity=100,
                is_active=True
            ),
            Product(
                product_name="T-Shirt",
                category_id=categories[1].category_id,
                brand="FashionBrand",
                description="Comfortable cotton t-shirt",
                selling_price=29.99,
                cost_price=10.00,
                stock_quantity=200,
                is_active=True
            ),
            Product(
                product_name="Python Programming Book",
                category_id=categories[2].category_id,
                brand="TechBooks",
                description="Learn Python programming",
                selling_price=49.99,
                cost_price=25.00,
                stock_quantity=75,
                is_active=True
            ),
            Product(
                product_name="Coffee Maker",
                category_id=categories[4].category_id,
                brand="HomeBrand",
                description="Automatic coffee maker",
                selling_price=89.99,
                cost_price=50.00,
                stock_quantity=40,
                is_active=True
            ),
        ]
        db.add_all(products)
        db.commit()
        logger.info(f"Created {len(products)} sample products")
        
        # Create sample cart
        cart = Cart(customer_id=customers[0].customer_id)
        db.add(cart)
        db.commit()
        
        # Add items to cart
        cart_items = [
            CartItem(
                cart_id=cart.cart_id,
                product_id=products[0].product_id,
                quantity=1
            ),
            CartItem(
                cart_id=cart.cart_id,
                product_id=products[2].product_id,
                quantity=2
            ),
        ]
        db.add_all(cart_items)
        db.commit()
        logger.info(f"Created sample cart with {len(cart_items)} items")
        
        # Create sample order
        order = Order(
            customer_id=customers[1].customer_id,
            address_id=addresses[2].address_id,
            payment_method="credit_card",
            payment_status=PaymentStatus.COMPLETED,
            order_status=OrderStatus.DELIVERED,
            subtotal=629.98,
            tax_amount=50.40,
            discount_amount=0,
            shipping_fee=10.00,
            total_amount=690.38,
            placed_at=datetime.utcnow() - timedelta(days=10),
            shipped_at=datetime.utcnow() - timedelta(days=8),
            delivered_at=datetime.utcnow() - timedelta(days=5)
        )
        db.add(order)
        db.commit()
        
        # Add order items
        order_items = [
            OrderItem(
                order_id=order.order_id,
                product_id=products[1].product_id,
                quantity=1,
                unit_price=products[1].selling_price
            ),
            OrderItem(
                order_id=order.order_id,
                product_id=products[2].product_id,
                quantity=1,
                unit_price=products[2].selling_price
            ),
        ]
        db.add_all(order_items)
        db.commit()
        logger.info(f"Created sample order with {len(order_items)} items")
        
        # Create sample payment
        payment = Payment(
            order_id=order.order_id,
            payment_method="credit_card",
            payment_status=PaymentStatus.COMPLETED,
            transaction_reference="TXN-20260530-001",
            amount=690.38,
            paid_at=datetime.utcnow() - timedelta(days=10)
        )
        db.add(payment)
        db.commit()
        logger.info("Created sample payment")
        
        # Create sample inventory logs
        inventory_logs = [
            InventoryLog(
                product_id=products[0].product_id,
                change_type=InventoryChangeType.PURCHASE,
                quantity_changed=-1,
                reason="Order #" + str(order.order_id)
            ),
            InventoryLog(
                product_id=products[1].product_id,
                change_type=InventoryChangeType.RESTOCK,
                quantity_changed=50,
                reason="Restocking"
            ),
        ]
        db.add_all(inventory_logs)
        db.commit()
        logger.info(f"Created {len(inventory_logs)} sample inventory logs")
        
        logger.info("Sample data loaded successfully!")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error loading sample data: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    load_sample_data()
