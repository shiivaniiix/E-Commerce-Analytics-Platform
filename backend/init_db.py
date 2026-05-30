"""
Database initialization script
Creates all tables and initializes the database
"""

import logging
from app.db.base import engine, Base
from app.core.config import get_settings

# Import all models to register them with Base
from app.models import (
    Customer, Address, Category, Product, Cart, CartItem,
    Order, OrderItem, Payment, InventoryLog
)

logger = logging.getLogger(__name__)
settings = get_settings()


def init_db():
    """Initialize the database by creating all tables"""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully!")


def drop_db():
    """Drop all tables (use with caution!)"""
    logger.warning("Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    logger.warning("All database tables dropped!")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "drop":
        response = input("Are you sure you want to drop all tables? (yes/no): ")
        if response.lower() == "yes":
            drop_db()
            print("Tables dropped!")
        else:
            print("Operation cancelled.")
    else:
        init_db()
        print("Database initialized successfully!")
