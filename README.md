# E-Commerce Analytics Platform

A full-stack e-commerce platform with AI-powered analytics, built with React + Vite (frontend) and FastAPI (backend).

## 📋 Table of Contents

- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Backend Setup](#backend-setup)
- [Frontend Setup](#frontend-setup)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Features](#features)
- [Environment Variables](#environment-variables)
- [Development](#development)

## 📁 Project Structure

```
E-Commerce Analytics Platform/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── common/          # Reusable UI components
│   │   │   ├── layout/          # Layout components (Header, Footer)
│   │   │   ├── products/        # Product-related components
│   │   │   ├── cart/            # Cart components
│   │   │   └── auth/            # Authentication components
│   │   ├── pages/               # Page components
│   │   ├── services/            # API services
│   │   ├── hooks/               # Custom React hooks
│   │   ├── context/             # React Context
│   │   ├── utils/               # Utility functions
│   │   ├── assets/              # Images, fonts, etc.
│   │   ├── App.jsx              # Root component
│   │   └── main.jsx             # Entry point
│   ├── public/                  # Static assets
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── index.html
│   └── .env.example
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── endpoints/   # API endpoints
│   │   │       └── router.py    # API router
│   │   ├── core/
│   │   │   ├── config.py        # Configuration management
│   │   │   └── security.py      # JWT & password hashing
│   │   ├── db/
│   │   │   └── base.py          # Database setup & session
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # Business logic
│   │   └── main.py              # FastAPI app initialization
│   ├── tests/                   # Unit tests
│   ├── main.py                  # Entry point
│   ├── requirements.txt
│   └── .env.example
│
└── README.md                    # This file
```

## 🔧 Prerequisites

### System Requirements
- Python 3.10+
- Node.js 16+ and npm
- PostgreSQL 12+

### Install PostgreSQL

**On Windows:**
- Download from [postgresql.org](https://www.postgresql.org/download/windows/)
- During installation, set a password for the `postgres` user
- PostgreSQL will run on port 5432 by default

**On macOS:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**On Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo service postgresql start
```

## 🚀 Backend Setup

### 1. Navigate to Backend Directory
```bash
cd backend
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```bash
# Copy example env file
cp .env.example .env

# Edit .env with your settings
# Make sure DATABASE_URL is correct for your PostgreSQL setup
```

### 5. Create Database
```bash
# Connect to PostgreSQL
psql -U postgres

# Run these SQL commands:
CREATE USER ecommerce_user WITH PASSWORD 'ecommerce_password';
CREATE DATABASE ecommerce_db OWNER ecommerce_user;
GRANT ALL PRIVILEGES ON DATABASE ecommerce_db TO ecommerce_user;
\q
```

### 6. Initialize Database Tables
```bash
# Create tables using SQLAlchemy
python -c "from app.db.base import engine, Base; from app.models import *; Base.metadata.create_all(bind=engine)"
```

### 7. Run Backend Server
```bash
python main.py
```

The backend will start at `http://localhost:8000`

**API Documentation:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🎨 Frontend Setup

### 1. Navigate to Frontend Directory
```bash
cd frontend
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Configure Environment Variables
```bash
# Copy example env file
cp .env.example .env

# Edit .env if needed (defaults should work for local development)
```

### 4. Run Development Server
```bash
npm run dev
```

The frontend will start at `http://localhost:3000` or `http://localhost:5173` (Vite's default)

### 5. Build for Production
```bash
npm run build
```

Output will be in the `dist` folder.

## 🗄️ Database Setup

### Models Overview

**User Table**
- Stores user account information
- Fields: id, email, first_name, last_name, hashed_password, is_active, timestamps

**Product Table**
- Stores product information
- Fields: id, name, description, price, quantity, category, is_active, timestamps

**Order Table**
- Stores order information
- Fields: id, user_id, total_amount, status, timestamps

### Connection Details

The project uses SQLAlchemy ORM with PostgreSQL. Connection string format:
```
postgresql://username:password@host:port/database
```

Default example:
```
postgresql://ecommerce_user:ecommerce_password@localhost:5432/ecommerce_db
```

## 🏃 Running the Application

### Development Mode (Both Frontend & Backend)

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Visit `http://localhost:3000` in your browser.

### Testing API Health
```bash
# Should return healthy status
curl http://localhost:8000/api/health
```

## 📚 API Documentation

### Base URL
```
http://localhost:8000/api
```

### Available Endpoints

#### Health Check
```
GET /health
```

#### Authentication
```
POST /auth/register
POST /auth/login
GET /auth/me
```

### Request/Response Examples

**Register:**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

**Login:**
```bash
curl -X POST "http://localhost:8000/api/auth/login?email=user@example.com&password=securepassword"
```

## ✨ Features

### Backend
- ✅ FastAPI framework with async support
- ✅ SQLAlchemy ORM for database operations
- ✅ JWT authentication with bcrypt password hashing
- ✅ CORS enabled for frontend integration
- ✅ Pydantic schemas for data validation
- ✅ Health check endpoint
- ✅ Production-ready error handling
- ✅ Environment-based configuration

### Frontend
- ✅ React 18 with Vite bundler
- ✅ Tailwind CSS for styling
- ✅ React Router for navigation
- ✅ Axios HTTP client with interceptors
- ✅ Authentication token management
- ✅ Responsive design
- ✅ Component-based architecture
- ✅ Error handling and loading states

## 🔐 Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://user:password@localhost/dbname
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=["http://localhost:3000"]
ENVIRONMENT=development
DEBUG=true
```

### Frontend (.env)
```
VITE_API_BASE_URL=http://localhost:8000/api
VITE_ENV=development
```

## 🛠️ Development

### Backend Development

**Code Style:**
```bash
# Format code with Black
black app/

# Lint code
flake8 app/

# Sort imports
isort app/
```

**Testing:**
```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app
```

### Frontend Development

**Code Quality:**
```bash
# Lint code
npm run lint

# Fix linting issues
npm run lint -- --fix
```

**Development Server Features:**
- Hot module replacement (HMR)
- Fast refresh on file changes
- Proxy to backend API

## 📦 Project Dependencies

### Backend
- **FastAPI** - Modern web framework
- **SQLAlchemy** - ORM for database
- **psycopg2** - PostgreSQL adapter
- **python-jose** - JWT handling
- **passlib** - Password hashing
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

### Frontend
- **React** - UI library
- **Vite** - Build tool
- **React Router** - Routing
- **Axios** - HTTP client
- **Tailwind CSS** - Styling
- **Zustand** - State management (optional)

## 🐛 Troubleshooting

### PostgreSQL Connection Error
- Ensure PostgreSQL is running: `psql -U postgres`
- Check DATABASE_URL in .env
- Verify credentials and database name

### Port Already in Use
- Backend (8000): `lsof -i :8000` or `netstat -ano | findstr :8000`
- Frontend (3000/5173): `lsof -i :3000` or `netstat -ano | findstr :3000`

### Module Not Found Errors
- Reinstall dependencies: `pip install -r requirements.txt` or `npm install`
- Ensure virtual environment is activated

### CORS Issues
- Check CORS_ORIGINS in backend .env
- Ensure frontend URL matches allowed origins

## 📝 Next Steps

1. Deploy models and migrations
2. Implement product endpoints
3. Add shopping cart functionality
4. Integrate payment processing
5. Add order management
6. Implement user dashboard
7. Add analytics features
8. Deploy to production

## 📄 License

This project is licensed under the MIT License.

## 👥 Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

For issues and questions, please open an issue in the repository.

---

**Happy coding!** 🎉
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
