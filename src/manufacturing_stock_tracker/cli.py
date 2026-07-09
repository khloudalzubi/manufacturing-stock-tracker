import argparse
import os
from pathlib import Path

from dotenv import load_dotenv

from manufacturing_stock_tracker.api import AlphaVantageError, fetch_daily_prices
from manufacturing_stock_tracker.process import daily_rows, save_csv, save_json, summarize


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Collect and process Alpha Vantage stock data for manufacturing companies."
    )
    parser.add_argument(
        "--symbol",
        default="CAT",
        help="Stock ticker symbol to fetch. Defaults to CAT.",
    )
    return parser


def main() -> None:
    load_dotenv()
    parser = build_parser()
    args = parser.parse_args()
    symbol = args.symbol.upper()
    api_key = os.environ.get("ALPHA_VANTAGE_API_KEY")

    if not api_key:
        raise SystemExit(
            "Missing ALPHA_VANTAGE_API_KEY. Copy .env.example to .env and add your API key."
        )

    try:
        payload = fetch_daily_prices(symbol, api_key)
    except AlphaVantageError as exc:
        raise SystemExit(f"Alpha Vantage error: {exc}") from exc

    raw_path = Path("data") / "raw" / f"{symbol.lower()}_daily_raw.json"
    processed_path = Path("data") / "processed" / f"{symbol.lower()}_daily_prices.csv"

    save_json(payload, raw_path)
    rows = daily_rows(payload)
    save_csv(rows, processed_path)
    summary = summarize(rows)

    print(f"Symbol: {summary['symbol']}")
    print(f"Latest date: {summary['latest_date']}")
    print(f"Latest close: {summary['latest_close']:.2f}")
    if summary["previous_close"] is not None:
        print(f"Previous close: {summary['previous_close']:.2f}")
        print(f"Change: {summary['change']:.2f} ({summary['percent_change']:.2f}%)")
    print(f"Rows saved: {summary['row_count']}")
    print(f"Raw response: {raw_path}")
    print(f"Processed data: {processed_path}")
