import json
from pathlib import Path

import pytest

from manufacturing_stock_tracker.pipeline import collect_history, collect_symbols
from manufacturing_stock_tracker.process import StockDataError

QUOTE_FIXTURE_PATH = Path(__file__).parent / "fixtures" / "twelve_data_quotes_watchlist.json"
HISTORY_FIXTURE_PATH = Path(__file__).parent / "fixtures" / "twelve_data_time_series_watchlist.json"


def test_collect_symbols_saves_one_raw_response_and_one_processed_watchlist(tmp_path) -> None:
    fixture = json.loads(QUOTE_FIXTURE_PATH.read_text(encoding="utf-8-sig"))
    calls = []

    def fake_fetcher(symbols, api_key):
        calls.append({"symbols": symbols, "api_key": api_key})
        return fixture

    batch = collect_symbols(["CAT", "DE", "HON"], "secret-key", tmp_path, fake_fetcher)

    assert calls == [{"symbols": ["CAT", "DE", "HON"], "api_key": "secret-key"}]
    assert batch.symbols == ["CAT", "DE", "HON"]
    assert len(batch.rows) == 3
    assert batch.summary["top_gainer_symbol"] == "CAT"
    assert batch.raw_path == tmp_path / "raw" / "twelve_data_watchlist_quotes_raw.json"
    assert batch.processed_path == tmp_path / "processed" / "manufacturing_watchlist_quotes.csv"
    assert batch.raw_path.exists()
    assert batch.processed_path.exists()
    assert "CAT" in batch.processed_path.read_text(encoding="utf-8")


def test_collect_history_saves_raw_history_processed_rows_and_momentum(tmp_path) -> None:
    fixture = json.loads(HISTORY_FIXTURE_PATH.read_text(encoding="utf-8-sig"))
    calls = []

    def fake_fetcher(symbols, api_key, interval, outputsize):
        calls.append(
            {"symbols": symbols, "api_key": api_key, "interval": interval, "outputsize": outputsize}
        )
        return fixture

    batch = collect_history(["CAT", "DE", "HON"], "secret-key", tmp_path, 30, fake_fetcher)

    assert calls == [
        {
            "symbols": ["CAT", "DE", "HON"],
            "api_key": "secret-key",
            "interval": "1day",
            "outputsize": 30,
        }
    ]
    assert len(batch.rows) == 9
    assert [row["symbol"] for row in batch.momentum] == ["CAT", "HON", "DE"]
    assert batch.summary["strongest_symbol"] == "CAT"
    assert batch.raw_path == tmp_path / "raw" / "twelve_data_watchlist_history_raw.json"
    assert batch.processed_path == tmp_path / "processed" / "manufacturing_watchlist_history.csv"
    assert batch.momentum_path == tmp_path / "processed" / "manufacturing_watchlist_momentum.csv"
    assert batch.raw_path.exists()
    assert batch.processed_path.exists()
    assert batch.momentum_path.exists()


def test_collect_symbols_fails_when_api_omits_requested_symbol(tmp_path) -> None:
    fixture = json.loads(QUOTE_FIXTURE_PATH.read_text(encoding="utf-8-sig"))

    def fake_fetcher(symbols, api_key):
        return fixture

    with pytest.raises(StockDataError, match="MMM"):
        collect_symbols(["CAT", "DE", "HON", "MMM"], "secret-key", tmp_path, fake_fetcher)


def test_collect_history_fails_when_api_omits_requested_symbol(tmp_path) -> None:
    fixture = json.loads(HISTORY_FIXTURE_PATH.read_text(encoding="utf-8-sig"))

    def fake_fetcher(symbols, api_key, interval, outputsize):
        return fixture

    with pytest.raises(StockDataError, match="MMM"):
        collect_history(["CAT", "DE", "HON", "MMM"], "secret-key", tmp_path, 30, fake_fetcher)


def test_collect_symbols_can_save_sqlite_quote_run(tmp_path) -> None:
    fixture = json.loads(QUOTE_FIXTURE_PATH.read_text(encoding="utf-8-sig"))

    def fake_fetcher(symbols, api_key):
        return fixture

    db_path = tmp_path / "tracker.db"
    batch = collect_symbols(["CAT", "DE", "HON"], "secret-key", tmp_path, fake_fetcher, db_path)

    assert batch.db_path == db_path
    assert batch.db_run_id == 1
    assert db_path.exists()