# E-Commerce Analytics Platform – End-to-End Data Engineering Project

# 1. Project Overview

## Introduction

This project is a complete end-to-end E-Commerce platform integrated with a modern Data Engineering and Analytics pipeline.

The application allows customers to:

* Sign up / Login
* Browse products
* Add items to cart
* Manage addresses
* Place orders
* Select payment methods
* Track order history

The project also includes a modern cloud-based analytics architecture where operational data is processed into a Data Warehouse for business reporting and analytics.

The main objective of this project is to simulate how real-world E-Commerce companies design:

* Transactional systems
* Data pipelines
* Cloud storage
* Data warehousing
* Analytics dashboards

---

# 2. Project Objectives

The goals of this project are:

* Build a scalable E-Commerce application
* Implement proper relational database design
* Create cloud-based data pipelines
* Store and process historical business data
* Perform analytics using Snowflake + dbt + Power BI
* Simulate real-world production architecture

---

# 3. Tech Stack

## Frontend

* React.js
* Tailwind CSS
* Axios

## Backend

* FastAPI / Node.js (Express)
* REST APIs
* JWT Authentication

## Operational Database

* PostgreSQL

## Cloud & Storage

* AWS S3

## Data Warehouse

* Snowflake

## Data Transformation

* dbt (Data Build Tool)

## Analytics & Reporting

* Power BI

## CI/CD & Automation

* GitHub Actions

---

# 4. High-Level Architecture

```text
User
  ↓
React Frontend
  ↓
Backend APIs
  ↓
PostgreSQL Database
  ↓
Data Export / CDC Pipeline
  ↓
AWS S3 Data Lake
  ↓
Snowflake Warehouse
  ↓
dbt Transformations
  ↓
Power BI Dashboards
```

---

# 5. System Flow

## User Authentication Flow

```text
User Signup/Login
        ↓
Backend validates credentials
        ↓
Password stored as HASH
        ↓
JWT Token generated
        ↓
User session authenticated
```

---

## Product Purchase Flow

```text
User views products
        ↓
Adds products to cart
        ↓
Selects address
        ↓
Chooses payment method
        ↓
Order created
        ↓
Inventory updated
        ↓
Order items inserted
        ↓
Analytics pipeline triggered
```

---

## Data Engineering Flow

```text
PostgreSQL
     ↓
Batch Export / CDC
     ↓
AWS S3
     ↓
Snowflake COPY INTO
     ↓
dbt Models
     ↓
Power BI Dashboards
```

---

# 6. Database Design

# 6.1 CUSTOMER Table

Stores customer account information.

| Column Name        | Data Type | Description                |
| ------------------ | --------- | -------------------------- |
| customer_id        | INT       | Primary Key                |
| first_name         | VARCHAR   | Customer first name        |
| last_name          | VARCHAR   | Customer last name         |
| email              | VARCHAR   | Unique email               |
| password_hash      | VARCHAR   | Encrypted password         |
| phone_number       | VARCHAR   | Contact number             |
| account_created_at | TIMESTAMP | Account creation timestamp |
| account_status     | VARCHAR   | Active/Inactive            |

---

# 6.2 ADDRESS Table

One customer can have multiple addresses.

| Column Name   | Data Type |
| ------------- | --------- |
| address_id    | INT       |
| customer_id   | INT       |
| address_line1 | VARCHAR   |
| city          | VARCHAR   |
| state         | VARCHAR   |
| country       | VARCHAR   |
| pincode       | VARCHAR   |
| is_default    | BOOLEAN   |

---

# 6.3 CATEGORY Table

Stores product categories.

| Column Name   | Data Type |
| ------------- | --------- |
| category_id   | INT       |
| category_name | VARCHAR   |

---

# 6.4 PRODUCT Table

Stores product master data.

| Column Name    | Data Type |
| -------------- | --------- |
| product_id     | INT       |
| product_name   | VARCHAR   |
| category_id    | INT       |
| brand          | VARCHAR   |
| selling_price  | DECIMAL   |
| cost_price     | DECIMAL   |
| stock_quantity | INT       |
| created_at     | TIMESTAMP |
| is_active      | BOOLEAN   |

---

# 6.5 CART Table

Stores cart information.

| Column Name | Data Type |
| ----------- | --------- |
| cart_id     | INT       |
| customer_id | INT       |
| created_at  | TIMESTAMP |

---

# 6.6 CART_ITEMS Table

Stores products added into cart.

| Column Name  | Data Type |
| ------------ | --------- |
| cart_item_id | INT       |
| cart_id      | INT       |
| product_id   | INT       |
| quantity     | INT       |

---

# 6.7 ORDERS Table

Stores order-level information.

