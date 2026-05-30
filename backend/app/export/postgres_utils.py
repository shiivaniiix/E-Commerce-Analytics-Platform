from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import get_settings
from app.export.logging_config import get_logger

logger = get_logger(__name__)


def get_db_engine() -> Engine:
    """Create a SQLAlchemy engine for PostgreSQL using environment settings."""
    settings = get_settings()
    try:
        engine = create_engine(
            settings.DATABASE_URL,
            future=True,
            pool_pre_ping=True,
        )
        logger.info("Created PostgreSQL engine for export pipeline")
        return engine
    except SQLAlchemyError as exc:
        logger.exception("Failed to create PostgreSQL engine")
        raise RuntimeError("Unable to connect to PostgreSQL database") from exc
