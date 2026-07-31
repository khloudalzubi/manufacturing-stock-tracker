"""Streamlit dashboard for quote snapshots and historical momentum analysis."""

from pathlib import Path
import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from manufacturing_stock_tracker.api import TwelveDataError
from manufacturing_stock_tracker.pipeline import collect_history, collect_symbols
from manufacturing_stock_tracker.process import StockDataError, historical_summary, parse_symbols, summarize


DATA_DIR = Path("data")
QUOTE_PATH = DATA_DIR / "processed" / "manufacturing_watchlist_quotes.csv"
HISTORY_PATH = DATA_DIR / "processed" / "manufacturing_watchlist_history.csv"
MOMENTUM_PATH = DATA_DIR / "processed" / "manufacturing_watchlist_momentum.csv"
QUOTE_COLUMNS = [
    "symbol",
    "name",
    "exchange",
    "currency",
    "price",
    "percent_change",
    "volume",
    "datetime",
]


def format_percent(value: float | None) -> str:
    """Format an optional percentage for dashboard metric cards."""
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value:.2f}%"


def normalized_prices(history_df: pd.DataFrame) -> pd.DataFrame:
    """Return close prices indexed to 100 at each symbol's first observation."""
    ordered = history_df.sort_values(["symbol", "datetime"]).copy()
    ordered["normalized_close"] = ordered.groupby("symbol")["close"].transform(
        lambda values: (values / values.iloc[0]) * 100
    )
    return ordered.pivot(index="datetime", columns="symbol", values="normalized_close")


def show_quotes() -> None:
    """Render current quote metrics, tables, and comparison charts."""
    if not QUOTE_PATH.exists():
        st.info("No processed quote data found yet. Use the sidebar to collect data first.")
        return

    df = pd.read_csv(QUOTE_PATH)
    missing_columns = [column for column in QUOTE_COLUMNS if column not in df.columns]

    if missing_columns:
        st.error("Processed quote data is missing required column(s): " + ", ".join(missing_columns))
        return

    display_df = df.sort_values("symbol")
    summary = summarize(display_df.to_dict("records"))
    top_gainer = summary["top_gainer_symbol"] or "n/a"
    top_decliner = summary["top_decliner_symbol"] or "n/a"

    metric_cols = st.columns(5)
    metric_cols[0].metric("Symbols", summary["row_count"])
    metric_cols[1].metric("Average Price", f"${summary['average_price']:.2f}")
    metric_cols[2].metric("Average Change", format_percent(summary["average_percent_change"]))
    metric_cols[3].metric("Top Gainer", top_gainer, format_percent(summary["top_gainer_percent_change"]))
    metric_cols[4].metric("Top Decliner", top_decliner, format_percent(summary["top_decliner_percent_change"]))

    st.caption(
        f"Watchlist direction: {summary['positive_count']} up, "
        f"{summary['negative_count']} down, {summary['flat_count']} flat."
    )

    st.subheader("Latest Watchlist Quotes")
    st.dataframe(
        display_df[QUOTE_COLUMNS].sort_values("percent_change", ascending=False),
        width="stretch",
        hide_index=True,
    )

    chart_cols = st.columns(2)
    with chart_cols[0]:
        st.subheader("Price by Symbol")
        st.bar_chart(display_df.set_index("symbol")["price"])

    with chart_cols[1]:
        st.subheader("Percent Change by Symbol")
        st.bar_chart(display_df.set_index("symbol")["percent_change"])

    st.subheader("Processed Quote Data")
    st.dataframe(display_df, width="stretch", hide_index=True)


def show_history() -> None:
    """Render historical momentum metrics, ranking table, and normalized trend."""
    if not HISTORY_PATH.exists() or not MOMENTUM_PATH.exists():
        st.info("No processed historical data found yet. Use the sidebar to collect history first.")
        return

    history_df = pd.read_csv(HISTORY_PATH)
    momentum_df = pd.read_csv(MOMENTUM_PATH)
    summary = historical_summary(momentum_df.to_dict("records"))

    metric_cols = st.columns(4)
    metric_cols[0].metric("Symbols", summary["symbol_count"])
    metric_cols[1].metric("Average Return", format_percent(summary["average_return_percent"]))
    metric_cols[2].metric("Strongest", summary["strongest_symbol"], format_percent(summary["strongest_return_percent"]))
    metric_cols[3].metric("Weakest", summary["weakest_symbol"], format_percent(summary["weakest_return_percent"]))

    st.caption(
        "Historical momentum asks: which manufacturing companies moved the most over the collected period? "
        f"{summary['positive_count']} symbols were positive, {summary['negative_count']} were negative, "
        f"and {summary['flat_count']} were flat."
    )

    st.subheader("Normalized Close Trend")
    st.line_chart(normalized_prices(history_df))

    st.subheader("Momentum Ranking")
    st.dataframe(
        momentum_df.sort_values("period_return_percent", ascending=False),
        width="stretch",
        hide_index=True,
    )

    st.subheader("Processed Historical Data")
    st.dataframe(history_df.sort_values(["symbol", "datetime"]), width="stretch", hide_index=True)


def main() -> None:
    """Run the Streamlit dashboard application."""
    load_dotenv()
    st.set_page_config(page_title="Manufacturing Market Monitor", layout="wide")
    st.title("Manufacturing Market Monitor")
    st.caption("Twelve Data market data for selected manufacturing and industrial companies.")

    mode = st.sidebar.radio("View", ["Current quotes", "Historical momentum"])
    symbols_input = st.sidebar.text_input("Ticker symbols", "CAT,DE,HON,GE,MMM")
    api_key = os.environ.get("TWELVE_DATA_API_KEY")

    if mode == "Current quotes":
        collect = st.sidebar.button("Collect latest quote data")
        if collect:
            if not api_key:
                st.error("Missing TWELVE_DATA_API_KEY. Copy .env.example to .env and add your API key.")
            else:
                try:
                    symbols = parse_symbols(symbols_input)
                    batch = collect_symbols(symbols, api_key, DATA_DIR)
                except (TwelveDataError, StockDataError) as exc:
                    st.error(str(exc))
                else:
                    st.success(f"Collected {len(batch.rows)} quote rows for {', '.join(symbols)}.")
        show_quotes()
    else:
        outputsize = st.sidebar.slider("Historical days", min_value=5, max_value=90, value=30, step=5)
        collect = st.sidebar.button("Collect historical data")
        if collect:
            if not api_key:
                st.error("Missing TWELVE_DATA_API_KEY. Copy .env.example to .env and add your API key.")
            else:
                try:
                    symbols = parse_symbols(symbols_input)
                    batch = collect_history(symbols, api_key, DATA_DIR, outputsize)
                except (TwelveDataError, StockDataError) as exc:
                    st.error(str(exc))
                else:
                    st.success(
                        f"Collected {len(batch.rows)} historical rows for {', '.join(symbols)}."
                    )
        show_history()


main()
