from __future__ import annotations
"""SQLite repository for vaccination statistics.

Responsibilities:
    - Ensure schema and indexes exist on first use
    - Insert normalized rows with idempotency (INSERT OR IGNORE)
    - Query by filters with typed date conversion
    - Utility operations: list_countries; (update/delete kept minimal)

Design choices:
    - Use sqlite3 directly to reduce dependencies and keep behavior explicit.
    - Store dates as ISO strings in DB; parse back to date objects on read.
    - Unique constraint on (location, iso_code, date) protects data integrity.
"""
import logging
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
        """Bulk insert rows using INSERT OR IGNORE.

        - Dates are converted to ISO strings to avoid adapter ambiguity.
        - Returns number of accepted rows; ignored rows do not count.
        """
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

        # Convert date to ISO strings explicitly to avoid adapter differences.
        converted_rows = []
        for r in rows:
            rr = dict(r)
            if rr.get("date") and isinstance(rr["date"], date):
                rr["date"] = rr["date"].isoformat()
            converted_rows.append(rr)

        with self._connect() as con:
            cur = con.executemany(sql, converted_rows)
            rowcount = cur.rowcount or 0

        # ✅ Add repo logs here
        log = logging.getLogger("repo")
        log.info("Inserted rows (accepted): %d", rowcount)

        return rowcount

    def query(
        self, *, country: Optional[str] = None,
        start: Optional[str] = None, end: Optional[str] = None
    ) -> Iterator[Dict[str, Any]]:
        """Query rows with optional filters and yield dicts.

        Inputs `start`/`end` are ISO strings for consistency with storage;
        outputs have `date` coerced back to datetime.date when possible.
        """
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

        out: list[Dict[str, Any]] = []
        with self._connect() as con:
            for row in con.execute(sql, params):
                d = dict(row)
                if d.get("date"):
                    try:
                        d["date"] = datetime.fromisoformat(d["date"]).date()
                    except Exception:
                        # leave as-is if parsing fails
                        pass
                out.append(d)

        # Log useful query metadata 
        log = logging.getLogger("repo")
        n_rows = len(out)
        log.debug("Query(country=%s, start=%s, end=%s) -> %d rows", country, start, end, n_rows)

        # Yield after logging
        for d in out:
            yield d

    def update_field(self, *, country: str, date: str, field: str, value: Any) -> int:
        """Update a single numeric field for a specific (country, date).

        Note: In typical research workflows data is treated as immutable; this
        helper exists for test coverage and rare correction scenarios.
        """
        assert field in {
            "total_vaccinations", "people_vaccinated", "people_fully_vaccinated",
            "total_boosters", "daily_vaccinations",
            "total_vaccinations_per_hundred", "people_vaccinated_per_hundred",
            "people_fully_vaccinated_per_hundred", "total_boosters_per_hundred",
        }, f"Unsupported field: {field}"

        sql = f"UPDATE vaccination_stats SET {field} = :value WHERE location=:c AND date=:d"
        with self._connect() as con:
            cur = con.execute(sql, {"value": value, "c": country, "d": date})
            rowcount = cur.rowcount or 0

        # Optional: log updates at DEBUG (less noisy)
        logging.getLogger("repo").debug(
            "Update field=%s for country=%s date=%s -> %d row(s)",
            field, country, date, rowcount
        )
        return rowcount

    def delete_row(self, *, country: str, date: str) -> int:
        """Delete a row by (country, date). Used primarily in tests.

        Prefer reloading corrected source data over destructive edits in
        production workflows to preserve provenance.
        """
        with self._connect() as con:
            cur = con.execute(
                "DELETE FROM vaccination_stats WHERE location=:c AND date=:d",
                {"c": country, "d": date},
            )
            rowcount = cur.rowcount or 0

        # Optional: log deletes at DEBUG
        logging.getLogger("repo").debug(
            "Delete country=%s date=%s -> %d row(s)", country, date, rowcount
        )
        return rowcount

    def list_countries(self) -> list[str]:
        """Return distinct locations sorted alphabetically."""
        with self._connect() as con:
            rows = con.execute(
                "SELECT DISTINCT location FROM vaccination_stats ORDER BY location"
            ).fetchall()
        countries = [r[0] for r in rows]

        # Optional: log list size at DEBUG
        logging.getLogger("repo").debug("list_countries -> %d", len(countries))
        return countries
