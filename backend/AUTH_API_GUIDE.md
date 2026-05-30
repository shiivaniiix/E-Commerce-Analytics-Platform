# Authentication API Documentation

## Overview

Complete authentication system for the E-Commerce Analytics Platform using FastAPI, JWT, and bcrypt.

---

## Table of Contents

1. [Features](#features)
2. [Architecture](#architecture)
3. [Endpoints](#endpoints)
4. [Authentication Flow](#authentication-flow)
5. [Examples](#examples)
6. [Error Handling](#error-handling)
7. [Security Best Practices](#security-best-practices)

---

## Features

✅ **User Registration** - Email validation, password strength, duplicate checking  
✅ **User Login** - Credential verification with JWT token generation  
✅ **JWT Tokens** - Secure token-based authentication  
✅ **Bcrypt Hashing** - Industry-standard password hashing with salt  
✅ **Password Management** - Change password functionality  
✅ **Email Validation** - Check email availability before signup  
✅ **Account Deactivation** - Soft delete accounts  
✅ **Token Validation** - Verify token validity  
✅ **CORS Support** - Cross-origin requests allowed  

---

## Architecture

### Components

```
┌─────────────────────────────────────────┐
│         Client Application              │
│         (Web/Mobile)                    │
└────────────────┬────────────────────────┘
                 │
         HTTP Request/Response
                 │
┌─────────────────▼────────────────────────┐
│      FastAPI Application                │
│                                         │
│  ┌───────────────────────────────────┐  │
│  │  API Endpoints                    │  │
│  │  - POST /signup                   │  │
│  │  - POST /login                    │  │
│  │  - GET /me                        │  │
│  │  - POST /change-password          │  │
│  └───────────────────────────────────┘  │
│                 │                       │
│  ┌──────────────▼────────────────────┐  │
│  │  Authentication Service           │  │
│  │  - register_user()                │  │
│  │  - authenticate_user()            │  │
│  │  - change_password()              │  │
│  │  - validate_token()               │  │
│  └──────────────┬────────────────────┘  │
│                 │                       │
│  ┌──────────────▼────────────────────┐  │
│  │  Security Module                  │  │
│  │  - hash_password()                │  │
│  │  - verify_password()              │  │
│  │  - create_access_token()          │  │
│  │  - decode_token()                 │  │
│  └──────────────┬────────────────────┘  │
│                 │                       │
└─────────────────┼────────────────────────┘
                  │
         Database Queries
                  │
┌─────────────────▼────────────────────────┐
│      PostgreSQL Database                 │
│      (customers table)                   │
└──────────────────────────────────────────┘
```

### Technologies

- **FastAPI**: Modern Python web framework
- **Pydantic**: Data validation and serialization
- **SQLAlchemy**: Database ORM
- **Python-Jose**: JWT library with crypto
- **Passlib**: Password hashing library
- **Bcrypt**: Cryptographic hashing

---

## Endpoints

### 1. User Signup

**POST** `/api/auth/signup`

Register a new user account

#### Request Body

```json
{
  "email": "john@example.com",
  "password": "SecurePass123",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+1-555-0101"
}
```

#### Response (201 Created)

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "customer": {
    "customer_id": 1,
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+1-555-0101",
    "account_created_at": "2026-05-30T12:00:00",
    "account_status": "active"
  }
}
```

#### Error Responses

**400 Bad Request** - Email already registered
```json
{
  "detail": "Email already registered. Please use a different email or login."
}
```

**422 Unprocessable Entity** - Invalid data
```json
{
  "detail": [
    {
      "loc": ["body", "password"],
      "msg": "Password must contain at least one uppercase letter",
      "type": "value_error"
    }
  ]
}
```

---

### 2. User Login

**POST** `/api/auth/login`

Authenticate user and receive access token

#### Request Body

```json
{
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

#### Response (200 OK)

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "customer": {
    "customer_id": 1,
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "account_status": "active",
    "account_created_at": "2026-05-30T12:00:00"
  }
}
```

#### Error Responses

**401 Unauthorized** - Invalid credentials
```json
{
  "detail": "Invalid email or password"
}
```

**403 Forbidden** - Account inactive
```json
{
  "detail": "Account is inactive. Please contact support."
}
```

---

### 3. Get Current User

**GET** `/api/auth/me`

Get authenticated user's information

#### Headers

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Response (200 OK)

```json
{
  "customer_id": 1,
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+1-555-0101",
  "account_created_at": "2026-05-30T12:00:00",
  "account_status": "active"
}
```

#### Error Response

**401 Unauthorized** - Invalid or missing token
```json
{
  "detail": "Invalid authentication credentials"
}
```

---

### 4. Change Password

**POST** `/api/auth/change-password`

Change user password (requires authentication)

#### Headers

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Request Body

```json
{
  "current_password": "SecurePass123",
  "new_password": "NewSecurePass456",
  "confirm_password": "NewSecurePass456"
}
```

#### Response (200 OK)

```json
{
  "message": "Password changed successfully",
  "status": "success"
}
```

#### Error Responses

**401 Unauthorized** - Incorrect current password
```json
{
  "detail": "Current password is incorrect"
}
```

**422 Unprocessable Entity** - Passwords don't match
```json
{
  "detail": [
    {
      "loc": ["body", "confirm_password"],
      "msg": "Passwords do not match",
      "type": "value_error"
    }
  ]
}
```

---

### 5. Check Email Availability

**POST** `/api/auth/check-email`

Check if email is available for registration

#### Request Body

```json
{
  "email": "newuser@example.com"
}
```

#### Response (200 OK)

```json
{
  "email": "newuser@example.com",
  "available": true
}
```

---

### 6. Deactivate Account

**POST** `/api/auth/deactivate`

Deactivate user account (requires authentication)

#### Headers

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Response (200 OK)

```json
{
  "message": "Account deactivated successfully",
  "status": "success"
}
```

---

### 7. Validate Token

**GET** `/api/auth/validate-token`

Check if JWT token is valid (requires authentication)

#### Headers

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Response (200 OK)

```json
{
  "access_token": "token_valid",
  "token_type": "bearer",
  "expires_in": 86400
}
```

---

## Authentication Flow

### Registration Flow

```
1. User submits signup form
   ↓
2. CLIENT validates input (email format, password strength)
   ↓
3. CLIENT sends POST /api/auth/signup with credentials
   ↓
4. SERVER validates data again (Pydantic)
   ↓
5. SERVER checks if email exists in database
   ↓
6. SERVER hashes password using bcrypt (12 rounds)
   ↓
7. SERVER creates new Customer record
   ↓
8. SERVER generates JWT token
   ↓
9. SERVER returns token + user info
   ↓
10. CLIENT stores token in localStorage/sessionStorage
    ↓
11. CLIENT redirects to dashboard
```

### Login Flow

```
1. User submits login form
   ↓
2. CLIENT sends POST /api/auth/login with credentials
   ↓
3. SERVER finds user by email
   ↓
4. SERVER verifies password using bcrypt.verify()
   ↓
5. SERVER checks account status (active/inactive/suspended)
   ↓
6. SERVER generates JWT token with user info
   ↓
7. SERVER returns token + user info
   ↓
8. CLIENT stores token (localStorage, cookie, etc)
   ↓
9. CLIENT sets Authorization header for subsequent requests
```

### API Request Flow (Protected Endpoint)

```
1. CLIENT makes GET /api/auth/me
   ↓
2. CLIENT includes: Authorization: Bearer <token>
   ↓
3. SERVER middleware extracts token from header
   ↓
4. SERVER validates token signature using SECRET_KEY
   ↓
5. SERVER checks token expiration
   ↓
6. SERVER extracts user_id from token payload
   ↓
7. SERVER looks up user in database
   ↓
8. SERVER checks user account status
   ↓
9. SERVER returns user info (if all checks pass)
   ↓
10. CLIENT receives response
```

---

## Examples

### Python Client Example

```python
import requests
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

# 1. Signup
signup_response = requests.post(
    f"{BASE_URL}/auth/signup",
    json={
        "email": "john@example.com",
        "password": "SecurePass123",
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": "+1-555-0101"
    }
)

if signup_response.status_code == 201:
    data = signup_response.json()
    token = data["access_token"]
    print(f"✓ Signup successful")
    print(f"Token: {token}")
else:
    print(f"✗ Signup failed: {signup_response.json()}")

# 2. Login
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": "john@example.com",
        "password": "SecurePass123"
    }
)

if login_response.status_code == 200:
    data = login_response.json()
    token = data["access_token"]
    print(f"✓ Login successful")
else:
    print(f"✗ Login failed: {login_response.json()}")

# 3. Get Current User
headers = {"Authorization": f"Bearer {token}"}
me_response = requests.get(
    f"{BASE_URL}/auth/me",
    headers=headers
)

if me_response.status_code == 200:
    user = me_response.json()
    print(f"✓ User: {user['first_name']} {user['last_name']}")
else:
    print(f"✗ Failed: {me_response.json()}")

# 4. Check Email
check_response = requests.post(
    f"{BASE_URL}/auth/check-email",
    json={"email": "newuser@example.com"}
)

if check_response.status_code == 200:
    result = check_response.json()
    print(f"Email available: {result['available']}")
```

### JavaScript/Frontend Example

```javascript
// Configuration
const API_BASE_URL = "http://localhost:8000/api";

// 1. Signup Function
async function signup(email, password, firstName, lastName) {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email,
        password,
        first_name: firstName,
        last_name: lastName
      })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail);
    }

    const data = await response.json();
    
    // Store token
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("user", JSON.stringify(data.customer));
    
    return data;
  } catch (error) {
    console.error("Signup failed:", error.message);
    throw error;
  }
}

