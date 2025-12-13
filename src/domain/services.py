from __future__ import annotations
from typing import Iterable, Dict, List
import statistics
from datetime import date

def filter_records(records: Iterable[dict], *, country: str | None,
                   start: date | None, end: date | None) -> List[dict]:
    # Pure filter by country and optional date range
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
    # Return count/min/mean/max for numeric field
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
