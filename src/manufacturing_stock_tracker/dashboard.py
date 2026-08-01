"""Streamlit dashboard for quote snapshots and historical momentum analysis."""

from pathlib import Path
import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from manufacturing_stock_tracker.api import TwelveDataError
from manufacturing_stock_tracker.pipeline import collect_history, collect_symbols
from manufacturing_stock_tracker.process import StockDataError, parse_symbols, summarize
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
from manufacturing_stock_tracker.storage import DEFAULT_DB_PATH, recent_quote_runs


DATA_DIR = Path("data")
QUOTE_PATH = DATA_DIR / "processed" / "manufacturing_watchlist_quotes.csv"
HISTORY_PATH = DATA_DIR / "processed" / "manufacturing_watchlist_history.csv"
MOMENTUM_PATH = DATA_DIR / "processed" / "manufacturing_watchlist_momentum.csv"
DB_PATH = DEFAULT_DB_PATH
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
DASHBOARD_CSS = """
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}
.hero {
    border: 1px solid #d8dee8;
    border-left: 6px solid #2f6f73;
    border-radius: 8px;
    padding: 1.15rem 1.25rem;
    background: #f7faf9;
    margin-bottom: 1.25rem;
}
.hero h1 {
    margin: 0 0 .35rem 0;
    font-size: 2rem;
    letter-spacing: 0;
}
.hero p {
    margin: 0;
    color: #3f4f5f;
    font-size: 1.02rem;
}
.story-panel {
    border: 1px solid #d8dee8;
    border-radius: 8px;
    padding: 1rem 1.1rem;
    background: #ffffff;
    margin: .75rem 0 1.1rem 0;
}
.story-panel strong {
    color: #20343f;
}
.evidence-note {
    color: #52616f;
    font-size: .9rem;
}
.small-label {
    color: #667382;
    font-size: .78rem;
    text-transform: uppercase;
    letter-spacing: .04em;
    margin-bottom: .15rem;
}
</style>
"""


def apply_dashboard_style() -> None:
    """Apply small visual refinements for the Streamlit dashboard."""
    st.markdown(DASHBOARD_CSS, unsafe_allow_html=True)


def format_percent(value: float | None) -> str:
    """Format an optional percentage for dashboard metric cards."""
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value:.2f}%"


def format_money(value: float | None) -> str:
    """Format optional share prices for dashboard metric cards."""
    if value is None or pd.isna(value):
        return "n/a"
    return f"${value:,.2f}"


