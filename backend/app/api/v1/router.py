from fastapi import APIRouter

from app.api.v1.endpoints import health, auth, cart, orders, products

router = APIRouter()

# Include routers
router.include_router(health.router, prefix="", tags=["health"])
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(cart.router, prefix="/cart", tags=["cart"])
router.include_router(orders.router, prefix="/orders", tags=["orders"])
router.include_router(products.router, prefix="/products", tags=["products"])
