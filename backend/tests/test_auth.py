"""
Authentication API Test Suite
Tests for all authentication endpoints and service layer
"""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.models import Customer, AccountStatus
from app.services.auth_service import AuthService
from app.core.security import hash_password, verify_password, create_access_token, decode_token
from app.schemas import SignupRequest, LoginRequest, ChangePasswordRequest


@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def db_session(db: Session):
    """Database session for tests"""
    yield db
    db.rollback()


@pytest.fixture
def auth_service(db_session):
    """AuthService instance for testing"""
    return AuthService(db_session)


@pytest.fixture
def test_user_data():
    """Standard test user data"""
    return {
        "email": "testuser@example.com",
        "password": "TestPass123",
        "first_name": "Test",
        "last_name": "User",
        "phone_number": "+1-555-0100"
    }


@pytest.fixture
def create_test_user(db_session, test_user_data):
    """Create a test user in database"""
    user = Customer(
        email=test_user_data["email"],
        password_hash=hash_password(test_user_data["password"]),
        first_name=test_user_data["first_name"],
        last_name=test_user_data["last_name"],
        phone_number=test_user_data["phone_number"],
        account_status=AccountStatus.ACTIVE
    )
    db_session.add(user)
    db_session.commit()
    return user


# ==================== Security Tests ====================

class TestSecurityFunctions:
    """Test security utility functions"""

    def test_hash_password(self):
        """Test password hashing"""
        password = "TestPass123"
        hashed = hash_password(password)
        
        # Hash should not be equal to plain password
        assert hashed != password
        # Hash should be bcrypt format
        assert hashed.startswith("$2b$")

    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        password = "TestPass123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        password = "TestPass123"
        wrong_password = "WrongPass456"
        hashed = hash_password(password)
        
        assert verify_password(wrong_password, hashed) is False

    def test_create_access_token(self):
        """Test JWT token creation"""
        data = {"sub": "testuser@example.com", "user_id": 1}
        token = create_access_token(data)
        
        # Token should be string
        assert isinstance(token, str)
        # Token should have 3 parts
        assert len(token.split(".")) == 3

    def test_decode_token_valid(self):
        """Test JWT token decoding with valid token"""
        data = {"sub": "testuser@example.com", "user_id": 1}
        token = create_access_token(data)
        decoded = decode_token(token)
        
        assert decoded["sub"] == "testuser@example.com"
        assert decoded["user_id"] == 1

    def test_decode_token_expired(self):
        """Test JWT token decoding with expired token"""
        # Create token with past expiration
        expires_delta = timedelta(minutes=-1)
        data = {"sub": "testuser@example.com", "user_id": 1}
        token = create_access_token(data, expires_delta)
        
        # Should raise HTTPException
        with pytest.raises(Exception):  # HTTPException
            decode_token(token)

    def test_decode_token_invalid(self):
        """Test JWT token decoding with invalid token"""
        invalid_token = "invalid.token.here"
        
        with pytest.raises(Exception):
            decode_token(invalid_token)


# ==================== AuthService Tests ====================

