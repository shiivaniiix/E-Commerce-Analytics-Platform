from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
from app.models import Product, Category


class ProductService:
    """Service layer for product operations"""

    @staticmethod
    def get_products(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        category_id: Optional[int] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Product], int]:
        """Retrieve active products with optional filtering and pagination"""
        query = db.query(Product).filter(Product.is_active == True)

        if category_id is not None:
            query = query.filter(Product.category_id == category_id)

        if search:
            search_pattern = f"%{search}%"
            query = query.filter(Product.product_name.ilike(search_pattern))

        total = query.count()
        products = (
            query.order_by(Product.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return products, total

    @staticmethod
    def get_product_by_id(
        db: Session,
        product_id: int,
        active_only: bool = True,
    ) -> Optional[Product]:
        """Retrieve a product by its ID"""
        query = db.query(Product).filter(Product.product_id == product_id)
        if active_only:
            query = query.filter(Product.is_active == True)
        return query.first()

    @staticmethod
    def create_product(db: Session, product_data: dict) -> Product:
        """Create a new product record"""
        category_id = product_data.get('category_id')
        category = db.query(Category).filter(Category.category_id == category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {category_id} not found"
            )

        product = Product(**product_data)
        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def update_product(db: Session, product_id: int, update_data: dict) -> Optional[Product]:
        """Update an existing product record"""
        product = ProductService.get_product_by_id(db, product_id, active_only=False)
        if not product:
            return None

        if 'category_id' in update_data and update_data['category_id'] is not None:
            category = db.query(Category).filter(Category.category_id == update_data['category_id']).first()
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Category with id {update_data['category_id']} not found"
                )

        for key, value in update_data.items():
            if hasattr(product, key) and value is not None:
                setattr(product, key, value)

        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def delete_product(db: Session, product_id: int) -> bool:
        """Soft delete a product by marking it inactive"""
        product = ProductService.get_product_by_id(db, product_id, active_only=False)
        if not product:
            return False

        product.is_active = False
        db.commit()
        return True
