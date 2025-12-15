from __future__ import annotations
"""Application entrypoint.

Delegates directly to the CLI `main()` so that `python -m src.app`
behaves like a standard executable without extra wrappers.
"""
from .presentation.cli import main


if __name__ == "__main__": 
    # Exit codes are propagated from CLI; raising SystemExit keeps
    # behavior consistent with typical Python entrypoints.
    raise SystemExit(main())