// 2. Login Function
async function login(email, password) {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail);
    }

    const data = await response.json();
    
    // Store token
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("user", JSON.stringify(data.customer));
    
    return data;
  } catch (error) {
    console.error("Login failed:", error.message);
    throw error;
  }
}

// 3. Get Current User
async function getCurrentUser() {
  try {
    const token = localStorage.getItem("access_token");
    
    if (!token) {
      throw new Error("No authentication token found");
    }

    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      }
    });

    if (!response.ok) {
      if (response.status === 401) {
        // Token expired or invalid
        localStorage.removeItem("access_token");
        localStorage.removeItem("user");
        throw new Error("Session expired. Please login again.");
      }
      throw new Error("Failed to fetch user");
    }

    return await response.json();
  } catch (error) {
    console.error("Get user failed:", error.message);
    throw error;
  }
}

// 4. Logout Function
function logout() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("user");
  window.location.href = "/login";
}

// 5. Axios Interceptor (for automatic Authorization header)
import axios from "axios";

const apiClient = axios.create({
  baseURL: API_BASE_URL
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export { apiClient };
```

### cURL Examples

```bash
# 1. Signup
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+1-555-0101"
  }'

# 2. Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123"
  }'

# 3. Get Current User (replace TOKEN with actual token)
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# 4. Change Password
curl -X POST http://localhost:8000/api/auth/change-password \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "SecurePass123",
    "new_password": "NewPassword456",
    "confirm_password": "NewPassword456"
  }'

