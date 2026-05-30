# Database Schema Documentation

## Overview

This document provides comprehensive documentation for the E-Commerce Analytics Platform database schema. The database is built with SQLAlchemy ORM and PostgreSQL.

## Table of Contents

1. [Database Models](#database-models)
2. [Relationships](#relationships)
3. [Enums](#enums)
4. [Setup Instructions](#setup-instructions)
5. [Schema Diagram](#schema-diagram)
6. [Best Practices](#best-practices)

---

## Database Models

### 1. Customer

**Table Name:** `customers`

**Purpose:** Stores customer account information

**Fields:**

| Field | Type | Constraints | Description |
|-------|------|-----------|-------------|
| customer_id | INTEGER | PRIMARY KEY | Unique customer identifier |
| first_name | VARCHAR(100) | NOT NULL | Customer first name |
| last_name | VARCHAR(100) | NOT NULL | Customer last name |
| email | VARCHAR(255) | UNIQUE, NOT NULL | Unique email address |
| password_hash | VARCHAR(255) | NOT NULL | Bcrypt hashed password |
| phone_number | VARCHAR(20) | NULLABLE | Customer phone number |
| account_created_at | TIMESTAMP | NOT NULL | Account creation date |
| account_status | ENUM | NOT NULL | Active/Inactive/Suspended |

**Indexes:**
- `idx_customer_email` on email column
- `idx_customer_phone` on phone_number column

**Relationships:**
- One-to-Many: Customer → Addresses (cascade delete)
- One-to-Many: Customer → Carts (cascade delete)
- One-to-Many: Customer → Orders (cascade delete)

---

### 2. Address

**Table Name:** `addresses`

**Purpose:** Stores customer shipping and billing addresses

**Fields:**

| Field | Type | Constraints | Description |
|-------|------|-----------|-------------|
| address_id | INTEGER | PRIMARY KEY | Unique address identifier |
| customer_id | INTEGER | FOREIGN KEY | References customer |
| address_line1 | VARCHAR(255) | NOT NULL | Street address |
| address_line2 | VARCHAR(255) | NULLABLE | Additional address info |
| city | VARCHAR(100) | NOT NULL | City name |
| state | VARCHAR(100) | NOT NULL | State/Province |
| country | VARCHAR(100) | NOT NULL | Country name |
| pincode | VARCHAR(20) | NOT NULL | Postal code |
| is_default | BOOLEAN | NOT NULL | Default address flag |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Last update timestamp |

**Indexes:**
- `idx_address_customer` on customer_id column

**Relationships:**
- Many-to-One: Address → Customer
- One-to-Many: Address → Orders (cascade delete)

---

### 3. Category

**Table Name:** `categories`

**Purpose:** Stores product categories

**Fields:**

| Field | Type | Constraints | Description |
|-------|------|-----------|-------------|
| category_id | INTEGER | PRIMARY KEY | Unique category identifier |
| category_name | VARCHAR(150) | UNIQUE, NOT NULL | Category name |
| description | TEXT | NULLABLE | Category description |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |

**Relationships:**
- One-to-Many: Category → Products (cascade delete)

---

### 4. Product

**Table Name:** `products`

**Purpose:** Stores product information and inventory

**Fields:**

| Field | Type | Constraints | Description |
|-------|------|-----------|-------------|
| product_id | INTEGER | PRIMARY KEY | Unique product identifier |
| product_name | VARCHAR(255) | NOT NULL | Product name |
| category_id | INTEGER | FOREIGN KEY | References category |
| brand | VARCHAR(100) | NULLABLE | Product brand |
| description | TEXT | NULLABLE | Product description |
| selling_price | NUMERIC(10,2) | NOT NULL | Customer price |
| cost_price | NUMERIC(10,2) | NOT NULL | Wholesale/cost price |
| stock_quantity | INTEGER | NOT NULL | Available quantity |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Last update timestamp |
| is_active | BOOLEAN | NOT NULL | Active/Inactive flag |

**Indexes:**
- `idx_product_category` on category_id column
- `idx_product_is_active` on is_active column

**Relationships:**
- Many-to-One: Product → Category
- One-to-Many: Product → CartItems (cascade delete)
- One-to-Many: Product → OrderItems (cascade delete)
- One-to-Many: Product → InventoryLogs (cascade delete)

---

### 5. Cart

**Table Name:** `carts`

**Purpose:** Stores shopping cart information

**Fields:**

| Field | Type | Constraints | Description |
|-------|------|-----------|-------------|
| cart_id | INTEGER | PRIMARY KEY | Unique cart identifier |
| customer_id | INTEGER | FOREIGN KEY | References customer |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Last update timestamp |

**Indexes:**
- `idx_cart_customer` on customer_id column

**Relationships:**
- Many-to-One: Cart → Customer
- One-to-Many: Cart → CartItems (cascade delete)

---

### 6. CartItem

**Table Name:** `cart_items`

**Purpose:** Stores items in shopping carts

**Fields:**

| Field | Type | Constraints | Description |
|-------|------|-----------|-------------|
| cart_item_id | INTEGER | PRIMARY KEY | Unique cart item identifier |
| cart_id | INTEGER | FOREIGN KEY | References cart |
| product_id | INTEGER | FOREIGN KEY | References product |
| quantity | INTEGER | NOT NULL | Item quantity |
| added_at | TIMESTAMP | NOT NULL | When item was added |
| updated_at | TIMESTAMP | NOT NULL | Last update timestamp |

**Indexes:**
- `idx_cart_item_cart` on cart_id column
- `idx_cart_item_product` on product_id column

**Relationships:**
- Many-to-One: CartItem → Cart
- Many-to-One: CartItem → Product

---

### 7. Order

**Table Name:** `orders`

**Purpose:** Stores customer orders and order details

**Fields:**

| Field | Type | Constraints | Description |
|-------|------|-----------|-------------|
| order_id | INTEGER | PRIMARY KEY | Unique order identifier |
| customer_id | INTEGER | FOREIGN KEY | References customer |
| address_id | INTEGER | FOREIGN KEY | References address |
| payment_method | VARCHAR(50) | NOT NULL | Payment type |
| payment_status | ENUM | NOT NULL | Payment status |
| order_status | ENUM | NOT NULL | Order status |
| subtotal | NUMERIC(12,2) | NOT NULL | Order subtotal |
| tax_amount | NUMERIC(12,2) | NOT NULL | Tax amount |
| discount_amount | NUMERIC(12,2) | NOT NULL | Discount amount |
| shipping_fee | NUMERIC(12,2) | NOT NULL | Shipping cost |
| total_amount | NUMERIC(12,2) | NOT NULL | Total order amount |
| placed_at | TIMESTAMP | NOT NULL | Order placement date |
| shipped_at | TIMESTAMP | NULLABLE | Shipping date |
| delivered_at | TIMESTAMP | NULLABLE | Delivery date |
| cancelled_at | TIMESTAMP | NULLABLE | Cancellation date |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Last update timestamp |

**Indexes:**
- `idx_order_customer` on customer_id column
- `idx_order_address` on address_id column
- `idx_order_status` on order_status column
- `idx_order_placed_at` on placed_at column

**Relationships:**
- Many-to-One: Order → Customer
- Many-to-One: Order → Address
- One-to-Many: Order → OrderItems (cascade delete)
- One-to-Many: Order → Payments (cascade delete)

---

### 8. OrderItem

**Table Name:** `order_items`

**Purpose:** Stores individual items in an order

**Fields:**

| Field | Type | Constraints | Description |
|-------|------|-----------|-------------|
| order_item_id | INTEGER | PRIMARY KEY | Unique order item identifier |
| order_id | INTEGER | FOREIGN KEY | References order |
| product_id | INTEGER | FOREIGN KEY | References product |
| quantity | INTEGER | NOT NULL | Item quantity |
| unit_price | NUMERIC(10,2) | NOT NULL | Price at time of purchase |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |

**Indexes:**
- `idx_order_item_order` on order_id column
- `idx_order_item_product` on product_id column

**Relationships:**
- Many-to-One: OrderItem → Order
- Many-to-One: OrderItem → Product

---

### 9. Payment

**Table Name:** `payments`

**Purpose:** Stores payment transaction information

**Fields:**

| Field | Type | Constraints | Description |
|-------|------|-----------|-------------|
| payment_id | INTEGER | PRIMARY KEY | Unique payment identifier |
| order_id | INTEGER | FOREIGN KEY | References order |
| payment_method | VARCHAR(50) | NOT NULL | Payment method |
| payment_status | ENUM | NOT NULL | Payment status |
| transaction_reference | VARCHAR(255) | NULLABLE | Payment gateway reference |
| amount | NUMERIC(12,2) | NOT NULL | Payment amount |
| paid_at | TIMESTAMP | NULLABLE | Payment completion date |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Last update timestamp |

**Indexes:**
- `idx_payment_order` on order_id column
- `idx_payment_status` on payment_status column

**Relationships:**
- Many-to-One: Payment → Order

---

### 10. InventoryLog

**Table Name:** `inventory_logs`

**Purpose:** Tracks all inventory changes for auditing

**Fields:**

| Field | Type | Constraints | Description |
|-------|------|-----------|-------------|
| inventory_log_id | INTEGER | PRIMARY KEY | Unique log identifier |
| product_id | INTEGER | FOREIGN KEY | References product |
| change_type | ENUM | NOT NULL | Type of change |
| quantity_changed | INTEGER | NOT NULL | Quantity increase/decrease |
| reason | VARCHAR(255) | NULLABLE | Reason for change |
| changed_at | TIMESTAMP | NOT NULL | Change timestamp |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |

**Indexes:**
- `idx_inventory_log_product` on product_id column
- `idx_inventory_log_changed_at` on changed_at column

**Relationships:**
- Many-to-One: InventoryLog → Product

---

## Relationships

### Relationship Diagram

```
Customer
  ├─→ Address (1:N)
  ├─→ Cart (1:N)
  └─→ Order (1:N)
       ├─→ OrderItem (1:N)
       │    └─→ Product
       ├─→ Payment (1:N)
       └─→ Address
           └─→ Customer

Product
  ├─→ Category (N:1)
  ├─→ CartItem (1:N)
  ├─→ OrderItem (1:N)
  └─→ InventoryLog (1:N)

Cart
  ├─→ Customer (N:1)
  └─→ CartItem (1:N)
       └─→ Product
```

### Cascade Delete Behavior

- **Customer** → deletes all related Addresses, Carts, and Orders
- **Address** → deletes all related Orders
- **Category** → deletes all related Products
- **Product** → deletes all related CartItems, OrderItems, and InventoryLogs
- **Cart** → deletes all related CartItems
- **Order** → deletes all related OrderItems and Payments

### Restrict Delete References

- **Customer** is referenced by Orders (RESTRICT)
- **Address** is referenced by Orders (RESTRICT)
- **Product** is referenced by OrderItems (RESTRICT)
- **Order** is required for Payments

---

## Enums

### AccountStatus
- `active` - Active account
- `inactive` - Inactive account
- `suspended` - Suspended account

### OrderStatus
- `pending` - Order placed, awaiting confirmation
- `confirmed` - Order confirmed
- `shipped` - Order shipped
- `delivered` - Order delivered
- `cancelled` - Order cancelled
- `returned` - Order returned

### PaymentStatus
- `pending` - Payment pending
- `completed` - Payment successful
- `failed` - Payment failed
- `refunded` - Payment refunded

### InventoryChangeType
- `purchase` - Sold/purchased
- `return` - Customer return
- `restock` - Restocking
- `damaged` - Damaged items
- `adjustment` - Manual adjustment

---

## Setup Instructions

### 1. Initialize Database

```bash
# From the backend directory
python init_db.py
```

### 2. Load Sample Data

```bash
python load_sample_data.py
```

### 3. Drop Database (WARNING: Destructive)

```bash
python init_db.py drop
```

---

## Schema Diagram

### Table Structure

```sql
-- Customers table with account management
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20),
    account_created_at TIMESTAMP DEFAULT NOW(),
    account_status VARCHAR(20) DEFAULT 'active'
);

-- Addresses for customers
CREATE TABLE addresses (
    address_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    address_line1 VARCHAR(255) NOT NULL,
    address_line2 VARCHAR(255),
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    pincode VARCHAR(20) NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Product categories
CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(150) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Products
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    category_id INTEGER NOT NULL REFERENCES categories(category_id) ON DELETE RESTRICT,
    brand VARCHAR(100),
    description TEXT,
    selling_price NUMERIC(10, 2) NOT NULL,
    cost_price NUMERIC(10, 2) NOT NULL,
    stock_quantity INTEGER DEFAULT 0 NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Shopping carts
CREATE TABLE carts (
    cart_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Cart items
CREATE TABLE cart_items (
    cart_item_id SERIAL PRIMARY KEY,
    cart_id INTEGER NOT NULL REFERENCES carts(cart_id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL DEFAULT 1,
    added_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Orders
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    address_id INTEGER NOT NULL REFERENCES addresses(address_id),
    payment_method VARCHAR(50) NOT NULL,
    payment_status VARCHAR(20),
    order_status VARCHAR(20),
    subtotal NUMERIC(12, 2) NOT NULL,
    tax_amount NUMERIC(12, 2) DEFAULT 0,
    discount_amount NUMERIC(12, 2) DEFAULT 0,
    shipping_fee NUMERIC(12, 2) DEFAULT 0,
    total_amount NUMERIC(12, 2) NOT NULL,
    placed_at TIMESTAMP DEFAULT NOW(),
    shipped_at TIMESTAMP,
    delivered_at TIMESTAMP,
    cancelled_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Order items
CREATE TABLE order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(product_id),
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Payments
CREATE TABLE payments (
    payment_id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    payment_method VARCHAR(50) NOT NULL,
    payment_status VARCHAR(20),
    transaction_reference VARCHAR(255),
    amount NUMERIC(12, 2) NOT NULL,
    paid_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Inventory logs
CREATE TABLE inventory_logs (
    inventory_log_id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    change_type VARCHAR(20) NOT NULL,
    quantity_changed INTEGER NOT NULL,
    reason VARCHAR(255),
    changed_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## Best Practices

### 1. Querying

Use relationships to fetch related data:

```python
# Efficient: Uses relationship loading
customer = db.query(Customer).filter(Customer.customer_id == 1).first()
print(customer.orders)  # Lazy loaded

# Better: Eager loading with joinedload
from sqlalchemy.orm import joinedload
customer = db.query(Customer).options(
    joinedload(Customer.orders),
    joinedload(Customer.addresses)
).filter(Customer.customer_id == 1).first()
```

### 2. Creating Records

```python
# Create a customer with address
customer = Customer(
    first_name="John",
    last_name="Doe",
    email="john@example.com",
    password_hash=hash_password("password"),
    phone_number="+1-555-0101"
)
db.add(customer)
db.commit()

# Add address
address = Address(
    customer_id=customer.customer_id,
    address_line1="123 Main St",
    city="New York",
    state="NY",
    country="USA",
    pincode="10001"
)
db.add(address)
db.commit()
```

### 3. Updating Records

```python
customer = db.query(Customer).filter(Customer.customer_id == 1).first()
customer.phone_number = "+1-555-9999"
customer.account_status = AccountStatus.ACTIVE
db.commit()
```

### 4. Deleting Records

```python
# Cascade delete - removes all dependent records
customer = db.query(Customer).filter(Customer.customer_id == 1).first()
db.delete(customer)
db.commit()
```

### 5. Queries with Filters

```python
# Find all active products in a category
products = db.query(Product).filter(
    Product.category_id == 1,
    Product.is_active == True
).all()

# Find completed orders for a customer
orders = db.query(Order).filter(
    Order.customer_id == 1,
    Order.order_status == OrderStatus.DELIVERED
).all()
```

---

## Performance Considerations

1. **Indexes** are created for frequently queried columns
2. **Foreign Keys** are used for referential integrity
3. **Cascading deletes** maintain data consistency
4. **Timestamps** track record creation and updates
5. **Enums** provide type safety for status fields

---

## Migration Strategy

For schema changes:

1. Create migration file
2. Use Alembic for version control
3. Test in development
4. Deploy to production

Example:
```bash
# Generate migration
alembic revision --autogenerate -m "Add new columns"

# Apply migration
alembic upgrade head
```

---

**Last Updated:** 2026-05-30
**Version:** 1.0
