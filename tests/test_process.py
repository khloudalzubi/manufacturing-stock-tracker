import json
from pathlib import Path

import pytest

from manufacturing_stock_tracker.process import (
    StockDataError,
    load_json,
    parse_symbols,
    quote_rows,
    summarize,
    validate_symbol,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "twelve_data_quotes_watchlist.json"


def load_fixture():
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8-sig"))


def test_quote_rows_converts_twelve_data_payload() -> None:
    rows = quote_rows(load_fixture(), collected_at="2026-07-25T12:00:00+00:00")

    assert len(rows) == 3
    assert rows[0] == {
        "collected_at": "2026-07-25T12:00:00+00:00",
        "symbol": "CAT",
        "name": "Caterpillar Inc.",
        "exchange": "NYSE",
        "currency": "USD",
        "datetime": "2026-07-25",
        "price": 356.42,
        "open": 354.0,
        "high": 358.2,
        "low": 352.75,
        "volume": 2456789,
        "previous_close": 354.24,
        "change": 2.18,
        "percent_change": 0.6154,
        "timestamp": 1785000000,
    }


def test_summarize_reports_watchlist_values() -> None:
    summary = summarize(quote_rows(load_fixture()))

    assert summary["symbols"] == ["CAT", "DE", "HON"]
    assert summary["row_count"] == 3
    assert summary["highest_price_symbol"] == "DE"
    assert summary["lowest_price_symbol"] == "HON"
    assert summary["average_price"] == pytest.approx(324.1233333333)
    assert summary["average_percent_change"] == pytest.approx(0.2202333333)


def test_quote_rows_handles_single_symbol_payload() -> None:
    payload = load_fixture()["CAT"]

    rows = quote_rows(payload)

    assert len(rows) == 1
    assert rows[0]["symbol"] == "CAT"
    assert rows[0]["price"] == 356.42


def test_quote_rows_fails_when_payload_is_not_object_or_list() -> None:
    with pytest.raises(StockDataError, match="JSON object or list"):
        quote_rows("not-json")


def test_quote_rows_fails_when_symbol_payload_has_error() -> None:
    payload = {"CAT": {"status": "error", "message": "Invalid symbol"}}

    with pytest.raises(StockDataError, match="Invalid symbol"):
        quote_rows(payload)


def test_quote_rows_fails_when_required_close_missing() -> None:
    payload = load_fixture()
    del payload["CAT"]["close"]

    with pytest.raises(StockDataError, match="close: Field required"):
        quote_rows(payload)


def test_quote_rows_fails_when_numeric_value_is_invalid() -> None:
    payload = load_fixture()
    payload["CAT"]["close"] = "not-a-number"

    with pytest.raises(StockDataError, match="valid number"):
        quote_rows(payload)


def test_summarize_fails_on_empty_rows() -> None:
    with pytest.raises(StockDataError, match="empty"):
        summarize([])


def test_validate_symbol_cleans_input() -> None:
    assert validate_symbol(" cat ") == "CAT"


def test_validate_symbol_rejects_empty_symbol() -> None:
    with pytest.raises(StockDataError, match="cannot be empty"):
        validate_symbol("  ")


def test_validate_symbol_rejects_unexpected_characters() -> None:
    with pytest.raises(StockDataError, match="letters, numbers"):
        validate_symbol("CAT!")


def test_parse_symbols_splits_deduplicates_and_cleans() -> None:
    assert parse_symbols("cat, de, CAT,HON") == ["CAT", "DE", "HON"]


def test_load_json_reads_fixture() -> None:
    assert load_json(FIXTURE_PATH)["CAT"]["symbol"] == "CAT"
