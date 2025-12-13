from pathlib import Path
from datetime import date
import sqlite3

from src.infrastructure.repository import SqliteRepository

def test_repository_insert_query_update_delete(tmp_path: Path):
    db = tmp_path / "t.db"
    repo = SqliteRepository(db)
    repo.insert_many([{
        "location": "UK", "iso_code": "GBR", "date": "2021-01-01",
        "total_vaccinations": 10, "people_vaccinated": 5, "people_fully_vaccinated": 3,
        "total_boosters": None, "daily_vaccinations": 10,
        "total_vaccinations_per_hundred": 0.01, "people_vaccinated_per_hundred": 0.005,
        "people_fully_vaccinated_per_hundred": 0.003, "total_boosters_per_hundred": None,
    }])
    r = list(repo.query(country="UK"))
    assert r and r[0]["location"] == "UK"
    assert repo.update_field(country="UK", date="2021-01-01", field="daily_vaccinations", value=99) >= 0
    assert repo.delete_row(country="UK", date="2021-01-01") == 1


def test_insert_many_converts_date_to_iso(tmp_path: Path):
    db = tmp_path / "t2.db"
    repo = SqliteRepository(db)
    repo.insert_many([{
        "location": "UK", "iso_code": "GBR", "date": date(2021, 1, 2),
        "total_vaccinations": None, "people_vaccinated": None, "people_fully_vaccinated": None,
        "total_boosters": None, "daily_vaccinations": None,
        "total_vaccinations_per_hundred": None, "people_vaccinated_per_hundred": None,
        "people_fully_vaccinated_per_hundred": None, "total_boosters_per_hundred": None,
    }])

    # Raw DB value should be ISO string
    with sqlite3.connect(db) as con:
        raw_date = con.execute("SELECT date FROM vaccination_stats").fetchone()[0]
    assert raw_date == "2021-01-02"

    # Public query should still return datetime.date
    rows = list(repo.query(country="UK"))
    assert rows and isinstance(rows[0]["date"], date)
    assert rows[0]["date"].isoformat() == "2021-01-02"
