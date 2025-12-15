from __future__ import annotations
"""Central logging configuration.

We use a rotating file handler to keep CLI output clean while
preserving detailed diagnostics for reproducibility and debugging.
"""
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from .config import LOG_FILE


def setup_logging(log_path: Path | None = None) -> None:
    """Configure a rotating file logger (max ~1MB, 3 backups).

    Console logging is disabled to keep CLI outputs focused on results.
    """
    import logging
    from logging.handlers import RotatingFileHandler
    from pathlib import Path
    from .config import LOG_FILE

    log_file = Path(log_path) if log_path else LOG_FILE
    log_file.parent.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger()
    root.setLevel(logging.INFO)

    fh = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3)
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s'))

    # Reset handlers to avoid duplicates across test runs
    root.handlers.clear()
    root.addHandler(fh)


