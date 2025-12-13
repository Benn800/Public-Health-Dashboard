
from datetime import date
from src.domain.services import *

def test_filter_records_by_country_and_date():
    rows = [
        {"location": "UK", "date": date(2021, 1, 1), "v": 1},
        {"location": "UK", "date": date(2021, 1, 2), "v": 2},
        {"location": "FR", "date": date(2021, 1, 2), "v": 3},
    ]
    out = filter_records(rows, country="UK", start=date(2021,1,2), end=None)
    assert len(out) == 1 and out[0]["v"] == 2

def test_summarize_numeric_handles_empty():
    assert summarize_numeric([], "x") == {"count": 0, "min": 0.0, "mean": 0.0, "max": 0.0}    


