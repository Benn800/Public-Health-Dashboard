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