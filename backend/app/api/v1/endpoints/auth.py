"""
Authentication endpoints
Handles user signup, login, and profile management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import timedelta

from app.db.base import get_db
from app.schemas import (
    SignupRequest, LoginRequest, ChangePasswordRequest,
    AuthResponse, CustomerResponse, EmailCheckRequest,
    EmailCheckResponse, TokenResponse
)
from app.core.config import get_settings
from app.core.security import get_current_user
from app.services.auth_service import AuthService

router = APIRouter()
settings = get_settings()


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    signup_data: SignupRequest,
    db: Session = Depends(get_db)
):
    """
    User signup endpoint
    
    Creates a new customer account with email and password
    
    Args:
        signup_data: User registration data
        db: Database session
        
    Returns:
        AuthResponse: Contains access token and user info
        
    Raises:
        HTTPException 400: If email already exists
        HTTPException 422: If validation fails
    """
    try:
        # Register user
        user = AuthService.register_user(
            db=db,
            email=signup_data.email,
            password=signup_data.password,
            first_name=signup_data.first_name,
            last_name=signup_data.last_name,
            phone_number=signup_data.phone_number
        )
        
        # Create access token
        expires_delta = timedelta(hours=24)
        access_token = AuthService.authenticate_user(
            db=db,
            email=signup_data.email,
            password=signup_data.password
        )[1]
        
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=int(expires_delta.total_seconds()),
            customer=CustomerResponse.model_validate(user)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during signup"
        )


@router.post("/login", response_model=AuthResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    User login endpoint
    
    Authenticates user with email and password, returns JWT token
    
    Args:
        login_data: User credentials
        db: Database session
        
    Returns:
        AuthResponse: Contains access token and user info
        
    Raises:
        HTTPException 401: If credentials are invalid
        HTTPException 403: If account is inactive
    """
    try:
        # Authenticate user
        user, access_token = AuthService.authenticate_user(
            db=db,
            email=login_data.email,
            password=login_data.password
        )
        
        expires_delta = timedelta(hours=24)
        
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=int(expires_delta.total_seconds()),
            customer=CustomerResponse.model_validate(user)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login"
        )


@router.get("/me", response_model=CustomerResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user information
    
    Requires valid JWT token
    
    Returns:
        CustomerResponse: Current user information
        
    Raises:
        HTTPException 401: If token is invalid
    """
    try:
        user = AuthService.get_user_by_id(db, int(current_user["user_id"]))
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return CustomerResponse.model_validate(user)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching user information"
        )


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    change_password_data: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change user password
    
    Requires valid JWT token and current password
    
    Args:
        change_password_data: Current and new passwords
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException 401: If current password is incorrect
        HTTPException 404: If user not found
    """
    try:
        AuthService.change_password(
            db=db,
            user_id=int(current_user["user_id"]),
            current_password=change_password_data.current_password,
            new_password=change_password_data.new_password
        )
        
        return {
            "message": "Password changed successfully",
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while changing password"
        )


@router.post("/check-email", response_model=EmailCheckResponse)
async def check_email_availability(
    email_data: EmailCheckRequest,
    db: Session = Depends(get_db)
):
    """
    Check if email is available for registration
    
    Args:
        email_data: Email to check
        db: Database session
        
    Returns:
        EmailCheckResponse: Email availability status
    """
    try:
        available = AuthService.is_email_available(db, email_data.email)
        
        return EmailCheckResponse(
            email=email_data.email,
            available=available
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while checking email"
        )


@router.post("/deactivate", status_code=status.HTTP_200_OK)
async def deactivate_account(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deactivate user account
    
    Requires valid JWT token
    
    Returns:
        dict: Success message
        
    Raises:
        HTTPException 404: If user not found
    """
    try:
        AuthService.deactivate_account(
            db=db,
            user_id=int(current_user["user_id"])
        )
        
        return {
            "message": "Account deactivated successfully",
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deactivating account"
        )


@router.get("/validate-token", response_model=TokenResponse)
async def validate_token(
    current_user: dict = Depends(get_current_user)
):
    """
    Validate JWT token
    
    Requires valid JWT token
    
    Returns:
        TokenResponse: Token validity confirmation
    """
    return TokenResponse(
        access_token="token_valid",
        token_type="bearer",
        expires_in=86400
    )
