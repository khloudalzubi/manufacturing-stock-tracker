import csv
import json
from datetime import UTC, datetime
from pathlib import Path

from pydantic import ValidationError

from manufacturing_stock_tracker.models import TwelveDataQuote


class StockDataError(ValueError):
    """Raised when stock quote data cannot be processed safely."""


def save_json(payload: dict | list, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_json(path: Path) -> dict | list:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def validate_symbol(symbol: str) -> str:
    cleaned = symbol.strip().upper()
    if not cleaned:
        raise StockDataError("Ticker symbol cannot be empty.")
    if not cleaned.replace(".", "").replace("-", "").replace("/", "").isalnum():
        raise StockDataError(
            "Ticker symbol can only contain letters, numbers, periods, hyphens, or slashes."
        )
    return cleaned


def parse_symbols(raw_symbols: str) -> list[str]:
    symbols = []
    for raw_symbol in raw_symbols.split(","):
        symbol = validate_symbol(raw_symbol)
        if symbol not in symbols:
            symbols.append(symbol)

    if not symbols:
        raise StockDataError("At least one ticker symbol is required.")

    return symbols


def _payload_items(payload: dict | list) -> list[tuple[str, dict]]:
    if isinstance(payload, list):
        return [(str(index), item) for index, item in enumerate(payload)]
    if not isinstance(payload, dict):
        raise StockDataError("Twelve Data response must be a JSON object or list.")
    if payload.get("status") == "error":
        raise StockDataError(str(payload.get("message", "Twelve Data returned an error.")))
    if "symbol" in payload and "close" in payload:
        return [(payload["symbol"], payload)]
    return [(symbol, item) for symbol, item in payload.items()]


def validated_quotes(payload: dict | list) -> list[TwelveDataQuote]:
    quotes = []
    errors = []

    for symbol, item in _payload_items(payload):
        if isinstance(item, dict) and item.get("status") == "error":
            errors.append(f"{symbol}: {item.get('message', 'Twelve Data returned an error.')}")
            continue
        try:
            quotes.append(TwelveDataQuote.model_validate(item))
        except ValidationError as exc:
            details = "; ".join(
                f"{'.'.join(str(part) for part in error['loc'])}: {error['msg']}"
                for error in exc.errors()
            )
            errors.append(f"{symbol}: {details}")

    if errors:
        raise StockDataError("Twelve Data quote data failed validation: " + "; ".join(errors))
    if not quotes:
        raise StockDataError("Twelve Data response did not include quote data.")

    return quotes


def quote_rows(payload: dict | list, collected_at: str | None = None) -> list[dict]:
    collected_at = collected_at or datetime.now(UTC).isoformat(timespec="seconds")
    rows = []

    for quote in validated_quotes(payload):
        rows.append(
            {
                "collected_at": collected_at,
                "symbol": quote.symbol.upper(),
                "name": quote.name,
                "exchange": quote.exchange,
                "currency": quote.currency,
                "datetime": quote.datetime,
                "price": quote.close,
                "open": quote.open_price,
                "high": quote.high,
                "low": quote.low,
                "volume": quote.volume,
                "previous_close": quote.previous_close,
                "change": quote.change,
                "percent_change": quote.percent_change,
                "timestamp": quote.timestamp,
            }
        )

    return rows


def save_csv(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "collected_at",
        "symbol",
        "name",
        "exchange",
        "currency",
        "datetime",
        "price",
        "open",
        "high",
        "low",
        "volume",
        "previous_close",
        "change",
        "percent_change",
        "timestamp",
    ]
    with path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def summarize(rows: list[dict]) -> dict:
    if not rows:
        raise StockDataError("Cannot summarize an empty set of stock quote rows.")

    prices = [row["price"] for row in rows]
    changes = [row["percent_change"] for row in rows if row["percent_change"] is not None]

    return {
        "symbols": [row["symbol"] for row in rows],
        "row_count": len(rows),
        "average_price": sum(prices) / len(prices),
        "highest_price_symbol": max(rows, key=lambda row: row["price"])["symbol"],
        "lowest_price_symbol": min(rows, key=lambda row: row["price"])["symbol"],
        "average_percent_change": sum(changes) / len(changes) if changes else None,
    }
