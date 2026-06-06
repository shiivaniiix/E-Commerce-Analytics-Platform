"""
Category endpoints
Read-only listing of product categories for navigation/filtering.
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models import Category
from app.schemas import CategoryResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=List[CategoryResponse])
async def list_categories(db: Session = Depends(get_db)):
    """Return all product categories ordered by name."""
    try:
        categories = db.query(Category).order_by(Category.category_name.asc()).all()
        return [CategoryResponse.model_validate(c) for c in categories]
    except Exception:
        logger.exception("Failed to list categories")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching categories",
        )
