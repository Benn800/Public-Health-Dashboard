
# tests/test_cli_smoke.py
from __future__ import annotations
from pathlib import Path
from src.presentation.cli import main

def test_cli_load_and_list(tmp_path: Path):
    # Arrange: dedicated DB and mini CSV in a temp folder
    db = tmp_path / "smoke.db"
    csv = tmp_path / "mini.csv"
    csv.write_text(
        "location,iso_code,date,people_fully_vaccinated_per_hundred\n"
        "UK,GBR,2021-01-01,0.5\n"
    )

    # Act: load the CSV
    assert main(["--db", str(db), "load-csv", str(csv)]) == 0

    # Act: list countries (stdout is printed; we only check it doesn’t crash)
    assert main(["--db", str(db), "countries"]) == 0

def test_cli_summary_plot_export(tmp_path: Path):
    db = tmp_path / "smoke.db"
    csv = tmp_path / "mini.csv"
    csv.write_text(
        "location,iso_code,date,people_fully_vaccinated_per_hundred\n"
        "UK,GBR,2021-01-01,0.5\n"
        "UK,GBR,2021-01-02,0.7\n"
    )
    # Load first
    assert main(["--db", str(db), "load-csv", str(csv)]) == 0

    # Summary
    assert main(["--db", str(db), "summary", "--country", "UK", "--start", "2021-01-01"]) == 0

    # Plot
    out_png = tmp_path / "uk_trend.png"
    assert main([
        "--db", str(db), "plot",
        "--country", "UK",
        "--field", "people_fully_vaccinated_per_hundred",
        "--out", str(out_png)
    ]) == 0
    assert out_png.exists()

    # Export
    out_csv = tmp_path / "uk_subset.csv"
    assert main([
        "--db", str(db), "export",
        "--country", "UK",
        "--start", "2021-01-01",
        "--out", str(out_csv)
    ]) == 0
    assert out_csv.exists()
