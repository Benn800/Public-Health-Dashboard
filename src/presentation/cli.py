from __future__ import annotations
"""Command-line interface (CLI)

This module wires user commands to the underlying architecture:
    - load-csv: ingest and normalize OWID CSV into SQLite
    - countries: list distinct locations available
    - summary: compute simple descriptive stats on key fields
    - plot: render a time-series trend to a PNG file
    - export: write filtered rows to CSV for downstream analysis

Design notes:
    - Parsing is done with argparse for minimal deps and clarity.
    - Logging is file-based (see logging_conf) to keep CLI output clean.
    - Domain services remain pure; repository handles persistence.
"""
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
    """Best-effort ISO date parsing.

    Accepts YYYY-MM-DD strings and returns datetime.date or None.
    Errors propagate to caller where they are handled.
    """
    return datetime.fromisoformat(s).date() if s else None


def build_parser() -> argparse.ArgumentParser:
    """Construct the CLI parser with all subcommands and options."""
    p = argparse.ArgumentParser(
        description=(
            "Public Health Data Insights Tool: load OWID vaccination CSV, "
            "clean, store in SQLite, filter, summarize, and plot."
        )
    )
    p.add_argument("--db", type=Path, default=DEFAULT_DB_PATH, help="SQLite DB path")
    p.add_argument("--log", type=Path, default=None, help="Optional log file path")

    sub = p.add_subparsers(dest="cmd", required=True)

    # Ingestion: one-shot CSV -> SQLite load
    s = sub.add_parser("load-csv", help="Load a vaccination CSV into the database")
    s.add_argument("path", type=Path, help="Path to vaccinations.csv")

    # Descriptive statistics on selected fields for a filtered slice
    s = sub.add_parser("summary", help="Summarize metrics for a country/date range")
    s.add_argument("--country", required=True)
    s.add_argument("--start", default=None)
    s.add_argument("--end", default=None)

    # Plot time-series for a numeric field into a PNG
    s = sub.add_parser("plot", help="Create a trend plot for a field")
    s.add_argument("--country", required=True)
    s.add_argument("--field", default="people_fully_vaccinated_per_hundred")
    s.add_argument("--start", default=None)
    s.add_argument("--end", default=None)
    s.add_argument("--out", type=Path, default=Path("plot.png"))

    # Export filtered rows for downstream analysis or sharing
    s = sub.add_parser("export", help="Export filtered rows to CSV")
    s.add_argument("--country", required=True)
    s.add_argument("--start", default=None)
    s.add_argument("--end", default=None)
    s.add_argument("--out", type=Path, default=Path("export.csv"))

    sub.add_parser("countries", help="List countries available in DB")

    return p


def main(argv: list[str] | None = None) -> int:
    """Entry point for CLI; returns process exit code.

    Each subcommand is protected with try/except to ensure
    informative logs and non-zero exit codes on failures.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    setup_logging(args.log)
    log = logging.getLogger("cli")

    repo = SqliteRepository(args.db)

    if args.cmd == "load-csv":
        try:
            src = CsvVaccinationSource(str(args.path))
            rows = list(src.load())
            inserted = repo.insert_many(rows)
            log.info("Inserted %s rows into %s", inserted, args.db)
            return 0
        except Exception:
            log.exception("CMD failed: %s", args.cmd)
            return 1


    if args.cmd == "countries":
        try:
            for c in repo.list_countries():
                print(c)
            return 0
        except Exception:
            log.exception("CMD failed: %s", args.cmd)
            return 1

    if args.cmd in {"summary", "plot", "export"}:
        try:
            start_d = _parse_date(args.start)
            end_d = _parse_date(args.end)
            rows = [dict(r) for r in repo.query(country=args.country, start=args.start, end=args.end)]
            if not rows:
                log.info("No rows match the criteria.")
                return 0
        except Exception:
            log.exception("CMD failed: %s", args.cmd)
            return 1    

        if args.cmd == "summary":
            try:
                filtered = filter_records(rows, country=args.country, start=start_d, end=end_d)
                for field in (
                    "daily_vaccinations",
                    "people_vaccinated_per_hundred",
                    "people_fully_vaccinated_per_hundred",
                    "total_boosters_per_hundred",
                ):
                    stats = summarize_numeric(filtered, field)
                    print(field, stats)
                
                log.info("CMD start: %s", args.cmd)
                # For filter-based commands:
                log.info("Filters: country=%s start=%s end=%s", args.country, args.start, args.end)
                # After success:
                log.info("CMD done: %s", args.cmd)
                return 0
            except Exception:
                log.exception("CMD failed: %s", args.cmd)
                return 1 

        if args.cmd == "plot":
            try:            
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
            except Exception:
                log.exception("CMD failed: %s", args.cmd)
                return 1             

        if args.cmd == "export":
            try:    
                filtered = filter_records(rows, country=args.country, start=start_d, end=end_d)
                import csv
                args.out.parent.mkdir(parents=True, exist_ok=True)
                with args.out.open("w", newline="", encoding="utf-8") as f:
                    w = csv.DictWriter(f, fieldnames=list(filtered[0].keys()))
                    w.writeheader()
                    w.writerows(filtered)
                log.info("Exported %s rows to %s", len(filtered), args.out)
                return 0
            except Exception:
                log.exception("CMD failed: %s", args.cmd)
                return 1 

    return 0
