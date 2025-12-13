from __future__ import annotations
from typing import Iterable, Dict
import pandas as pd

from .base import DataSource

NUMERIC_COLS = [
    "total_vaccinations","people_vaccinated","people_fully_vaccinated","total_boosters",
    "daily_vaccinations_raw","daily_vaccinations","total_vaccinations_per_hundred",
    "people_vaccinated_per_hundred","people_fully_vaccinated_per_hundred","total_boosters_per_hundred",
    "daily_vaccinations_per_million","daily_people_vaccinated","daily_people_vaccinated_per_hundred",
]


class CsvVaccinationSource(DataSource):
    def __init__(self, path: str):
        self.path = path

    def load(self) -> Iterable[Dict]:
        df = pd.read_csv(self.path, low_memory=False)
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
        for col in NUMERIC_COLS:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        df = df.dropna(subset=["location", "date"])  # essential fields
        keep = [
            "location","iso_code","date","total_vaccinations","people_vaccinated",
            "people_fully_vaccinated","total_boosters","daily_vaccinations",
            "total_vaccinations_per_hundred","people_vaccinated_per_hundred",
            "people_fully_vaccinated_per_hundred","total_boosters_per_hundred",
        ]
        # only select columns that are present and yield normalized rows
        existing = [c for c in keep if c in df.columns]
        for _, row in df[existing].iterrows():
            out = {}
            for k in keep:
                if k in row.index:
                    v = row[k]
                    out[k] = (None if pd.isna(v) else v)
                else:
                    out[k] = None
            yield out
