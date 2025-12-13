from pathlib import Path
from task1_public_health.src.infrastructure.data_sources.csv_source import CsvVaccinationSource

def test_csv_source_normalizes_and_yields(tmp_path: Path):
    csv = tmp_path / "mini.csv"
    csv.write_text(
        "location,iso_code,date,people_fully_vaccinated_per_hundred\n"
        "UK,GBR,2021-01-01,0.5\nUK,GBR,2021-01-02,0.7\n"
    )
    src = CsvVaccinationSource(str(csv))
    rows = list(src.load())
    assert rows[0]["date"].isoformat() == "2021-01-01"
    assert isinstance(rows[1]["people_fully_vaccinated_per_hundred"], float)
