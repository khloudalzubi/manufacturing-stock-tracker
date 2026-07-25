from dataclasses import dataclass
from pathlib import Path
import logging

from manufacturing_stock_tracker.api import fetch_quotes
from manufacturing_stock_tracker.process import quote_rows, save_csv, save_json, summarize

LOGGER = logging.getLogger(__name__)


@dataclass
class CollectionBatch:
    symbols: list[str]
    summary: dict
    rows: list[dict]
    raw_path: Path
    processed_path: Path
    source: str


def collect_symbols(
    symbols: list[str],
    api_key: str,
    data_dir: Path = Path("data"),
    fetcher=fetch_quotes,
) -> CollectionBatch:
    raw_path = data_dir / "raw" / "twelve_data_watchlist_quotes_raw.json"
    processed_path = data_dir / "processed" / "manufacturing_watchlist_quotes.csv"

    LOGGER.info("Collecting Twelve Data quote data for %s", ",".join(symbols))
    payload = fetcher(symbols, api_key)
    save_json(payload, raw_path)
    rows = quote_rows(payload)
    save_csv(rows, processed_path)
    summary = summarize(rows)
    LOGGER.info("Saved %s quote rows to %s", len(rows), processed_path)

    return CollectionBatch(
        symbols=symbols,
        summary=summary,
        rows=rows,
        raw_path=raw_path,
        processed_path=processed_path,
        source="api",
    )
