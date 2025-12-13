from __future__ import annotations
from pathlib import Path

# Centralised configuration constants.
DEFAULT_DB_PATH: Path = Path(__file__).resolve().parent.parent / 'data' / 'public_health.db'
LOG_FILE: Path = Path(__file__).resolve().parent.parent / 'logs' / 'app.log'
FIG_SIZE = (10, 5)
