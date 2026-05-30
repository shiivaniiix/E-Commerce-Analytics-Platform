# E-Commerce Analytics Platform - Setup Guide

## Quick Start

This guide will help you set up and run the entire application locally.

### Prerequisites
- Python 3.10+
- Node.js 16+
- PostgreSQL 12+

### Step 1: Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your PostgreSQL details

# Create database (use psql to run):
# CREATE USER ecommerce_user WITH PASSWORD 'ecommerce_password';
# CREATE DATABASE ecommerce_db OWNER ecommerce_user;

# Initialize tables
python init_db.py

# (Optional) Load sample data
python load_sample_data.py

# Run server
python main.py
```

Backend runs at: http://localhost:8000
API Docs: http://localhost:8000/docs

### Step 2: Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env

# Run development server
npm run dev
```

Frontend runs at: http://localhost:3000 or http://localhost:5173

## Project Structure

- **Frontend**: React + Vite + Tailwind CSS
  - Components, pages, services, utilities, hooks
  - Styled with Tailwind CSS
  - API communication via Axios

- **Backend**: FastAPI + SQLAlchemy
  - Modular API structure (v1 endpoints)
  - JWT authentication with bcrypt
  - Pydantic validation
  - PostgreSQL database
  - 10 comprehensive data models

## Database Models

The database includes 10 tables:

1. **Customer** - Customer accounts and information
2. **Address** - Customer shipping/billing addresses
3. **Category** - Product categories
4. **Product** - Product information and inventory
5. **Cart** - Shopping carts
6. **CartItem** - Items in shopping carts
7. **Order** - Customer orders
8. **OrderItem** - Items in orders
9. **Payment** - Payment transactions
10. **InventoryLog** - Inventory change tracking

For detailed schema documentation, see **DATABASE_SCHEMA.md**

## Available APIs

- `GET /api/health` - Health check
- `POST /api/auth/register` - Register user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user

See README.md for detailed API documentation.

## Database Initialization

### Initialize Empty Database

```bash
python init_db.py
```

This creates all tables based on SQLAlchemy models.

### Load Sample Data

```bash
python load_sample_data.py
```

This populates the database with sample customers, products, orders, etc.

### Drop Database (Caution!)

```bash
python init_db.py drop
```

This deletes all tables. You'll be prompted for confirmation.

## Troubleshooting

### PostgreSQL Connection Error
```
Error: could not connect to server
```
- Ensure PostgreSQL is running
- Check DATABASE_URL in .env
- Verify username and password

### Port Already in Use
```
Address already in use
```
- Backend (8000): `lsof -i :8000` (macOS/Linux) or `netstat -ano | findstr :8000` (Windows)
- Frontend (5173): `lsof -i :5173` (macOS/Linux) or `netstat -ano | findstr :5173` (Windows)

### Module Import Errors
```
ModuleNotFoundError: No module named 'app'
```
- Ensure you're running from the backend directory
- Virtual environment is activated
- All dependencies installed: `pip install -r requirements.txt`

## Next Steps

1. Explore the database models in `backend/app/models/__init__.py`
2. Review the comprehensive schema documentation in `DATABASE_SCHEMA.md`
3. Check sample data in `load_sample_data.py`
4. Start building API endpoints using the models
5. Connect frontend components to the API
