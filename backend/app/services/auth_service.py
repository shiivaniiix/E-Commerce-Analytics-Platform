"""
Authentication service layer
Handles user registration, login, and token management
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from typing import Optional, Tuple

from app.models import Customer
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_token
)
from app.core.config import get_settings
from app.models import AccountStatus

settings = get_settings()


class AuthService:
    """Service layer for authentication operations"""

    @staticmethod
    def register_user(
        db: Session,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        phone_number: Optional[str] = None
    ) -> Customer:
        """
        Register a new user
        
        Args:
            db: Database session
            email: User email (must be unique)
            password: User password (will be hashed)
            first_name: User first name
            last_name: User last name
            phone_number: Optional phone number
            
        Returns:
            Customer: Newly created customer
            
        Raises:
            HTTPException: If email already exists
        """
        # Check if email already exists
        existing_user = db.query(Customer).filter(
            Customer.email == email
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered. Please use a different email or login."
            )
        
        # Create new customer
        hashed_password = hash_password(password)
        
        new_customer = Customer(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password_hash=hashed_password,
            phone_number=phone_number,
            account_status=AccountStatus.ACTIVE,
            account_created_at=datetime.utcnow()
        )
        
        db.add(new_customer)
        db.commit()
        db.refresh(new_customer)
        
        return new_customer

    @staticmethod
    def authenticate_user(
        db: Session,
        email: str,
        password: str
    ) -> Tuple[Customer, str]:
        """
        Authenticate user and return access token
        
        Args:
            db: Database session
            email: User email
            password: User password (plain text)
            
        Returns:
            Tuple of (Customer, access_token)
            
        Raises:
            HTTPException: If credentials are invalid or account is inactive
        """
        # Find user by email
        user = db.query(Customer).filter(
            Customer.email == email
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if account is active
        if user.account_status != AccountStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Account is {user.account_status.value}. Please contact support."
            )
        
        # Create access token
        access_token = create_access_token(
            data={
                "sub": str(user.customer_id),
                "email": user.email
            }
        )
        
        return user, access_token

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[Customer]:
        """
        Get user by ID
        
        Args:
            db: Database session
            user_id: Customer ID
            
        Returns:
            Customer or None
        """
        return db.query(Customer).filter(
            Customer.customer_id == user_id
        ).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[Customer]:
        """
        Get user by email
        
        Args:
            db: Database session
            email: User email
            
        Returns:
            Customer or None
        """
        return db.query(Customer).filter(
            Customer.email == email
        ).first()

    @staticmethod
    def get_current_user_from_token(
        db: Session,
        token: str
    ) -> Customer:
        """
        Get current user from JWT token
        
        Args:
            db: Database session
            token: JWT token
            
        Returns:
            Customer
            
        Raises:
            HTTPException: If token is invalid or user not found
        """
        try:
            payload = decode_token(token)
            user_id: Optional[str] = payload.get("sub")
            
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials"
                )
            
            user = AuthService.get_user_by_id(db, int(user_id))
            
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )
            
            if user.account_status != AccountStatus.ACTIVE:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Account is inactive"
                )
            
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )

    @staticmethod
    def change_password(
        db: Session,
        user_id: int,
        current_password: str,
        new_password: str
    ) -> bool:
        """
        Change user password
        
        Args:
            db: Database session
            user_id: Customer ID
            current_password: Current password (plain text)
            new_password: New password (plain text)
            
        Returns:
            bool: True if successful
            
        Raises:
            HTTPException: If password is incorrect or user not found
        """
        user = AuthService.get_user_by_id(db, user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify current password
        if not verify_password(current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect"
            )
        
        # Update password
        user.password_hash = hash_password(new_password)
        db.commit()
        
        return True

    @staticmethod
    def deactivate_account(db: Session, user_id: int) -> bool:
        """
        Deactivate user account
        
        Args:
            db: Database session
            user_id: Customer ID
            
        Returns:
            bool: True if successful
        """
        user = AuthService.get_user_by_id(db, user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.account_status = AccountStatus.INACTIVE
        db.commit()
        return True

    @staticmethod
    def is_email_available(db: Session, email: str) -> bool:
        """
        Check if email is available for registration
        
        Args:
            db: Database session
            email: Email to check
            
        Returns:
            bool: True if available, False if taken
        """
        user = db.query(Customer).filter(
            Customer.email == email
        ).first()
        return user is None
