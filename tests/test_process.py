import json
from pathlib import Path

import pytest

from manufacturing_stock_tracker.process import (
    StockDataError,
    ensure_requested_symbols_returned,
    historical_rows,
    historical_summary,
    load_json,
    missing_requested_symbols,
    momentum_rows,
    parse_symbols,
    quote_rows,
    summarize,
    validate_symbol,
)

QUOTE_FIXTURE_PATH = Path(__file__).parent / "fixtures" / "twelve_data_quotes_watchlist.json"
HISTORY_FIXTURE_PATH = Path(__file__).parent / "fixtures" / "twelve_data_time_series_watchlist.json"


def load_quote_fixture():
    return json.loads(QUOTE_FIXTURE_PATH.read_text(encoding="utf-8-sig"))


def load_history_fixture():
    return json.loads(HISTORY_FIXTURE_PATH.read_text(encoding="utf-8-sig"))


def test_quote_rows_converts_twelve_data_payload() -> None:
    rows = quote_rows(load_quote_fixture(), collected_at="2026-07-25T12:00:00+00:00")

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
    summary = summarize(quote_rows(load_quote_fixture()))

    assert summary["symbols"] == ["CAT", "DE", "HON"]
    assert summary["row_count"] == 3
    assert summary["highest_price_symbol"] == "DE"
    assert summary["lowest_price_symbol"] == "HON"
    assert summary["average_price"] == pytest.approx(324.1233333333)
    assert summary["average_percent_change"] == pytest.approx(0.2202333333)
    assert summary["top_gainer_symbol"] == "CAT"
    assert summary["top_gainer_percent_change"] == pytest.approx(0.6154)
    assert summary["top_decliner_symbol"] == "DE"
    assert summary["top_decliner_percent_change"] == pytest.approx(-0.3849)
    assert summary["positive_count"] == 2
    assert summary["negative_count"] == 1
    assert summary["flat_count"] == 0


def test_historical_rows_converts_twelve_data_time_series_payload() -> None:
    rows = historical_rows(load_history_fixture(), collected_at="2026-07-25T12:00:00+00:00")

    assert len(rows) == 9
    assert rows[0] == {
        "collected_at": "2026-07-25T12:00:00+00:00",
        "symbol": "CAT",
        "datetime": "2026-07-23",
        "open": 100.0,
        "high": 106.0,
        "low": 99.0,
        "close": 105.0,
        "volume": 800,
        "interval": "1day",
        "exchange": "NYSE",
        "currency": "USD",
    }


def test_momentum_rows_rank_historical_performance() -> None:
    momentum = momentum_rows(historical_rows(load_history_fixture()))

    assert [row["symbol"] for row in momentum] == ["CAT", "HON", "DE"]
    assert momentum[0]["period_return_percent"] == pytest.approx(6.6666666667)
    assert momentum[-1]["period_return_percent"] == pytest.approx(-4.8780487805)
    assert momentum[0]["observations"] == 3


def test_historical_summary_identifies_strongest_and_weakest() -> None:
    summary = historical_summary(momentum_rows(historical_rows(load_history_fixture())))

    assert summary["symbol_count"] == 3
    assert summary["strongest_symbol"] == "CAT"
    assert summary["weakest_symbol"] == "DE"
    assert summary["positive_count"] == 2
    assert summary["negative_count"] == 1
    assert summary["flat_count"] == 0


def test_quote_rows_handles_single_symbol_payload() -> None:
    payload = load_quote_fixture()["CAT"]

    rows = quote_rows(payload)

    assert len(rows) == 1
    assert rows[0]["symbol"] == "CAT"
    assert rows[0]["price"] == 356.42


def test_missing_requested_symbols_reports_any_requested_ticker_not_returned() -> None:
    rows = quote_rows(load_quote_fixture())

    assert missing_requested_symbols(["CAT", "DE", "MMM"], rows) == ["MMM"]


def test_ensure_requested_symbols_returned_fails_clearly() -> None:
    rows = quote_rows(load_quote_fixture())

    with pytest.raises(StockDataError, match="MMM"):
        ensure_requested_symbols_returned(["CAT", "DE", "MMM"], rows)


def test_quote_rows_fails_when_payload_is_not_object_or_list() -> None:
    with pytest.raises(StockDataError, match="JSON object or list"):
        quote_rows("not-json")


def test_historical_rows_fails_when_values_missing() -> None:
    payload = load_history_fixture()
    del payload["CAT"]["values"]

    with pytest.raises(StockDataError, match="values: Field required"):
        historical_rows(payload)


def test_momentum_rows_require_at_least_two_rows() -> None:
    with pytest.raises(StockDataError, match="at least two"):
        momentum_rows([{"symbol": "CAT", "datetime": "2026-07-25", "close": 100.0}])


def test_quote_rows_fails_when_symbol_payload_has_error() -> None:
    payload = {"CAT": {"status": "error", "message": "Invalid symbol"}}

    with pytest.raises(StockDataError, match="Invalid symbol"):
        quote_rows(payload)


def test_quote_rows_fails_when_required_close_missing() -> None:
    payload = load_quote_fixture()
    del payload["CAT"]["close"]

    with pytest.raises(StockDataError, match="close: Field required"):
        quote_rows(payload)


def test_quote_rows_fails_when_numeric_value_is_invalid() -> None:
    payload = load_quote_fixture()
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
    assert load_json(QUOTE_FIXTURE_PATH)["CAT"]["symbol"] == "CAT"