class TestAuthService:
    """Test authentication service layer"""

    def test_register_user_success(self, auth_service, test_user_data):
        """Test successful user registration"""
        user = auth_service.register_user(
            email=test_user_data["email"],
            password=test_user_data["password"],
            first_name=test_user_data["first_name"],
            last_name=test_user_data["last_name"],
            phone_number=test_user_data["phone_number"]
        )
        
        assert user.email == test_user_data["email"]
        assert user.first_name == test_user_data["first_name"]
        assert user.account_status == AccountStatus.ACTIVE
        assert verify_password(test_user_data["password"], user.password_hash)

    def test_register_user_duplicate_email(self, auth_service, create_test_user, test_user_data):
        """Test registration with duplicate email"""
        with pytest.raises(Exception):  # HTTPException with 400
            auth_service.register_user(
                email=test_user_data["email"],
                password="AnotherPass123",
                first_name="Another",
                last_name="User"
            )

    def test_authenticate_user_success(self, auth_service, create_test_user, test_user_data):
        """Test successful authentication"""
        user, token = auth_service.authenticate_user(
            email=test_user_data["email"],
            password=test_user_data["password"]
        )
        
        assert user.email == test_user_data["email"]
        assert isinstance(token, str)
        # Token should decode successfully
        decoded = decode_token(token)
        assert decoded["sub"] == test_user_data["email"]

    def test_authenticate_user_invalid_password(self, auth_service, create_test_user, test_user_data):
        """Test authentication with wrong password"""
        with pytest.raises(Exception):  # HTTPException with 401
            auth_service.authenticate_user(
                email=test_user_data["email"],
                password="WrongPassword123"
            )

    def test_authenticate_user_not_found(self, auth_service):
        """Test authentication with non-existent email"""
        with pytest.raises(Exception):  # HTTPException with 401
            auth_service.authenticate_user(
                email="nonexistent@example.com",
                password="TestPass123"
            )

    def test_authenticate_user_inactive_account(self, auth_service, db_session, test_user_data):
        """Test authentication with inactive account"""
        # Create inactive user
        user = Customer(
            email=test_user_data["email"],
            password_hash=hash_password(test_user_data["password"]),
            first_name=test_user_data["first_name"],
            last_name=test_user_data["last_name"],
            account_status=AccountStatus.INACTIVE
        )
        db_session.add(user)
        db_session.commit()
        
        with pytest.raises(Exception):  # HTTPException with 403
            auth_service.authenticate_user(
                email=test_user_data["email"],
                password=test_user_data["password"]
            )

    def test_get_user_by_email(self, auth_service, create_test_user, test_user_data):
        """Test retrieving user by email"""
        user = auth_service.get_user_by_email(test_user_data["email"])
        
        assert user is not None
        assert user.email == test_user_data["email"]

    def test_get_user_by_email_not_found(self, auth_service):
        """Test retrieving non-existent user"""
        user = auth_service.get_user_by_email("nonexistent@example.com")
        
        assert user is None

    def test_change_password_success(self, auth_service, create_test_user, test_user_data):
        """Test successful password change"""
        new_password = "NewPass456"
        
        auth_service.change_password(
            customer_id=create_test_user.customer_id,
            current_password=test_user_data["password"],
            new_password=new_password
        )
        
        # Verify new password works
        user = auth_service.get_user_by_id(create_test_user.customer_id)
        assert verify_password(new_password, user.password_hash)
        # Verify old password doesn't work
        assert not verify_password(test_user_data["password"], user.password_hash)

    def test_change_password_wrong_current(self, auth_service, create_test_user):
        """Test password change with wrong current password"""
        with pytest.raises(Exception):  # HTTPException
            auth_service.change_password(
                customer_id=create_test_user.customer_id,
                current_password="WrongPassword",
                new_password="NewPass456"
            )

    def test_deactivate_account(self, auth_service, create_test_user):
        """Test account deactivation"""
        auth_service.deactivate_account(create_test_user.customer_id)
        
        user = auth_service.get_user_by_id(create_test_user.customer_id)
        assert user.account_status == AccountStatus.INACTIVE

    def test_is_email_available_true(self, auth_service):
        """Test email availability check - available"""
        available = auth_service.is_email_available("available@example.com")
        
        assert available is True

    def test_is_email_available_false(self, auth_service, create_test_user, test_user_data):
        """Test email availability check - not available"""
        available = auth_service.is_email_available(test_user_data["email"])
        
        assert available is False


# ==================== API Endpoint Tests ====================