| Column Name     | Data Type |
| --------------- | --------- |
| order_id        | INT       |
| customer_id     | INT       |
| address_id      | INT       |
| payment_method  | VARCHAR   |
| payment_status  | VARCHAR   |
| order_status    | VARCHAR   |
| subtotal        | DECIMAL   |
| tax_amount      | DECIMAL   |
| discount_amount | DECIMAL   |
| shipping_fee    | DECIMAL   |
| total_amount    | DECIMAL   |
| placed_at       | TIMESTAMP |
| shipped_at      | TIMESTAMP |
| delivered_at    | TIMESTAMP |
| cancelled_at    | TIMESTAMP |

---

# 6.8 ORDER_ITEMS Table

Stores products inside each order.

| Column Name   | Data Type |
| ------------- | --------- |
| order_item_id | INT       |
| order_id      | INT       |
| product_id    | INT       |
| quantity      | INT       |
| unit_price    | DECIMAL   |

---

# 6.9 PAYMENT Table

Stores payment details.

| Column Name           | Data Type |
| --------------------- | --------- |
| payment_id            | INT       |
| order_id              | INT       |
| payment_method        | VARCHAR   |
| payment_status        | VARCHAR   |
| transaction_reference | VARCHAR   |
| paid_at               | TIMESTAMP |

---

# 6.10 INVENTORY_LOG Table

Tracks inventory changes.

| Column Name      | Data Type |
| ---------------- | --------- |
| inventory_log_id | INT       |
| product_id       | INT       |
| change_type      | VARCHAR   |
| quantity_changed | INT       |
| changed_at       | TIMESTAMP |

Examples of change_type:

* ORDER_PLACED
* RESTOCK
* RETURN
* CANCELLATION

---

# 7. Relationships Between Tables

```text
CUSTOMER
   ↓
ADDRESS

CUSTOMER
   ↓
CART
   ↓
CART_ITEMS
   ↓
PRODUCT

CUSTOMER
   ↓
ORDERS
   ↓
ORDER_ITEMS
   ↓
PRODUCT

ORDERS
   ↓
PAYMENT
```

---

# 8. Authentication & Security

## Password Security

Passwords will never be stored directly.

Instead:

* Passwords will be encrypted using bcrypt hashing.
* JWT tokens will be used for authentication.

---

# 9. Inventory Management Logic

## Example Scenario

Suppose:

* Product stock = 50
* Customer orders quantity = 2

System logic:

```sql
UPDATE product
SET stock_quantity = stock_quantity - 2
WHERE product_id = 101;
```

Inventory logs will also be created for audit tracking.

---

# 10. Data Pipeline Design

## Why PostgreSQL First?

PostgreSQL acts as the operational transactional database.

It handles:

* User logins
* Product browsing
* Real-time updates
* Order placement

Snowflake is NOT used for live transactions.

---

## Data Export Strategy

### Batch Pipeline (Project Version)

Data from PostgreSQL will be periodically exported:

* CSV
* JSON
* Parquet

Then uploaded into AWS S3.

---

## Future Scalable Architecture

In production systems:

* CDC (Change Data Capture)
* Kafka
* Debezium
* Airbyte

can be used for near real-time streaming.

---

# 11. Snowflake Layer

Snowflake acts as the centralized Data Warehouse.

Responsibilities:

* Store historical business data
* Analytical querying
* Aggregations
* Reporting

---

# 12. dbt Layer

dbt will transform raw data into analytics-ready models.

## Example Models

### Staging Models

* stg_customers
* stg_orders
* stg_products

### Intermediate Models

* int_order_summary
* int_customer_metrics

### Mart Models

* fct_sales
* dim_customers
* dim_products

---

# 13. Power BI Dashboards

The following dashboards can be created:

## Sales Dashboard

* Daily sales
* Monthly revenue
* Top-selling products

## Customer Dashboard

* Repeat customers
* Customer lifetime value
* Customer growth

## Inventory Dashboard

* Low stock alerts
* Inventory trends

## Profitability Dashboard

* Gross profit
* Profit by category
* Profit margin %

---

# 14. CI/CD Pipeline

GitHub Actions will automate:

* Code deployment
* Data export jobs
* S3 uploads
* Snowflake loading jobs

---

# 15. Future Enhancements

Possible future improvements:

* Real payment gateway integration
* Product recommendation engine
* Real-time Kafka streaming
* Airflow orchestration
* Docker containerization
* Kubernetes deployment
* Email/SMS notifications
* Refund management
* Supplier management
* Return order handling

---

# 16. Real-World Concepts Implemented

This project demonstrates:

* Relational Database Design
* OLTP vs OLAP Architecture
* Cloud Data Engineering
* Data Warehousing
* ETL/ELT Pipelines
* Data Modeling
* Analytics Engineering
* Inventory Management
* Authentication & Security
* Dashboarding & BI

---

# 17. Conclusion

This project simulates a real-world E-Commerce ecosystem with both operational and analytical layers.

The architecture follows modern industry practices by separating:

* transactional systems
* analytical systems

The project is highly suitable for:

* Data Engineering portfolios
* Analytics Engineering portfolios
* Full Stack projects
* Cloud/Data Warehouse demonstrations
* Interview discussions
