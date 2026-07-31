import pandas as pd
import pytest

from manufacturing_stock_tracker.reporting import momentum_summary, normalized_close_table


def test_normalized_close_table_indexes_each_symbol_to_100() -> None:
    history = pd.DataFrame(
        [
            {"symbol": "CAT", "datetime": "2026-07-01", "close": 100.0},
            {"symbol": "CAT", "datetime": "2026-07-02", "close": 110.0},
            {"symbol": "DE", "datetime": "2026-07-01", "close": 200.0},
            {"symbol": "DE", "datetime": "2026-07-02", "close": 190.0},
        ]
    )
    history["datetime"] = pd.to_datetime(history["datetime"])

    normalized = normalized_close_table(history)

    assert normalized.loc[pd.Timestamp("2026-07-01"), "CAT"] == 100.0
    assert normalized.loc[pd.Timestamp("2026-07-02"), "CAT"] == pytest.approx(110.0)
    assert normalized.loc[pd.Timestamp("2026-07-02"), "DE"] == pytest.approx(95.0)


def test_momentum_summary_uses_project_historical_summary_logic() -> None:
    momentum = pd.DataFrame(
        [
            {"symbol": "CAT", "period_return_percent": 5.0},
            {"symbol": "DE", "period_return_percent": -2.0},
        ]
    )

    summary = momentum_summary(momentum)

    assert summary["strongest_symbol"] == "CAT"
    assert summary["weakest_symbol"] == "DE"
    assert summary["average_return_percent"] == 1.5
