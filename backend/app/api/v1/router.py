from fastapi import APIRouter

from app.api.v1.endpoints import (
    health,
    auth,
    cart,
    orders,
    products,
    profile,
    addresses,
    categories,
)

router = APIRouter()

# Include routers
router.include_router(health.router, prefix="", tags=["health"])
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(profile.router, prefix="/profile", tags=["profile"])
router.include_router(addresses.router, prefix="/addresses", tags=["addresses"])
router.include_router(categories.router, prefix="/categories", tags=["categories"])
router.include_router(cart.router, prefix="/cart", tags=["cart"])
router.include_router(orders.router, prefix="/orders", tags=["orders"])
router.include_router(products.router, prefix="/products", tags=["products"])
