"""
Lightweight idempotent migration.

Adds the `image_url` column to the `products` table for databases that were
created before the column existed. Safe to run multiple times.

Usage:
    python migrate_add_product_image.py
"""

import logging

from sqlalchemy import inspect, text

from app.db.base import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def column_exists(table: str, column: str) -> bool:
    inspector = inspect(engine)
    if table not in inspector.get_table_names():
        return False
    return any(col["name"] == column for col in inspector.get_columns(table))


def run() -> None:
    if column_exists("products", "image_url"):
        logger.info("products.image_url already exists — nothing to do.")
        return

    logger.info("Adding products.image_url column...")
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE products ADD COLUMN image_url VARCHAR(500)"))
    logger.info("Done. products.image_url added.")


if __name__ == "__main__":
    run()
