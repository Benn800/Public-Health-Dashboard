from __future__ import annotations
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from .config import LOG_FILE



# src/logging_conf.py

def setup_logging(log_path: Path | None = None) -> None:
    import logging
    from logging.handlers import RotatingFileHandler
    from pathlib import Path
    from .config import LOG_FILE

    log_file = Path(log_path) if log_path else LOG_FILE
    log_file.parent.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger()
    root.setLevel(logging.INFO)

    # REMOVE the console handler entirely:
    # ch = logging.StreamHandler()
    # ch.setLevel(logging.INFO)
    # ch.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))

    fh = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3)
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s'))

    # Reset handlers to avoid duplicates across test runs
    root.handlers.clear()
    root.addHandler(fh)


