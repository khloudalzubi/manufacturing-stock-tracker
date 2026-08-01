from manufacturing_stock_tracker.storage import (
    initialize_database,
    quote_rows_for_run,
    recent_quote_runs,
    save_quote_run,
)


def sample_rows() -> list[dict]:
    return [
        {
            "collected_at": "2026-08-01T12:00:00+00:00",
            "symbol": "CAT",
            "name": "Caterpillar Inc.",
            "exchange": "NYSE",
            "currency": "USD",
            "datetime": "2026-08-01",
            "price": 100.0,
            "percent_change": 1.5,
            "volume": 1000,
        },
        {
            "collected_at": "2026-08-01T12:00:00+00:00",
            "symbol": "DE",
            "name": "Deere & Company",
            "exchange": "NYSE",
            "currency": "USD",
            "datetime": "2026-08-01",
            "price": 90.0,
            "percent_change": -0.5,
            "volume": 2000,
        },
    ]


def sample_summary() -> dict:
    return {
        "row_count": 2,
        "average_price": 95.0,
        "average_percent_change": 0.5,
        "top_gainer_symbol": "CAT",
        "top_decliner_symbol": "DE",
    }


def test_initialize_database_creates_sqlite_file(tmp_path) -> None:
    db_path = tmp_path / "tracker.db"

    initialize_database(db_path)

    assert db_path.exists()


def test_save_quote_run_and_load_recent_runs(tmp_path) -> None:
    db_path = tmp_path / "tracker.db"

    run_id = save_quote_run(sample_rows(), sample_summary(), ["CAT", "DE"], db_path)
    runs = recent_quote_runs(db_path)
    rows = quote_rows_for_run(run_id, db_path)

    assert run_id == 1
    assert runs[0]["symbols"] == "CAT,DE"
    assert runs[0]["row_count"] == 2
    assert rows[0]["symbol"] == "CAT"
    assert rows[1]["symbol"] == "DE"


def test_recent_quote_runs_returns_empty_list_when_database_missing(tmp_path) -> None:
    assert recent_quote_runs(tmp_path / "missing.db") == []
