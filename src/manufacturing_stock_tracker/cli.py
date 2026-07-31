"""Command-line interface for collecting quote and historical momentum data."""

import argparse
import os
from pathlib import Path

from dotenv import load_dotenv

from manufacturing_stock_tracker.api import TwelveDataError
from manufacturing_stock_tracker.logging_config import configure_logging
from manufacturing_stock_tracker.pipeline import collect_history, collect_symbols
from manufacturing_stock_tracker.process import StockDataError, parse_symbols, validate_symbol

DEFAULT_SYMBOLS = "CAT,DE,HON,GE,MMM"


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI argument parser for quote and history collection."""
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
        "--history",
        action="store_true",
        help="Collect daily historical prices and calculate momentum instead of current quotes.",
    )
    parser.add_argument(
        "--history-outputsize",
        type=int,
        default=30,
        help="Number of daily historical observations to request per symbol. Defaults to 30.",
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
    """Return a cleaned single symbol or watchlist from CLI arguments."""
    if symbol:
        return [validate_symbol(symbol)]
    return parse_symbols(symbols)


def _format_optional_percent(value: float | None) -> str:
    """Format optional percentages for readable command output."""
    return "n/a" if value is None else f"{value:.2f}%"


def main() -> None:
    """Run the CLI, collect requested data, and print a concise summary."""
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
        if args.history:
            batch = collect_history(symbols, api_key, Path("data"), args.history_outputsize)
            _print_history_summary(batch)
        else:
            batch = collect_symbols(symbols, api_key, Path("data"))
            _print_quote_summary(batch)
    except TwelveDataError as exc:
        raise SystemExit(f"Twelve Data error: {exc}") from exc
    except StockDataError as exc:
        raise SystemExit(f"Stock data error: {exc}") from exc


def _print_quote_summary(batch) -> None:
    """Print a summary for current quote collection results."""
    summary = batch.summary
    print(f"Symbols processed: {', '.join(batch.symbols)}")
    print(f"Rows saved: {summary['row_count']}")
    print(f"Average price: {summary['average_price']:.2f}")
    print(f"Average percent change: {_format_optional_percent(summary['average_percent_change'])}")
    print(f"Highest price symbol: {summary['highest_price_symbol']}")
    print(f"Lowest price symbol: {summary['lowest_price_symbol']}")
    print(
        "Top gainer: "
        f"{summary['top_gainer_symbol']} "
        f"({_format_optional_percent(summary['top_gainer_percent_change'])})"
    )
    print(
        "Top decliner: "
        f"{summary['top_decliner_symbol']} "
        f"({_format_optional_percent(summary['top_decliner_percent_change'])})"
    )
    print(
        "Watchlist direction: "
        f"{summary['positive_count']} up, "
        f"{summary['negative_count']} down, "
        f"{summary['flat_count']} flat"
    )
    print(f"Raw response: {batch.raw_path}")
    print(f"Processed data: {batch.processed_path}")


def _print_history_summary(batch) -> None:
    """Print a summary for historical momentum collection results."""
    summary = batch.summary
    print(f"Historical symbols processed: {', '.join(batch.symbols)}")
    print(f"Historical rows saved: {len(batch.rows)}")
    print(f"Average period return: {summary['average_return_percent']:.2f}%")
    print(
        "Strongest performer: "
        f"{summary['strongest_symbol']} ({summary['strongest_return_percent']:.2f}%)"
    )
    print(
        "Weakest performer: "
        f"{summary['weakest_symbol']} ({summary['weakest_return_percent']:.2f}%)"
    )
    print(
        "Momentum direction: "
        f"{summary['positive_count']} positive, "
        f"{summary['negative_count']} negative, "
        f"{summary['flat_count']} flat"
    )
    print(f"Raw historical response: {batch.raw_path}")
    print(f"Processed historical data: {batch.processed_path}")
    print(f"Momentum summary data: {batch.momentum_path}")
