from fastapi import APIRouter

from app.api.v1.endpoints import health, auth, products

router = APIRouter()

# Include routers
router.include_router(health.router, prefix="", tags=["health"])
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(products.router, prefix="/products", tags=["products"])
