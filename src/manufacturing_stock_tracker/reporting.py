"""Report and dashboard helpers for processed project outputs."""

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


def quote_story(summary: dict) -> str:
    """Return a concise plain-language summary of the current quote snapshot."""
    return (
        f"This saved quote snapshot contains {summary['row_count']} symbols. "
        f"{summary['positive_count']} are up, {summary['negative_count']} are down, "
        f"and {summary['flat_count']} are flat in the provider's latest quote data."
    )


def momentum_story(summary: dict) -> str:
    """Return a concise plain-language interpretation of momentum results."""
    return (
        f"{summary['strongest_symbol']} has the strongest recent momentum "
        f"at {summary['strongest_return_percent']:.2f}%, while "
        f"{summary['weakest_symbol']} has the weakest at "
        f"{summary['weakest_return_percent']:.2f}%. Across the watchlist, "
        f"{summary['positive_count']} symbols are positive, "
        f"{summary['negative_count']} are negative, and {summary['flat_count']} are flat."
    )


def normalized_close_explanation() -> str:
    """Explain normalized close values for nontechnical dashboard users."""
    return (
        "Normalized close sets each symbol's first closing price to 100. "
        "Values above 100 mean the stock rose from its starting point, and "
        "values below 100 mean it fell from its starting point."
    )


def historical_period_label(momentum: pd.DataFrame) -> str:
    """Return a compact label for the historical period covered by momentum data."""
    start = pd.to_datetime(momentum["start_datetime"]).min().strftime("%Y-%m-%d")
    end = pd.to_datetime(momentum["end_datetime"]).max().strftime("%Y-%m-%d")
    observations = int(momentum["observations"].max())
    return f"{start} to {end} with up to {observations} daily observations per symbol"


def quote_freshness_label(quotes: pd.DataFrame) -> str:
    """Return a compact label for the latest quote snapshot timestamp."""
    collected_at = pd.to_datetime(quotes["collected_at"]).max().strftime("%Y-%m-%d %H:%M UTC")
    provider_date = str(quotes["datetime"].max())
    return f"Collected {collected_at}; provider quote date {provider_date}"


def symbol_detail(symbol: str, momentum: pd.DataFrame, quotes: pd.DataFrame | None = None) -> dict:
    """Return combined quote and momentum details for one selected symbol."""
    selected = symbol.upper()
    momentum_row = momentum.loc[momentum["symbol"] == selected]
    if momentum_row.empty:
        raise ValueError(f"No momentum row found for {selected}.")

    detail = momentum_row.iloc[0].to_dict()
    if quotes is not None and "symbol" in quotes.columns:
        quote_row = quotes.loc[quotes["symbol"] == selected]
        if not quote_row.empty:
            detail.update(
                {
                    "price": quote_row.iloc[0].get("price"),
                    "percent_change": quote_row.iloc[0].get("percent_change"),
                    "volume": quote_row.iloc[0].get("volume"),
                    "name": quote_row.iloc[0].get("name"),
                }
            )
    return detail