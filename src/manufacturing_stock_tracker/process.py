"""Validation, transformation, and summary logic for Twelve Data outputs."""

import csv
import json
from datetime import UTC, datetime
from pathlib import Path

from pydantic import ValidationError

from manufacturing_stock_tracker.models import TwelveDataQuote, TwelveDataTimeSeries


class StockDataError(ValueError):
    """Raised when stock data cannot be processed safely."""


def save_json(payload: dict | list, path: Path) -> None:
    """Save a raw API payload as formatted JSON evidence."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_json(path: Path) -> dict | list:
    """Load JSON from disk, accepting UTF-8 files with or without a BOM."""
    return json.loads(path.read_text(encoding="utf-8-sig"))


def validate_symbol(symbol: str) -> str:
    """Normalize one ticker symbol and reject unsupported characters."""
    cleaned = symbol.strip().upper()
    if not cleaned:
        raise StockDataError("Ticker symbol cannot be empty.")
    if not cleaned.replace(".", "").replace("-", "").replace("/", "").isalnum():
        raise StockDataError(
            "Ticker symbol can only contain letters, numbers, periods, hyphens, or slashes."
        )
    return cleaned


def parse_symbols(raw_symbols: str) -> list[str]:
    """Parse a comma-separated watchlist into cleaned, deduplicated symbols."""
    symbols = []
    for raw_symbol in raw_symbols.split(","):
        symbol = validate_symbol(raw_symbol)
        if symbol not in symbols:
            symbols.append(symbol)

    if not symbols:
        raise StockDataError("At least one ticker symbol is required.")

    return symbols


def _payload_items(payload: dict | list) -> list[tuple[str, dict]]:
    """Return symbol-payload pairs from single, batch, or list responses."""
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
    """Validate quote payloads and collect symbol-specific validation errors."""
    quotes = []
    errors = []

    for symbol, item in _payload_items(payload):
        if isinstance(item, dict) and item.get("status") == "error":
            errors.append(f"{symbol}: {item.get('message', 'Twelve Data returned an error.')}")
            continue
        try:
            quotes.append(TwelveDataQuote.model_validate(item))
        except ValidationError as exc:
            details = _validation_details(exc)
            errors.append(f"{symbol}: {details}")

    if errors:
        raise StockDataError("Twelve Data quote data failed validation: " + "; ".join(errors))
    if not quotes:
        raise StockDataError("Twelve Data response did not include quote data.")

    return quotes


def quote_rows(payload: dict | list, collected_at: str | None = None) -> list[dict]:
    """Convert validated quote payloads into processed CSV-ready rows."""
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


def _time_series_items(payload: dict | list) -> list[tuple[str, dict]]:
    """Return symbol-payload pairs from single or batch time-series responses."""
    if isinstance(payload, dict) and "meta" in payload and "values" in payload:
        symbol = payload.get("meta", {}).get("symbol", "UNKNOWN")
        return [(symbol, payload)]
    return _payload_items(payload)


def validated_time_series(payload: dict | list) -> list[TwelveDataTimeSeries]:
    """Validate historical time-series payloads and aggregate clear errors."""
    series_list = []
    errors = []

    for symbol, item in _time_series_items(payload):
        if isinstance(item, dict) and item.get("status") == "error":
            errors.append(f"{symbol}: {item.get('message', 'Twelve Data returned an error.')}")
            continue
        try:
            series_list.append(TwelveDataTimeSeries.model_validate(item))
        except ValidationError as exc:
            errors.append(f"{symbol}: {_validation_details(exc)}")

    if errors:
        raise StockDataError("Twelve Data historical data failed validation: " + "; ".join(errors))
    if not series_list:
        raise StockDataError("Twelve Data response did not include historical price data.")

    return series_list


def historical_rows(payload: dict | list, collected_at: str | None = None) -> list[dict]:
    """Convert validated time-series payloads into processed historical rows."""
    collected_at = collected_at or datetime.now(UTC).isoformat(timespec="seconds")
    rows = []

    for series in validated_time_series(payload):
        symbol = series.meta.symbol.upper()
        for bar in sorted(series.values, key=lambda value: value.datetime):
            rows.append(
                {
                    "collected_at": collected_at,
                    "symbol": symbol,
                    "datetime": bar.datetime,
                    "open": bar.open_price,
                    "high": bar.high,
                    "low": bar.low,
                    "close": bar.close,
                    "volume": bar.volume,
                    "interval": series.meta.interval,
                    "exchange": series.meta.exchange,
                    "currency": series.meta.currency,
                }
            )

    return rows


def momentum_rows(rows: list[dict]) -> list[dict]:
    """Calculate period return and price range for each symbol's history."""
    if not rows:
        raise StockDataError("Cannot calculate momentum from empty historical rows.")

    grouped: dict[str, list[dict]] = {}
    for row in rows:
        grouped.setdefault(row["symbol"], []).append(row)

    momentum = []
    for symbol, symbol_rows in sorted(grouped.items()):
        ordered = sorted(symbol_rows, key=lambda row: row["datetime"])
        if len(ordered) < 2:
            raise StockDataError(f"Need at least two historical rows to calculate momentum for {symbol}.")
        start = ordered[0]
        end = ordered[-1]
        start_close = start["close"]
        end_close = end["close"]
        if start_close == 0:
            raise StockDataError(f"Cannot calculate momentum for {symbol} because start close is zero.")
        period_return = ((end_close - start_close) / start_close) * 100
        closes = [row["close"] for row in ordered]
        price_range_percent = ((max(closes) - min(closes)) / start_close) * 100
        momentum.append(
            {
                "symbol": symbol,
                "start_datetime": start["datetime"],
                "end_datetime": end["datetime"],
                "start_close": start_close,
                "end_close": end_close,
                "period_return_percent": period_return,
                "price_range_percent": price_range_percent,
                "observations": len(ordered),
            }
        )

    return sorted(momentum, key=lambda row: row["period_return_percent"], reverse=True)


