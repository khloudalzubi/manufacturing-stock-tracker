import json
from pathlib import Path

from manufacturing_stock_tracker.pipeline import collect_symbols

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "twelve_data_quotes_watchlist.json"


def test_collect_symbols_saves_one_raw_response_and_one_processed_watchlist(tmp_path) -> None:
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8-sig"))
    calls = []

    def fake_fetcher(symbols, api_key):
        calls.append({"symbols": symbols, "api_key": api_key})
        return fixture

    batch = collect_symbols(["CAT", "DE", "HON"], "secret-key", tmp_path, fake_fetcher)

    assert calls == [{"symbols": ["CAT", "DE", "HON"], "api_key": "secret-key"}]
    assert batch.symbols == ["CAT", "DE", "HON"]
    assert len(batch.rows) == 3
    assert batch.raw_path == tmp_path / "raw" / "twelve_data_watchlist_quotes_raw.json"
    assert batch.processed_path == tmp_path / "processed" / "manufacturing_watchlist_quotes.csv"
    assert batch.raw_path.exists()
    assert batch.processed_path.exists()
    assert "CAT" in batch.processed_path.read_text(encoding="utf-8")
