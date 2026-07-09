import csv
import json
from pathlib import Path


def save_json(payload: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def daily_rows(payload: dict) -> list[dict]:
    metadata = payload.get("Meta Data", {})
    symbol = metadata.get("2. Symbol", "UNKNOWN")
    series = payload["Time Series (Daily)"]

    rows = []
    for date, values in sorted(series.items(), reverse=True):
        rows.append(
            {
                "symbol": symbol,
                "date": date,
                "open": float(values["1. open"]),
                "high": float(values["2. high"]),
                "low": float(values["3. low"]),
                "close": float(values["4. close"]),
                "volume": int(values["5. volume"]),
            }
        )
    return rows


def save_csv(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["symbol", "date", "open", "high", "low", "close", "volume"]
    with path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def summarize(rows: list[dict]) -> dict:
    latest = rows[0]
    previous = rows[1] if len(rows) > 1 else None
    change = None
    percent_change = None

    if previous:
        change = latest["close"] - previous["close"]
        percent_change = (change / previous["close"]) * 100

    return {
        "symbol": latest["symbol"],
        "latest_date": latest["date"],
        "latest_close": latest["close"],
        "previous_close": previous["close"] if previous else None,
        "change": change,
        "percent_change": percent_change,
        "row_count": len(rows),
    }
