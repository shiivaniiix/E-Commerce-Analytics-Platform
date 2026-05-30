"""
Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional, List
from enum import Enum


# ==================== Enums ====================

class AccountStatusSchema(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class OrderStatusSchema(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    RETURNED = "returned"


class PaymentStatusSchema(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class InventoryChangeTypeSchema(str, Enum):
    PURCHASE = "purchase"
    RETURN = "return"
    RESTOCK = "restock"
    DAMAGED = "damaged"
    ADJUSTMENT = "adjustment"


# ==================== Customer Schemas ====================

class CustomerBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone_number: Optional[str] = Field(None, max_length=20)


class CustomerCreate(CustomerBase):
    password: str = Field(..., min_length=8)


class CustomerUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=20)
    account_status: Optional[AccountStatusSchema] = None


class CustomerResponse(CustomerBase):
    customer_id: int
    account_created_at: datetime
    account_status: AccountStatusSchema

    class Config:
        from_attributes = True


class CustomerDetailResponse(CustomerResponse):
    addresses: Optional[List["AddressResponse"]] = []
    orders: Optional[List["OrderResponse"]] = []


# ==================== Address Schemas ====================

class AddressBase(BaseModel):
    address_line1: str = Field(..., max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: str = Field(..., max_length=100)
    state: str = Field(..., max_length=100)
    country: str = Field(..., max_length=100)
    pincode: str = Field(..., max_length=20)
    is_default: bool = False


class AddressCreate(AddressBase):
    pass


class AddressUpdate(BaseModel):
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    pincode: Optional[str] = None
    is_default: Optional[bool] = None


class AddressResponse(AddressBase):
    address_id: int
    customer_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== Category Schemas ====================

class CategoryBase(BaseModel):
    category_name: str = Field(..., max_length=150)
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    category_name: Optional[str] = None
    description: Optional[str] = None


class CategoryResponse(CategoryBase):
    category_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Product Schemas ====================

class ProductBase(BaseModel):
    product_name: str = Field(..., max_length=255)
    category_id: int
    brand: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    selling_price: float = Field(..., gt=0)
    cost_price: float = Field(..., ge=0)
    stock_quantity: int = Field(default=0, ge=0)
    is_active: bool = True

    @validator('selling_price')
    def selling_price_positive(cls, v):
        if v <= 0:
            raise ValueError('Selling price must be greater than 0')
        return v

    @validator('selling_price')
    def selling_price_greater_than_cost(cls, v, values):
        if 'cost_price' in values and v <= values['cost_price']:
            raise ValueError('Selling price must be greater than cost price')
        return v


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    product_name: Optional[str] = None
    category_id: Optional[int] = None
    brand: Optional[str] = None
    description: Optional[str] = None
    selling_price: Optional[float] = None
    cost_price: Optional[float] = None
    stock_quantity: Optional[int] = None
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    product_id: int
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryResponse] = None

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    products: List[ProductResponse]
    total: int
    page: int
    page_size: int

    class Config:
        from_attributes = True


# ==================== Cart Schemas ====================

class CartItemBase(BaseModel):
    product_id: int
    quantity: int = Field(..., ge=1)


class CartItemCreate(CartItemBase):
    pass


class CartItemUpdate(BaseModel):
    quantity: int = Field(..., ge=1)


class CartItemResponse(CartItemBase):
    cart_item_id: int
    cart_id: int
    added_at: datetime
    updated_at: datetime
    product: Optional[ProductResponse] = None

    class Config:
        from_attributes = True


class CartBase(BaseModel):
    customer_id: int


class CartCreate(CartBase):
    pass


class CartResponse(CartBase):
    cart_id: int
    created_at: datetime
    updated_at: datetime
    cart_items: Optional[List[CartItemResponse]] = []

    class Config:
        from_attributes = True


# ==================== Order Schemas ====================

class OrderItemBase(BaseModel):
    product_id: int
    quantity: int = Field(..., ge=1)
    unit_price: float = Field(..., gt=0)


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemResponse(OrderItemBase):
    order_item_id: int
    order_id: int
    created_at: datetime
    product: Optional[ProductResponse] = None

    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    customer_id: int
    address_id: int
    payment_method: str
    subtotal: float = Field(..., gt=0)
    tax_amount: float = Field(default=0, ge=0)
    discount_amount: float = Field(default=0, ge=0)
    shipping_fee: float = Field(default=0, ge=0)
    total_amount: float = Field(..., gt=0)


class OrderCreate(BaseModel):
    customer_id: int
    address_id: int
    payment_method: str
    items: List[OrderItemCreate]
    tax_amount: float = Field(default=0, ge=0)
    discount_amount: float = Field(default=0, ge=0)
    shipping_fee: float = Field(default=0, ge=0)


class OrderUpdate(BaseModel):
    order_status: Optional[OrderStatusSchema] = None
    payment_status: Optional[PaymentStatusSchema] = None


class OrderResponse(OrderBase):
    order_id: int
    payment_status: PaymentStatusSchema
    order_status: OrderStatusSchema
    placed_at: datetime
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    order_items: Optional[List[OrderItemResponse]] = []
    customer: Optional[CustomerResponse] = None
    address: Optional[AddressResponse] = None

    class Config:
        from_attributes = True


# ==================== Payment Schemas ====================

class PaymentBase(BaseModel):
    order_id: int
    payment_method: str
    amount: float = Field(..., gt=0)


class PaymentCreate(PaymentBase):
    pass


class PaymentResponse(PaymentBase):
    payment_id: int
    payment_status: PaymentStatusSchema
    transaction_reference: Optional[str] = None
    paid_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== Inventory Log Schemas ====================

class InventoryLogBase(BaseModel):
    product_id: int
    change_type: InventoryChangeTypeSchema
    quantity_changed: int
    reason: Optional[str] = None


class InventoryLogCreate(InventoryLogBase):
    pass


class InventoryLogResponse(InventoryLogBase):
    inventory_log_id: int
    changed_at: datetime
    created_at: datetime
    product: Optional[ProductResponse] = None

    class Config:
        from_attributes = True


# ==================== Authentication Schemas ====================

class SignupRequest(BaseModel):
    """Schema for user signup"""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=20)

    @validator('password')
    def password_strength(cls, v):
        """Validate password strength"""
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        return v


class LoginRequest(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str = Field(..., description="User password")


class ChangePasswordRequest(BaseModel):
    """Schema for changing password"""
    current_password: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str

    @validator('new_password')
    def password_strength(cls, v):
        """Validate new password strength"""
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        return v

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """Ensure passwords match"""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class AuthResponse(BaseModel):
    """Schema for authentication response (signup/login)"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    customer: CustomerResponse


class EmailCheckRequest(BaseModel):
    """Schema for checking email availability"""
    email: EmailStr


class EmailCheckResponse(BaseModel):
    """Schema for email availability response"""
    email: str
    available: bool


class HealthResponse(BaseModel):
    status: str
    message: str
    version: str
