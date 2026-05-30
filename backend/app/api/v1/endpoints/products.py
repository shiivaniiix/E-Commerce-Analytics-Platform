"""
Product endpoints
Handles product creation, retrieval, update, delete, filtering, search and pagination
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.schemas import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse,
)
from app.services.product_service import ProductService
from app.models import Category

router = APIRouter()


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db)
):
    """Create a new product"""
    category = db.query(Category).filter(Category.category_id == product_data.category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {product_data.category_id} not found"
        )

    try:
        product = ProductService.create_product(db, product_data.model_dump())
        return ProductResponse.model_validate(product)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the product"
        )


@router.get("", response_model=ProductListResponse)
async def list_products(
    page: int = Query(1, ge=1, title="Page number", description="Page number for pagination."),
    page_size: int = Query(20, ge=1, le=100, title="Page size", description="Number of products per page."),
    category_id: Optional[int] = Query(None, title="Category ID", description="Filter products by category."),
    search: Optional[str] = Query(None, title="Search", description="Search products by name."),
    db: Session = Depends(get_db),
):
    """List products with pagination, category filtering, and search"""
    try:
        skip = (page - 1) * page_size
        products, total = ProductService.get_products(
            db=db,
            skip=skip,
            limit=page_size,
            category_id=category_id,
            search=search,
        )

        return ProductListResponse(
            products=[ProductResponse.model_validate(product) for product in products],
            total=total,
            page=page,
            page_size=page_size,
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching products"
        )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int = Path(..., ge=1, title="Product ID", description="Unique product identifier."),
    db: Session = Depends(get_db),
):
    """Retrieve a single product by ID"""
    product = ProductService.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return ProductResponse.model_validate(product)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    update_data: ProductUpdate,
    product_id: int = Path(..., ge=1, title="Product ID", description="Unique product identifier."),
    db: Session = Depends(get_db),
):
    """Update an existing product"""
    try:
        product = ProductService.update_product(db, product_id, update_data.model_dump(exclude_unset=True))
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        return ProductResponse.model_validate(product)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the product"
        )


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int = Path(..., ge=1, title="Product ID", description="Unique product identifier."),
    db: Session = Depends(get_db),
):
    """Delete a product by setting it inactive"""
    deleted = ProductService.delete_product(db, product_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return None
