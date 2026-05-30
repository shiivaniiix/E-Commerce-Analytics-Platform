"""
FastAPI application initialization
Main entry point for the E-Commerce Analytics Platform API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router
from app.core.config import get_settings

settings = get_settings()

# Create FastAPI application with metadata
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="E-Commerce Analytics Platform API with authentication, products, orders, and more",
    debug=settings.DEBUG,
)

# Add CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)


# Include API routers
app.include_router(router, prefix=settings.API_PREFIX)


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "message": "E-Commerce Analytics Platform API",
        "version": settings.API_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
        "status": "running"
    }


@app.get("/status")
async def status_check():
    """Status check endpoint"""
    return {
        "status": "healthy",
        "api_version": settings.API_VERSION,
        "environment": settings.ENVIRONMENT
    }


# Event handlers
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    print(f"Starting {settings.API_TITLE} v{settings.API_VERSION}")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Debug mode: {settings.DEBUG}")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    print(f"Shutting down {settings.API_TITLE}")
