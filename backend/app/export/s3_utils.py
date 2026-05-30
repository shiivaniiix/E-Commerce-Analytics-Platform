from pathlib import Path
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from app.core.config import get_settings
from app.export.logging_config import get_logger

logger = get_logger(__name__)


def get_s3_client():
    """Return a boto3 S3 client configured from environment variables."""
    settings = get_settings()

    if not settings.AWS_ACCESS_KEY_ID or not settings.AWS_SECRET_ACCESS_KEY:
        logger.error("AWS credentials are not configured in environment variables")
        raise RuntimeError("AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY must be set")

    try:
        session = boto3.session.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION,
        )
        client = session.client("s3")
        logger.info("Created S3 client for bucket %s", settings.AWS_S3_BUCKET)
        return client
    except (BotoCoreError, ClientError) as exc:
        logger.exception("Failed to create S3 client")
        raise RuntimeError("Unable to initialize S3 client") from exc


def upload_file_to_s3(file_path: Path, bucket_name: str, object_key: str):
    """Upload a local file to AWS S3."""
    client = get_s3_client()
    try:
        logger.info("Uploading %s to s3://%s/%s", file_path, bucket_name, object_key)
        client.upload_file(str(file_path), bucket_name, object_key)
        logger.info("Successfully uploaded %s", object_key)
    except (BotoCoreError, ClientError) as exc:
        logger.exception("Failed to upload %s to S3", file_path)
        raise RuntimeError(f"Unable to upload {file_path.name} to S3") from exc
