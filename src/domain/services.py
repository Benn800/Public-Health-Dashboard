from __future__ import annotations
"""Pure domain services: filtering and summaries.

These functions operate purely on in-memory records (list/dict),
which makes them deterministic and straightforward to unit test.
They intentionally avoid I/O and external state.
"""
from typing import Iterable, Dict, List
import statistics
from datetime import date

def filter_records(records: Iterable[dict], *, country: str | None,
                   start: date | None, end: date | None) -> List[dict]:
    """Filter records by country and optional  date range.

    Returns records sorted by `date`.
    """
    out: List[dict] = []
    for r in records:
        if country and r.get('location') != country:
            continue
        d = r.get('date')
        if start and d < start:
            continue
        if end and d > end:
            continue
        out.append(r)
    return sorted(out, key=lambda x: x['date'])

def summarize_numeric(records: Iterable[dict], field: str) -> Dict[str, float]:
    """Compute count/min/mean/max for a numeric field.

    Non-numeric and missing values are ignored. Empty inputs yield zeros.
    """
    vals: List[float] = []
    for r in records:
        v = r.get(field)
        if isinstance(v, (int, float)):
            vals.append(float(v))
    if not vals:
        return {"count": 0, "min": 0.0, "mean": 0.0, "max": 0.0}
    return {
        "count": float(len(vals)),
        "min": float(min(vals)),
        "mean": float(statistics.fmean(vals)),
        "max": float(max(vals)),
    }
