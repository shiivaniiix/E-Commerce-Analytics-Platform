from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler
from app.core.config import get_settings


def get_logger(name: str = "export_pipeline") -> logging.Logger:
    settings = get_settings()
    log_dir = Path(settings.EXPORT_FOLDER or "exports") / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "export.log"

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=5_242_880,
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
