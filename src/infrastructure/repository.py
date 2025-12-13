from __future__ import annotations
import sqlite3
from pathlib import Path
from typing import Iterable, Dict, Any, Iterator, Optional
from datetime import datetime, date

SCHEMA = '''
CREATE TABLE IF NOT EXISTS vaccination_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location TEXT NOT NULL,
    iso_code TEXT NOT NULL,
    date TEXT NOT NULL,
    total_vaccinations INTEGER,
    people_vaccinated INTEGER,
    people_fully_vaccinated INTEGER,
    total_boosters INTEGER,
    daily_vaccinations INTEGER,
    total_vaccinations_per_hundred REAL,
    people_vaccinated_per_hundred REAL,
    people_fully_vaccinated_per_hundred REAL,
    total_boosters_per_hundred REAL,
    UNIQUE(location, iso_code, date)
);
'''

INDEXES = (
    "CREATE INDEX IF NOT EXISTS ix_country_date ON vaccination_stats(location, date);",
)


class SqliteRepository:
    def __init__(self, db_path: Path | str):
        self.db_path = str(db_path)
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        return con

    def _ensure_schema(self) -> None:
        with self._connect() as con:
            con.executescript(SCHEMA)
            for ddl in INDEXES:
                con.execute(ddl)

    def insert_many(self, rows: Iterable[Dict[str, Any]]) -> int:
        sql = (
            "INSERT OR IGNORE INTO vaccination_stats ("
            "location, iso_code, date,"
            " total_vaccinations, people_vaccinated, people_fully_vaccinated,"
            " total_boosters, daily_vaccinations,"
            " total_vaccinations_per_hundred, people_vaccinated_per_hundred,"
            " people_fully_vaccinated_per_hundred, total_boosters_per_hundred"
            ") VALUES ("
            ":location, :iso_code, :date,"
            " :total_vaccinations, :people_vaccinated, :people_fully_vaccinated,"
            " :total_boosters, :daily_vaccinations,"
            " :total_vaccinations_per_hundred, :people_vaccinated_per_hundred,"
            " :people_fully_vaccinated_per_hundred, :total_boosters_per_hundred"
            ");"
        )
        
        """convert date to ISO strings explicitly to avoid deprecation warnings 
        and platform differences in adapters."""
        converted_rows = []
        for r in rows:
            # make a shallow copy so we don't mutate caller data
            rr = dict(r)
            if rr.get("date") and isinstance(rr["date"], date):
                rr["date"] = rr["date"].isoformat()
            converted_rows.append(rr)
        with self._connect() as con:
            cur = con.executemany(sql, converted_rows)
            return cur.rowcount or 0

    def query(self, *, country: Optional[str] = None,
              start: Optional[str] = None, end: Optional[str] = None) -> Iterator[sqlite3.Row]:
        where = []
        params: Dict[str, Any] = {}
        if country:
            where.append("location = :country")
            params["country"] = country
        if start:
            where.append("date >= :start")
            params["start"] = start
        if end:
            where.append("date <= :end")
            params["end"] = end
        sql = "SELECT * FROM vaccination_stats"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY date ASC"
        with self._connect() as con:
            for row in con.execute(sql, params):
                # convert sqlite Row to dict and parse date field into date object
                d = dict(row)
                if d.get("date"):
                    try:
                        d["date"] = datetime.fromisoformat(d["date"]).date()
                    except Exception:
                        # leave as-is if parsing fails
                        pass
                yield d

    def update_field(self, *, country: str, date: str, field: str, value: Any) -> int:
        assert field in {
            "total_vaccinations","people_vaccinated","people_fully_vaccinated",
            "total_boosters","daily_vaccinations",
            "total_vaccinations_per_hundred","people_vaccinated_per_hundred",
            "people_fully_vaccinated_per_hundred","total_boosters_per_hundred",
        }, f"Unsupported field: {field}"
        sql = f"UPDATE vaccination_stats SET {field} = :value WHERE location=:c AND date=:d"
        with self._connect() as con:
            cur = con.execute(sql, {"value": value, "c": country, "d": date})
            return cur.rowcount or 0

    def delete_row(self, *, country: str, date: str) -> int:
        with self._connect() as con:
            cur = con.execute(
                "DELETE FROM vaccination_stats WHERE location=:c AND date=:d",
                {"c": country, "d": date},
            )
            return cur.rowcount or 0

    def list_countries(self) -> list[str]:
        with self._connect() as con:
            rows = con.execute("SELECT DISTINCT location FROM vaccination_stats ORDER BY location").fetchall()
            return [r[0] for r in rows]
