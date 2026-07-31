"""Report helpers for loading committed outputs and preparing figures."""

from pathlib import Path

import pandas as pd

from manufacturing_stock_tracker.process import historical_summary


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
HISTORY_CSV = PROCESSED_DIR / "manufacturing_watchlist_history.csv"
MOMENTUM_CSV = PROCESSED_DIR / "manufacturing_watchlist_momentum.csv"
QUOTE_CSV = PROCESSED_DIR / "manufacturing_watchlist_quotes.csv"


def load_history(path: Path = HISTORY_CSV) -> pd.DataFrame:
    """Load processed historical price rows from the committed CSV output."""
    return pd.read_csv(path, parse_dates=["datetime", "collected_at"])


def load_momentum(path: Path = MOMENTUM_CSV) -> pd.DataFrame:
    """Load processed momentum rows from the committed CSV output."""
    return pd.read_csv(path, parse_dates=["start_datetime", "end_datetime"])


def load_quotes(path: Path = QUOTE_CSV) -> pd.DataFrame:
    """Load processed current quote rows from the committed CSV output."""
    return pd.read_csv(path, parse_dates=["datetime", "collected_at"])


def normalized_close_table(history: pd.DataFrame) -> pd.DataFrame:
    """Return close prices normalized to 100 at each symbol's first date."""
    ordered = history.sort_values(["symbol", "datetime"]).copy()
    ordered["normalized_close"] = ordered.groupby("symbol")["close"].transform(
        lambda values: (values / values.iloc[0]) * 100
    )
    return ordered.pivot(index="datetime", columns="symbol", values="normalized_close")


def momentum_summary(momentum: pd.DataFrame) -> dict:
    """Summarize momentum rows using the project's processing logic."""
    return historical_summary(momentum.to_dict("records"))
