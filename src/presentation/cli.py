from __future__ import annotations
import argparse
from datetime import datetime
from pathlib import Path
import logging
from typing import Optional

from ..infrastructure.data_sources.csv_source import CsvVaccinationSource
from ..infrastructure.repository import SqliteRepository
from ..domain.services import filter_records, summarize_numeric
from ..presentation.charts import plot_trend
from ..logging_conf import setup_logging
from ..config import DEFAULT_DB_PATH


def _parse_date(s: Optional[str]):
    return datetime.fromisoformat(s).date() if s else None


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=(
            "Public Health Data Insights Tool: load OWID vaccination CSV, "
            "clean, store in SQLite, filter, summarize, and plot."
        )
    )
    p.add_argument("--db", type=Path, default=DEFAULT_DB_PATH, help="SQLite DB path")
    p.add_argument("--log", type=Path, default=None, help="Optional log file path")

    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("load-csv", help="Load a vaccination CSV into the database")
    s.add_argument("path", type=Path, help="Path to vaccinations.csv")

    s = sub.add_parser("summary", help="Summarize metrics for a country/date range")
    s.add_argument("--country", required=True)
    s.add_argument("--start", default=None)
    s.add_argument("--end", default=None)

    s = sub.add_parser("plot", help="Create a trend plot for a field")
    s.add_argument("--country", required=True)
    s.add_argument("--field", default="people_fully_vaccinated_per_hundred")
    s.add_argument("--start", default=None)
    s.add_argument("--end", default=None)
    s.add_argument("--out", type=Path, default=Path("plot.png"))

    s = sub.add_parser("export", help="Export filtered rows to CSV")
    s.add_argument("--country", required=True)
    s.add_argument("--start", default=None)
    s.add_argument("--end", default=None)
    s.add_argument("--out", type=Path, default=Path("export.csv"))

    sub.add_parser("countries", help="List countries available in DB")

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    setup_logging(args.log)
    log = logging.getLogger("cli")

    repo = SqliteRepository(args.db)

    if args.cmd == "load-csv":
        src = CsvVaccinationSource(str(args.path))
        rows = list(src.load())
        inserted = repo.insert_many(rows)
        log.info("Inserted %s rows into %s", inserted, args.db)
        return 0

    if args.cmd == "countries":
        for c in repo.list_countries():
            print(c)
        return 0

    if args.cmd in {"summary", "plot", "export"}:
        start_d = _parse_date(args.start)
        end_d = _parse_date(args.end)
        rows = [dict(r) for r in repo.query(country=args.country, start=args.start, end=args.end)]
        if not rows:
            log.info("No rows match the criteria.")
            return 0

        if args.cmd == "summary":
            filtered = filter_records(rows, country=args.country, start=start_d, end=end_d)
            for field in (
                "daily_vaccinations",
                "people_vaccinated_per_hundred",
                "people_fully_vaccinated_per_hundred",
                "total_boosters_per_hundred",
            ):
                stats = summarize_numeric(filtered, field)
                print(field, stats)
            return 0

        if args.cmd == "plot":
            filtered = filter_records(rows, country=args.country, start=start_d, end=end_d)
            out = plot_trend(
                filtered,
                x_field="date",
                y_field=args.field,
                title=f"{args.country}: {args.field.replace('_',' ').title()} over time",
                out_path=args.out,
            )
            log.info("Saved plot to %s", out)
            return 0

        if args.cmd == "export":
            filtered = filter_records(rows, country=args.country, start=start_d, end=end_d)
            import csv
            args.out.parent.mkdir(parents=True, exist_ok=True)
            with args.out.open("w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=list(filtered[0].keys()))
                w.writeheader()
                w.writerows(filtered)
            log.info("Exported %s rows to %s", len(filtered), args.out)
            return 0

    return 0
