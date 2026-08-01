import pandas as pd
import pytest

from manufacturing_stock_tracker.reporting import (
    historical_period_label,
    momentum_story,
    momentum_summary,
    normalized_close_explanation,
    normalized_close_table,
    quote_freshness_label,
    quote_story,
    symbol_detail,
)


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


def test_momentum_story_describes_strongest_and_weakest_symbols() -> None:
    story = momentum_story(
        {
            "strongest_symbol": "CAT",
            "strongest_return_percent": 12.5,
            "weakest_symbol": "DE",
            "weakest_return_percent": -3.25,
            "positive_count": 3,
            "negative_count": 2,
            "flat_count": 0,
        }
    )

    assert "CAT" in story
    assert "12.50%" in story
    assert "DE" in story
    assert "-3.25%" in story


def test_quote_story_describes_saved_quote_snapshot_direction() -> None:
    story = quote_story(
        {
            "row_count": 5,
            "positive_count": 2,
            "negative_count": 3,
            "flat_count": 0,
        }
    )

    assert "5 symbols" in story
    assert "2 are up" in story
    assert "3 are down" in story


def test_normalized_close_explanation_is_plain_language() -> None:
    explanation = normalized_close_explanation()

    assert "first closing price to 100" in explanation
    assert "above 100" in explanation
    assert "below 100" in explanation


def test_period_and_freshness_labels_summarize_data_context() -> None:
    momentum = pd.DataFrame(
        [
            {
                "symbol": "CAT",
                "start_datetime": "2026-07-01",
                "end_datetime": "2026-07-30",
                "observations": 30,
            }
        ]
    )
    quotes = pd.DataFrame(
        [
            {
                "symbol": "CAT",
                "collected_at": "2026-08-01T12:00:00+00:00",
                "datetime": "2026-07-31",
            }
        ]
    )

    assert "2026-07-01 to 2026-07-30" in historical_period_label(momentum)
    assert "Collected 2026-08-01 12:00 UTC" in quote_freshness_label(quotes)


def test_symbol_detail_combines_quote_and_momentum_context() -> None:
    momentum = pd.DataFrame(
        [
            {
                "symbol": "CAT",
                "period_return_percent": 10.0,
                "price_range_percent": 15.0,
                "observations": 30,
            }
        ]
    )
    quotes = pd.DataFrame(
        [
            {
                "symbol": "CAT",
                "name": "Caterpillar Inc.",
                "price": 100.0,
                "percent_change": 1.5,
                "volume": 1000,
            }
        ]
    )

    detail = symbol_detail("cat", momentum, quotes)

    assert detail["symbol"] == "CAT"
    assert detail["name"] == "Caterpillar Inc."
    assert detail["period_return_percent"] == 10.0
    assert detail["price"] == 100.0