def render_hero() -> None:
    """Render the dashboard hero section."""
    st.markdown(
        """
        <section class="hero">
            <h1>Manufacturing Stock Tracker</h1>
            <p>Compare a manufacturing and industrial watchlist using real Twelve Data responses, validated processed CSVs, SQLite run history, and a repeatable momentum report.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_story(title: str, body: str) -> None:
    """Render a highlighted dashboard interpretation panel."""
    st.markdown(
        f"""
        <section class="story-panel">
            <div class="small-label">Market story</div>
            <strong>{title}</strong>
            <p>{body}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def data_status(path: Path, label: str) -> None:
    """Show a small status message for saved demo data."""
    if path.exists():
        st.markdown(
            f"<div class='evidence-note'>Using saved {label}: <code>{path}</code></div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"<div class='evidence-note'>No saved {label} found at <code>{path}</code>.</div>",
            unsafe_allow_html=True,
        )


def show_database_history() -> None:
    """Render recent quote snapshots saved in SQLite."""
    st.subheader("Saved SQLite Quote Runs")
    data_status(DB_PATH, "SQLite quote history database")
    runs = recent_quote_runs(DB_PATH, limit=8)
    if not runs:
        st.caption("No SQLite quote runs saved yet. Use Current quotes and enable database saving.")
        return
    st.dataframe(pd.DataFrame(runs), width="stretch", hide_index=True)


def show_quotes() -> None:
    """Render current quote metrics, tables, and comparison charts."""
    st.header("Current Quote Snapshot")
    data_status(QUOTE_PATH, "processed quote data")

    if not QUOTE_PATH.exists():
        st.info("No processed quote data found yet. Use the sidebar to collect data first.")
        show_database_history()
        return

    df = pd.read_csv(QUOTE_PATH)
    missing_columns = [column for column in QUOTE_COLUMNS if column not in df.columns]

    if missing_columns:
        st.error("Processed quote data is missing required column(s): " + ", ".join(missing_columns))
        show_database_history()
        return

    display_df = df.sort_values("symbol")
    summary = summarize(display_df.to_dict("records"))
    top_gainer = summary["top_gainer_symbol"] or "n/a"
    top_decliner = summary["top_decliner_symbol"] or "n/a"

    render_story("Latest quote direction", quote_story(summary))

    metric_cols = st.columns(5)
    metric_cols[0].metric("Symbols", summary["row_count"])
    metric_cols[1].metric("Average Price", format_money(summary["average_price"]))
    metric_cols[2].metric("Average Change", format_percent(summary["average_percent_change"]))
    metric_cols[3].metric("Top Gainer", top_gainer, format_percent(summary["top_gainer_percent_change"]))
    metric_cols[4].metric("Top Decliner", top_decliner, format_percent(summary["top_decliner_percent_change"]))

    st.divider()
    table_col, chart_col = st.columns([1.15, 1])
    with table_col:
        st.subheader("Watchlist Quotes")
        st.dataframe(
            display_df[QUOTE_COLUMNS].sort_values("percent_change", ascending=False),
            width="stretch",
            hide_index=True,
        )
    with chart_col:
        st.subheader("Percent Change")
        st.bar_chart(display_df.set_index("symbol")["percent_change"])

    with st.expander("Inspect processed quote evidence"):
        st.dataframe(display_df, width="stretch", hide_index=True)

    show_database_history()


def show_history() -> None:
    """Render historical momentum metrics, ranking table, and normalized trend."""
    st.header("Manufacturing Momentum Snapshot")
    status_cols = st.columns(2)
    with status_cols[0]:
        data_status(HISTORY_PATH, "processed historical data")
    with status_cols[1]:
        data_status(MOMENTUM_PATH, "processed momentum data")

    if not HISTORY_PATH.exists() or not MOMENTUM_PATH.exists():
        st.info("No processed historical data found yet. Use the sidebar to collect history first.")
        return

    history_df = pd.read_csv(HISTORY_PATH)
    momentum_df = pd.read_csv(MOMENTUM_PATH)
    quote_context_df = pd.read_csv(QUOTE_PATH) if QUOTE_PATH.exists() else None
    summary = momentum_summary(momentum_df)
    ranked_momentum = momentum_df.sort_values("period_return_percent", ascending=False)

    render_story("Peer momentum comparison", momentum_story(summary))

    context_cols = st.columns(2)
    with context_cols[0]:
        st.caption("Historical period: " + historical_period_label(momentum_df))
    with context_cols[1]:
        if quote_context_df is not None:
            st.caption("Quote context: " + quote_freshness_label(quote_context_df))
        else:
            st.caption("Quote context: no saved quote snapshot found.")

    metric_cols = st.columns(4)
    metric_cols[0].metric("Symbols", summary["symbol_count"])
    metric_cols[1].metric("Average Return", format_percent(summary["average_return_percent"]))
    metric_cols[2].metric("Strongest", summary["strongest_symbol"], format_percent(summary["strongest_return_percent"]))
    metric_cols[3].metric("Lowest Peer Return", summary["weakest_symbol"], format_percent(summary["weakest_return_percent"]))

    st.divider()
    trend_col, rank_col = st.columns([1.45, 1])
    with trend_col:
        st.subheader("Normalized Price Trend")
        st.caption(normalized_close_explanation())
        st.line_chart(normalized_close_table(history_df))
    with rank_col:
        st.subheader("Peer Momentum Ranking")
        st.caption("Ranked from strongest to weakest return over the collected historical window.")
        ranking_view = ranked_momentum[
            ["symbol", "period_return_percent", "price_range_percent", "observations"]
        ].rename(
            columns={
                "symbol": "Symbol",
                "period_return_percent": "Return %",
                "price_range_percent": "Range %",
                "observations": "Days",
            }
        )
        st.dataframe(ranking_view, width="stretch", hide_index=True)

    st.subheader("Return And Price Range")
    st.caption(
        "This compares return with price range. A wider range means the symbol moved through "
        "a larger high-low band during the collected period."
    )
    scatter_data = ranked_momentum.rename(
        columns={
            "period_return_percent": "Return %",
            "price_range_percent": "Range %",
        }
    )
    st.scatter_chart(scatter_data, x="Range %", y="Return %", color="symbol")

    selected_symbol = st.selectbox("Inspect one symbol", ranked_momentum["symbol"].tolist())
    detail = symbol_detail(selected_symbol, momentum_df, quote_context_df)
    detail_cols = st.columns(5)
    detail_cols[0].metric("Selected", detail["symbol"])
    detail_cols[1].metric("Period Return", format_percent(detail["period_return_percent"]))
    detail_cols[2].metric("Price Range", format_percent(detail["price_range_percent"]))
    detail_cols[3].metric("Latest Price", format_money(detail.get("price")))
    detail_cols[4].metric("Latest Change", format_percent(detail.get("percent_change")))
    if detail.get("name"):
        st.caption(f"{detail['symbol']} company context: {detail['name']}.")

    if quote_context_df is not None:
        st.subheader("Current Quote Context")
        quote_columns = [column for column in QUOTE_COLUMNS if column in quote_context_df.columns]
        st.dataframe(
            quote_context_df[quote_columns].sort_values("percent_change", ascending=False),
            width="stretch",
            hide_index=True,
        )

    with st.expander("Inspect processed historical evidence"):
        st.dataframe(history_df.sort_values(["symbol", "datetime"]), width="stretch", hide_index=True)
    with st.expander("Inspect processed momentum evidence"):
        st.dataframe(ranked_momentum, width="stretch", hide_index=True)


def collect_quote_data(symbols_input: str, api_key: str | None, save_db: bool) -> None:
    """Collect current quote data from the sidebar action."""
    if not api_key:
        st.error("Missing TWELVE_DATA_API_KEY. Copy .env.example to .env and add your API key.")
        return
    try:
        symbols = parse_symbols(symbols_input)
        db_path = DB_PATH if save_db else None
        batch = collect_symbols(symbols, api_key, DATA_DIR, db_path=db_path)
    except (TwelveDataError, StockDataError) as exc:
        st.error(str(exc))
    else:
        message = f"Collected {len(batch.rows)} quote rows for {', '.join(symbols)}."
        if batch.db_run_id:
            message += f" Saved SQLite run {batch.db_run_id}."
        st.success(message)


def collect_historical_data(symbols_input: str, api_key: str | None, outputsize: int) -> None:
    """Collect historical momentum data from the sidebar action."""
    if not api_key:
        st.error("Missing TWELVE_DATA_API_KEY. Copy .env.example to .env and add your API key.")
        return
    try:
        symbols = parse_symbols(symbols_input)
        batch = collect_history(symbols, api_key, DATA_DIR, outputsize)
    except (TwelveDataError, StockDataError) as exc:
        st.error(str(exc))
    else:
        st.success(f"Collected {len(batch.rows)} historical rows for {', '.join(symbols)}.")


def main() -> None:
    """Run the Streamlit dashboard application."""
    load_dotenv()
    st.set_page_config(page_title="Manufacturing Stock Tracker", layout="wide")
    apply_dashboard_style()
    render_hero()

    st.sidebar.header("Data Controls")
    mode = st.sidebar.radio("View", ["Historical momentum", "Current quotes"])
    symbols_input = st.sidebar.text_input("Ticker symbols", "CAT,DE,HON,GE,MMM")
    st.sidebar.caption(
        "Use saved processed data for the demo. Use collection buttons only when you want a fresh live API request."
    )
    save_db = st.sidebar.checkbox("Save new quote collections to SQLite", value=True)
    st.sidebar.caption(f"SQLite path: `{DB_PATH}`")
    api_key = os.environ.get("TWELVE_DATA_API_KEY")

    if mode == "Current quotes":
        if st.sidebar.button("Collect latest quote data"):
            collect_quote_data(symbols_input, api_key, save_db)
        show_quotes()
    else:
        outputsize = st.sidebar.slider("Historical days", min_value=5, max_value=90, value=30, step=5)
        if st.sidebar.button("Collect historical data"):
            collect_historical_data(symbols_input, api_key, outputsize)
        show_history()


main()