class TestSignupEndpoint:
    """Test POST /api/auth/signup"""

    def test_signup_success(self, client, test_user_data):
        """Test successful signup"""
        response = client.post(
            "/api/auth/signup",
            json=test_user_data
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["customer"]["email"] == test_user_data["email"]
        assert data["customer"]["account_status"] == "active"

    def test_signup_duplicate_email(self, client, create_test_user, test_user_data):
        """Test signup with existing email"""
        response = client.post(
            "/api/auth/signup",
            json=test_user_data
        )
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    def test_signup_invalid_email(self, client):
        """Test signup with invalid email"""
        response = client.post(
            "/api/auth/signup",
            json={
                "email": "invalid-email",
                "password": "TestPass123",
                "first_name": "Test",
                "last_name": "User"
            }
        )
        
        assert response.status_code == 422

    def test_signup_weak_password_no_uppercase(self, client):
        """Test signup with weak password - no uppercase"""
        response = client.post(
            "/api/auth/signup",
            json={
                "email": "test@example.com",
                "password": "testpass123",
                "first_name": "Test",
                "last_name": "User"
            }
        )
        
        assert response.status_code == 422

    def test_signup_weak_password_no_digit(self, client):
        """Test signup with weak password - no digit"""
        response = client.post(
            "/api/auth/signup",
            json={
                "email": "test@example.com",
                "password": "TestPassword",
                "first_name": "Test",
                "last_name": "User"
            }
        )
        
        assert response.status_code == 422

    def test_signup_short_password(self, client):
        """Test signup with password too short"""
        response = client.post(
            "/api/auth/signup",
            json={
                "email": "test@example.com",
                "password": "Test1",
                "first_name": "Test",
                "last_name": "User"
            }
        )
        
        assert response.status_code == 422


class TestLoginEndpoint:
    """Test POST /api/auth/login"""

    def test_login_success(self, client, create_test_user, test_user_data):
        """Test successful login"""
        response = client.post(
            "/api/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["customer"]["email"] == test_user_data["email"]

    def test_login_invalid_email(self, client):
        """Test login with non-existent email"""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "TestPass123"
            }
        )
        
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    def test_login_invalid_password(self, client, create_test_user, test_user_data):
        """Test login with wrong password"""
        response = client.post(
            "/api/auth/login",
            json={
                "email": test_user_data["email"],
                "password": "WrongPassword123"
            }
        )
        
        assert response.status_code == 401

    def test_login_inactive_account(self, client, db_session, test_user_data):
        """Test login with inactive account"""
        # Create inactive user
        user = Customer(
            email=test_user_data["email"],
            password_hash=hash_password(test_user_data["password"]),
            first_name=test_user_data["first_name"],
            last_name=test_user_data["last_name"],
            account_status=AccountStatus.INACTIVE
        )
        db_session.add(user)
        db_session.commit()
        
        response = client.post(
            "/api/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )
        
        assert response.status_code == 403


class TestGetMeEndpoint:
    """Test GET /api/auth/me"""

    def test_get_me_success(self, client, create_test_user):
        """Test get current user success"""
        # Login first to get token
        response = client.post(
            "/api/auth/login",
            json={
                "email": create_test_user.email,
                "password": "TestPass123"
            }
        )
        token = response.json()["access_token"]
        
        # Get current user
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert response.json()["email"] == create_test_user.email

    def test_get_me_no_token(self, client):
        """Test get current user without token"""
        response = client.get("/api/auth/me")
        
        assert response.status_code == 403

    def test_get_me_invalid_token(self, client):
        """Test get current user with invalid token"""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"}
        )
        
        assert response.status_code == 401


