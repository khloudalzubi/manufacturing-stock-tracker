import argparse
import os
from pathlib import Path

from dotenv import load_dotenv

from manufacturing_stock_tracker.api import TwelveDataError
from manufacturing_stock_tracker.logging_config import configure_logging
from manufacturing_stock_tracker.pipeline import collect_symbols
from manufacturing_stock_tracker.process import StockDataError, parse_symbols, validate_symbol

DEFAULT_SYMBOLS = "CAT,DE,HON,GE,MMM"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Collect and process Twelve Data quote data for manufacturing companies."
    )
    parser.add_argument(
        "--symbol",
        help="Single stock ticker symbol to fetch, such as CAT.",
    )
    parser.add_argument(
        "--symbols",
        default=DEFAULT_SYMBOLS,
        help=f"Comma-separated ticker symbols to fetch as a watchlist. Defaults to {DEFAULT_SYMBOLS}.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Console logging level. Defaults to INFO.",
    )
    parser.add_argument(
        "--log-file",
        help="Optional path for writing logs to a file, such as logs/tracker.log.",
    )
    return parser


def selected_symbols(symbol: str | None, symbols: str) -> list[str]:
    if symbol:
        return [validate_symbol(symbol)]
    return parse_symbols(symbols)


def main() -> None:
    load_dotenv()
    parser = build_parser()
    args = parser.parse_args()
    configure_logging(args.log_level, args.log_file)

    try:
        symbols = selected_symbols(args.symbol, args.symbols)
    except StockDataError as exc:
        raise SystemExit(f"Invalid ticker symbol: {exc}") from exc

    api_key = os.environ.get("TWELVE_DATA_API_KEY")

    if not api_key:
        raise SystemExit("Missing TWELVE_DATA_API_KEY. Copy .env.example to .env and add your API key.")

    try:
        batch = collect_symbols(symbols, api_key, Path("data"))
    except TwelveDataError as exc:
        raise SystemExit(f"Twelve Data error: {exc}") from exc
    except StockDataError as exc:
        raise SystemExit(f"Stock data error: {exc}") from exc

    summary = batch.summary
    print(f"Symbols processed: {', '.join(batch.symbols)}")
    print(f"Rows saved: {summary['row_count']}")
    print(f"Average price: {summary['average_price']:.2f}")
    print(f"Highest price symbol: {summary['highest_price_symbol']}")
    print(f"Lowest price symbol: {summary['lowest_price_symbol']}")
    if summary["average_percent_change"] is not None:
        print(f"Average percent change: {summary['average_percent_change']:.2f}%")
    print(f"Raw response: {batch.raw_path}")
    print(f"Processed data: {batch.processed_path}")
