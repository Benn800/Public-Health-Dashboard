# src/infrastructure/data_sources/csv_source.py
from __future__ import annotations
from typing import Iterable, Dict
import logging
import pandas as pd

from .base import DataSource

NUMERIC_COLS = [
    "total_vaccinations", "people_vaccinated", "people_fully_vaccinated", "total_boosters",
    "daily_vaccinations_raw", "daily_vaccinations", "total_vaccinations_per_hundred",
    "people_vaccinated_per_hundred", "people_fully_vaccinated_per_hundred", "total_boosters_per_hundred",
    "daily_vaccinations_per_million", "daily_people_vaccinated", "daily_people_vaccinated_per_hundred",
]


class CsvVaccinationSource(DataSource):
    def __init__(self, path: str):
        self.path = path

    def load(self) -> Iterable[Dict]:
        log = logging.getLogger("csv")

        # 1) Announce which CSV path we’re loading
        log.info("Loading CSV: %s", self.path)

        # 2) Read the CSV
        df = pd.read_csv(self.path, low_memory=False)

        # 3) Log columns and row count BEFORE cleaning
        log.debug("CSV columns: %s", list(df.columns))
        log.info("CSV rows read: %d (before cleaning)", len(df))

        # 4) Coerce types
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
        for col in NUMERIC_COLS:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # 5) Essential cleaning (drop invalid location/date)
        df = df.dropna(subset=["location", "date"])

        # 6) Log row count AFTER cleaning
        log.info("CSV rows kept: %d (after cleaning)", len(df))

        # 7) Keep only columns we use, but tolerate missing ones
        keep = [
            "location", "iso_code", "date", "total_vaccinations", "people_vaccinated",
            "people_fully_vaccinated", "total_boosters", "daily_vaccinations",
            "total_vaccinations_per_hundred", "people_vaccinated_per_hundred",
            "people_fully_vaccinated_per_hundred", "total_boosters_per_hundred",
        ]
        existing = [c for c in keep if c in df.columns]

        # 8) Yield normalized dict rows (fill non-existing keys with None)
        for _, row in df[existing].iterrows():
            out = {}
            for k in keep:
                if k in row.index:
                    v = row[k]
                    out[k] = (None if pd.isna(v) else v)
                else:
                    out[k] = None
            yield out