class TestChangePasswordEndpoint:
    """Test POST /api/auth/change-password"""

    def test_change_password_success(self, client, create_test_user, test_user_data):
        """Test successful password change"""
        # Login to get token
        response = client.post(
            "/api/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )
        token = response.json()["access_token"]
        
        # Change password
        response = client.post(
            "/api/auth/change-password",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "current_password": test_user_data["password"],
                "new_password": "NewPass456",
                "confirm_password": "NewPass456"
            }
        )
        
        assert response.status_code == 200

    def test_change_password_wrong_current(self, client, create_test_user, test_user_data):
        """Test password change with wrong current password"""
        # Login to get token
        response = client.post(
            "/api/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )
        token = response.json()["access_token"]
        
        # Try to change with wrong current password
        response = client.post(
            "/api/auth/change-password",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "current_password": "WrongPassword",
                "new_password": "NewPass456",
                "confirm_password": "NewPass456"
            }
        )
        
        assert response.status_code == 401

    def test_change_password_mismatch(self, client, create_test_user, test_user_data):
        """Test password change with mismatched new passwords"""
        # Login to get token
        response = client.post(
            "/api/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )
        token = response.json()["access_token"]
        
        # Try to change with mismatched passwords
        response = client.post(
            "/api/auth/change-password",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "current_password": test_user_data["password"],
                "new_password": "NewPass456",
                "confirm_password": "DifferentPass456"
            }
        )
        
        assert response.status_code == 422


class TestCheckEmailEndpoint:
    """Test POST /api/auth/check-email"""

    def test_check_email_available(self, client):
        """Test check available email"""
        response = client.post(
            "/api/auth/check-email",
            json={"email": "available@example.com"}
        )
        
        assert response.status_code == 200
        assert response.json()["available"] is True

    def test_check_email_not_available(self, client, create_test_user, test_user_data):
        """Test check taken email"""
        response = client.post(
            "/api/auth/check-email",
            json={"email": test_user_data["email"]}
        )
        
        assert response.status_code == 200
        assert response.json()["available"] is False


class TestDeactivateEndpoint:
    """Test POST /api/auth/deactivate"""

    def test_deactivate_success(self, client, create_test_user, test_user_data):
        """Test successful account deactivation"""
        # Login to get token
        response = client.post(
            "/api/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )
        token = response.json()["access_token"]
        
        # Deactivate account
        response = client.post(
            "/api/auth/deactivate",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        
        # Try to login again - should fail
        response = client.post(
            "/api/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )
        assert response.status_code == 403


class TestValidateTokenEndpoint:
    """Test GET /api/auth/validate-token"""

    def test_validate_token_valid(self, client, create_test_user, test_user_data):
        """Test token validation with valid token"""
        # Login to get token
        response = client.post(
            "/api/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )
        token = response.json()["access_token"]
        
        # Validate token
        response = client.get(
            "/api/auth/validate-token",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200

    def test_validate_token_invalid(self, client):
        """Test token validation with invalid token"""
        response = client.get(
            "/api/auth/validate-token",
            headers={"Authorization": "Bearer invalid.token.here"}
        )
        
        assert response.status_code == 401


# ==================== Integration Tests ====================

class TestAuthenticationFlow:
    """Test complete authentication flows"""

    def test_signup_login_flow(self, client, test_user_data):
        """Test signup followed by login"""
        # Signup
        signup_response = client.post("/api/auth/signup", json=test_user_data)
        assert signup_response.status_code == 201
        signup_token = signup_response.json()["access_token"]
        
        # Login with same credentials
        login_response = client.post(
            "/api/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )
        assert login_response.status_code == 200
        login_token = login_response.json()["access_token"]
        
        # Both tokens should work for getting current user
        for token in [signup_token, login_token]:
            response = client.get(
                "/api/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 200
            assert response.json()["email"] == test_user_data["email"]

    def test_password_change_flow(self, client, create_test_user, test_user_data):
        """Test password change and re-login"""
        # Login with old password
        response = client.post(
            "/api/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )
        assert response.status_code == 200
        token = response.json()["access_token"]
        
        # Change password
        new_password = "NewPass789"
        response = client.post(
            "/api/auth/change-password",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "current_password": test_user_data["password"],
                "new_password": new_password,
                "confirm_password": new_password
            }
        )
        assert response.status_code == 200
        
        # Old password should not work
        response = client.post(
            "/api/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )
        assert response.status_code == 401
        
        # New password should work
        response = client.post(
            "/api/auth/login",
            json={
                "email": test_user_data["email"],
                "password": new_password
            }
        )
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
