"""Shared collection workflows used by the CLI, dashboard, and report."""

from dataclasses import dataclass
from pathlib import Path
import logging

from manufacturing_stock_tracker.api import fetch_quotes, fetch_time_series
from manufacturing_stock_tracker.process import (
    ensure_requested_symbols_returned,
    historical_rows,
    historical_summary,
    momentum_rows,
    quote_rows,
    save_csv,
    save_json,
    summarize,
)
from manufacturing_stock_tracker.storage import save_quote_run

LOGGER = logging.getLogger(__name__)


@dataclass
class CollectionBatch:
    """Outputs from one current-quote collection run."""

    symbols: list[str]
    summary: dict
    rows: list[dict]
    raw_path: Path
    processed_path: Path
    source: str
    db_path: Path | None = None
    db_run_id: int | None = None


@dataclass
class HistoricalBatch:
    """Outputs from one historical momentum collection run."""

    symbols: list[str]
    summary: dict
    rows: list[dict]
    momentum: list[dict]
    raw_path: Path
    processed_path: Path
    momentum_path: Path
    source: str


def collect_symbols(
    symbols: list[str],
    api_key: str,
    data_dir: Path = Path("data"),
    fetcher=fetch_quotes,
    db_path: Path | None = None,
) -> CollectionBatch:
    """Collect current quotes, save raw/processed files, and optionally persist SQLite history."""
    raw_path = data_dir / "raw" / "twelve_data_watchlist_quotes_raw.json"
    processed_path = data_dir / "processed" / "manufacturing_watchlist_quotes.csv"

    LOGGER.info("Collecting Twelve Data quote data for %s", ",".join(symbols))
    payload = fetcher(symbols, api_key)
    save_json(payload, raw_path)
    rows = quote_rows(payload)
    ensure_requested_symbols_returned(symbols, rows)
    save_csv(rows, processed_path)
    summary = summarize(rows)
    LOGGER.info("Saved %s quote rows to %s", len(rows), processed_path)

    db_run_id = None
    if db_path is not None:
        db_run_id = save_quote_run(rows, summary, symbols, db_path)
        LOGGER.info("Saved quote run %s to %s", db_run_id, db_path)

    return CollectionBatch(
        symbols=symbols,
        summary=summary,
        rows=rows,
        raw_path=raw_path,
        processed_path=processed_path,
        source="api",
        db_path=db_path,
        db_run_id=db_run_id,
    )


def collect_history(
    symbols: list[str],
    api_key: str,
    data_dir: Path = Path("data"),
    outputsize: int = 30,
    fetcher=fetch_time_series,
) -> HistoricalBatch:
    """Collect daily history, save evidence files, and calculate momentum."""
    raw_path = data_dir / "raw" / "twelve_data_watchlist_history_raw.json"
    processed_path = data_dir / "processed" / "manufacturing_watchlist_history.csv"
    momentum_path = data_dir / "processed" / "manufacturing_watchlist_momentum.csv"

    LOGGER.info("Collecting Twelve Data historical data for %s", ",".join(symbols))
    payload = fetcher(symbols, api_key, "1day", outputsize)
    save_json(payload, raw_path)
    rows = historical_rows(payload)
    ensure_requested_symbols_returned(symbols, rows)
    momentum = momentum_rows(rows)
    summary = historical_summary(momentum)
    save_csv(rows, processed_path)
    save_csv(momentum, momentum_path)
    LOGGER.info("Saved %s historical rows to %s", len(rows), processed_path)

    return HistoricalBatch(
        symbols=symbols,
        summary=summary,
        rows=rows,
        momentum=momentum,
        raw_path=raw_path,
        processed_path=processed_path,
        momentum_path=momentum_path,
        source="api",
    )
