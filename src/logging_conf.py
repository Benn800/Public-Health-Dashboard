from __future__ import annotations
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from .config import LOG_FILE


def setup_logging(log_path: Path | None = None) -> None:
    # Configure application logging (console + rotating file)
    log_file = Path(log_path) if log_path else LOG_FILE
    log_file.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))

    fh = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3)
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s'))

    if not logger.handlers:
        logger.addHandler(ch)
        logger.addHandler(fh)
