from pathlib import Path
from typing import List, Optional

import pandas as pd

from app.core.config import get_settings
from app.export.logging_config import get_logger
from app.export.postgres_utils import get_db_engine
from app.export.s3_utils import upload_file_to_s3

logger = get_logger(__name__)

DEFAULT_TABLES = [
    "customers",
    "products",
    "orders",
    "order_items",
]


def export_table_to_csv(
    engine,
    table_name: str,
    export_folder: Path,
) -> Path:
    """Export a PostgreSQL table to a CSV file."""
    export_folder.mkdir(parents=True, exist_ok=True)
    file_path = export_folder / f"{table_name}.csv"
    query = f"SELECT * FROM {table_name};"

    try:
        logger.info("Exporting table %s to %s", table_name, file_path)
        dataframe = pd.read_sql_query(query, con=engine)
        dataframe.to_csv(file_path, index=False)
        logger.info(
            "Exported %s rows from %s to %s",
            len(dataframe),
            table_name,
            file_path,
        )
        return file_path
    except Exception as exc:
        logger.exception("Failed to export table %s", table_name)
        raise RuntimeError(f"Failed to export {table_name}") from exc


def upload_csv_files(
    csv_paths: List[Path],
    bucket_name: str,
    prefix: Optional[str] = None,
) -> List[str]:
    """Upload CSV files to S3 and return the uploaded object keys."""
    uploaded_keys = []

    for path in csv_paths:
        object_key = f"{prefix.rstrip('/')}/{path.name}" if prefix else path.name
        upload_file_to_s3(path, bucket_name, object_key)
        uploaded_keys.append(object_key)

    return uploaded_keys


def run_export_pipeline(
    tables: Optional[List[str]] = None,
    export_folder: Optional[str] = None,
    s3_prefix: Optional[str] = None,
) -> List[str]:
    """Run the export pipeline for the configured tables."""
    settings = get_settings()
    tables = tables or DEFAULT_TABLES
    export_folder = export_folder or settings.EXPORT_FOLDER
    s3_prefix = s3_prefix or settings.AWS_S3_PREFIX

    logger.info("Starting export pipeline")
    engine = get_db_engine()
    export_dir = Path(export_folder)

    try:
        csv_paths = [export_table_to_csv(engine, table, export_dir) for table in tables]
        logger.info("All tables exported successfully")

        if not settings.AWS_S3_BUCKET:
            raise RuntimeError("AWS_S3_BUCKET is not configured")

        uploaded_keys = upload_csv_files(csv_paths, settings.AWS_S3_BUCKET, s3_prefix)
        logger.info("Export pipeline completed successfully")
        return uploaded_keys
    except Exception as exc:
        logger.exception("Export pipeline failed")
        raise
