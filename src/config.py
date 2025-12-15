from __future__ import annotations
"""Central configuration constants.

All paths are resolved relative to the repository root, enabling
portable execution across environments (Windows/macOS/Linux).
"""
from pathlib import Path

# Paths resolve from src/.. to top-level data/logs
DEFAULT_DB_PATH: Path = Path(__file__).resolve().parent.parent / 'data' / 'public_health.db'
LOG_FILE: Path = Path(__file__).resolve().parent.parent / 'logs' / 'app.log'

# Default figure size for charts; chosen for readability in reports
FIG_SIZE = (10, 5)