# 5. Check Email Availability
curl -X POST http://localhost:8000/api/auth/check-email \
  -H "Content-Type: application/json" \
  -d '{"email": "newuser@example.com"}'

# 6. Validate Token
curl -X GET http://localhost:8000/api/auth/validate-token \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Login successful |
| 201 | Created | User signup created |
| 400 | Bad Request | Email already exists |
| 401 | Unauthorized | Invalid credentials |
| 403 | Forbidden | Account inactive |
| 404 | Not Found | User not found |
| 422 | Unprocessable Entity | Validation error |
| 500 | Server Error | Database error |

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Validation Errors

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "invalid email format",
      "type": "value_error.email"
    }
  ]
}
```

---

## Security Best Practices

### Password Requirements
- Minimum 8 characters
- At least one uppercase letter
- At least one digit
- No common passwords

### JWT Tokens
- Expires in 24 hours
- Contains user_id and email
- Signed with SECRET_KEY
- Validated on each protected request

### Bcrypt Hashing
- 12 rounds (high security)
- Random salt per password
- Slow hashing (prevents brute force)
- One-way function (irreversible)

### Database Security
- Passwords stored as hashes only
- No plain text passwords
- Email unique constraint
- Account status tracking

### API Security
- CORS enabled for specified origins
- HTTPS required in production
- Rate limiting recommended
- Token validation on each request

### Authorization Headers
```
Authorization: Bearer <token>
```

### Token Storage (Frontend)
- **Avoid**: localStorage, sessionStorage for sensitive tokens
- **Prefer**: HTTP-only cookies (automatic with each request)
- **Alternative**: In-memory storage with token refresh

---

## Configuration

### Environment Variables (.env)

```
# JWT Settings
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 hours

# Database
DATABASE_URL=postgresql://user:password@localhost/dbname

# API
API_TITLE=E-Commerce Analytics Platform API
API_VERSION=0.1.0

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
```

---

## Testing

### Run Tests

```bash
pytest tests/auth/

# With coverage
pytest tests/auth/ --cov=app
```

### Example Test Cases

```python
def test_signup_success(client, db):
    response = client.post("/api/auth/signup", json={
        "email": "test@example.com",
        "password": "TestPass123",
        "first_name": "Test",
        "last_name": "User"
    })
    assert response.status_code == 201
    assert "access_token" in response.json()

def test_signup_duplicate_email(client, db):
    # First signup
    client.post("/api/auth/signup", json={...})
    # Second signup with same email
    response = client.post("/api/auth/signup", json={...})
    assert response.status_code == 400

def test_login_invalid_credentials(client, db):
    response = client.post("/api/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "WrongPass"
    })
    assert response.status_code == 401
```

---

## Troubleshooting

### Token Expires Immediately
- Check SECRET_KEY is consistent
- Verify system time is correct
- Check ACCESS_TOKEN_EXPIRE_MINUTES setting

### Password Verification Fails
- Ensure password uses bcrypt hash
- Check password_hash column type (VARCHAR)

### CORS Errors
- Verify frontend URL in CORS_ORIGINS
- Check Access-Control-Allow-Origin header

### Database Connection Fails
- Verify DATABASE_URL format
- Check PostgreSQL is running
- Verify credentials are correct

---

**Version**: 1.0  
**Updated**: 2026-05-30  
**Status**: Production Ready
