from pathlib import Path
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
