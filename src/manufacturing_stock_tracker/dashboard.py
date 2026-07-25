from pathlib import Path
import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from manufacturing_stock_tracker.api import TwelveDataError
from manufacturing_stock_tracker.pipeline import collect_symbols
from manufacturing_stock_tracker.process import StockDataError, parse_symbols


load_dotenv()

DATA_DIR = Path("data")
PROCESSED_PATH = DATA_DIR / "processed" / "manufacturing_watchlist_quotes.csv"

st.set_page_config(page_title="Manufacturing Market Monitor", layout="wide")
st.title("Manufacturing Market Monitor")
st.caption("Twelve Data quote data for selected manufacturing and industrial companies.")

symbols_input = st.sidebar.text_input("Ticker symbols", "CAT,DE,HON,GE,MMM")
collect = st.sidebar.button("Collect latest quote data")
api_key = os.environ.get("TWELVE_DATA_API_KEY")

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

available_files = sorted((DATA_DIR / "processed").glob("*.csv")) if (DATA_DIR / "processed").exists() else []
selected_file = PROCESSED_PATH if PROCESSED_PATH.exists() else None

if not selected_file and available_files:
    selected_file = available_files[0]

if not selected_file:
    st.info("No processed quote data found yet. Use the sidebar to collect data first.")
else:
    file_options = {path.name: path for path in available_files}
    default_index = list(file_options.values()).index(selected_file) if selected_file in file_options.values() else 0
    selected_name = st.sidebar.selectbox("Processed data file", list(file_options), index=default_index)
    selected_file = file_options[selected_name]

    df = pd.read_csv(selected_file)
    display_df = df.sort_values("symbol")

    st.subheader("Latest Watchlist Quotes")
    st.dataframe(
        display_df[["symbol", "name", "exchange", "currency", "price", "percent_change", "volume"]],
        width="stretch",
        hide_index=True,
    )

    st.subheader("Price by Symbol")
    st.bar_chart(display_df.set_index("symbol")["price"])

    st.subheader("Percent Change by Symbol")
    st.bar_chart(display_df.set_index("symbol")["percent_change"])

    st.subheader("Processed Data")
    st.dataframe(display_df, width="stretch", hide_index=True)