def historical_summary(momentum: list[dict]) -> dict:
    """Summarize momentum rows for dashboard and CLI reporting."""
    if not momentum:
        raise StockDataError("Cannot summarize empty momentum rows.")

    strongest = max(momentum, key=lambda row: row["period_return_percent"])
    weakest = min(momentum, key=lambda row: row["period_return_percent"])
    returns = [row["period_return_percent"] for row in momentum]

    return {
        "symbol_count": len(momentum),
        "average_return_percent": sum(returns) / len(returns),
        "strongest_symbol": strongest["symbol"],
        "strongest_return_percent": strongest["period_return_percent"],
        "weakest_symbol": weakest["symbol"],
        "weakest_return_percent": weakest["period_return_percent"],
        "positive_count": sum(1 for value in returns if value > 0),
        "negative_count": sum(1 for value in returns if value < 0),
        "flat_count": sum(1 for value in returns if value == 0),
    }


def missing_requested_symbols(requested_symbols: list[str], rows: list[dict]) -> list[str]:
    """Return requested symbols that are absent from processed rows."""
    returned_symbols = {str(row["symbol"]).upper() for row in rows}
    return [symbol for symbol in requested_symbols if symbol.upper() not in returned_symbols]


def ensure_requested_symbols_returned(requested_symbols: list[str], rows: list[dict]) -> None:
    """Raise a clear error when an API response omits requested symbols."""
    missing = missing_requested_symbols(requested_symbols, rows)
    if missing:
        raise StockDataError(
            "Twelve Data did not return data for requested symbol(s): "
            + ", ".join(missing)
        )


def save_csv(rows: list[dict], path: Path) -> None:
    """Save processed rows as CSV using the first row's field order."""
    if not rows:
        raise StockDataError("Cannot save an empty CSV.")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def summarize(rows: list[dict]) -> dict:
    """Summarize current quote rows for CLI and dashboard display."""
    if not rows:
        raise StockDataError("Cannot summarize an empty set of stock quote rows.")

    prices = [row["price"] for row in rows]
    changes = [row["percent_change"] for row in rows if row["percent_change"] is not None]
    rows_with_changes = [row for row in rows if row["percent_change"] is not None]
    top_gainer = max(rows_with_changes, key=lambda row: row["percent_change"], default=None)
    top_decliner = min(rows_with_changes, key=lambda row: row["percent_change"], default=None)

    return {
        "symbols": [row["symbol"] for row in rows],
        "row_count": len(rows),
        "average_price": sum(prices) / len(prices),
        "highest_price_symbol": max(rows, key=lambda row: row["price"])["symbol"],
        "lowest_price_symbol": min(rows, key=lambda row: row["price"])["symbol"],
        "average_percent_change": sum(changes) / len(changes) if changes else None,
        "top_gainer_symbol": top_gainer["symbol"] if top_gainer else None,
        "top_gainer_percent_change": top_gainer["percent_change"] if top_gainer else None,
        "top_decliner_symbol": top_decliner["symbol"] if top_decliner else None,
        "top_decliner_percent_change": top_decliner["percent_change"] if top_decliner else None,
        "positive_count": sum(1 for row in rows_with_changes if row["percent_change"] > 0),
        "negative_count": sum(1 for row in rows_with_changes if row["percent_change"] < 0),
        "flat_count": sum(1 for row in rows_with_changes if row["percent_change"] == 0),
    }


def _validation_details(exc: ValidationError) -> str:
    """Format Pydantic validation errors as compact location/message text."""
    return "; ".join(
        f"{'.'.join(str(part) for part in error['loc'])}: {error['msg']}"
        for error in exc.errors()
    )
