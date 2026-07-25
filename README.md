# Manufacturing Stock Tracker

Manufacturing Stock Tracker is a command-line data tool that collects quote data for a manufacturing stock watchlist, saves the raw API response as evidence, and writes processed CSV files for analysis and dashboard use.

## API

This project uses the Twelve Data API, especially the quote endpoint.

Docs: https://twelvedata.com/docs

Example request:

```text
https://api.twelvedata.com/quote?symbol=CAT,DE,HON&apikey=YOUR_KEY
```

The response contains one quote object per ticker with fields such as symbol, company name, exchange, currency, datetime, open, high, low, close, volume, previous close, change, and percent change.

## Why Twelve Data

The project started with Alpha Vantage, but its free request limit made multi-ticker collection difficult. Financial Modeling Prep was tested next, but the batch quote endpoint returned `HTTP 402 Payment Required` for the available key/plan. Twelve Data is a better fit for the project direction because its documentation supports comma-separated symbols for the `/quote` endpoint.

## What This Will Build

This project will become a reproducible manufacturing market watchlist for comparing selected manufacturing and industrial companies in a dashboard or report.

## Setup

```bash
uv sync
cp .env.example .env
```

Add your Twelve Data API key to `.env`:

```env
TWELVE_DATA_API_KEY=your_real_key_here
```

## Run

Fetch a default manufacturing watchlist:

```bash
uv run manufacturing-stock-tracker
```

Fetch one company:

```bash
uv run manufacturing-stock-tracker --symbol CAT
```

Fetch a manufacturing watchlist in one API request:

```bash
uv run manufacturing-stock-tracker --symbols CAT,DE,HON,GE,MMM
```

Write console and file logs:

```bash
uv run manufacturing-stock-tracker --symbols CAT,DE,HON --log-level DEBUG --log-file logs/tracker.log
```

The command saves files under:

```text
data/raw/
data/processed/
```

The `data/` and `logs/` folders are ignored by Git because they contain generated local output.

## Dashboard

Run the local Streamlit dashboard:

```bash
uv run streamlit run src/manufacturing_stock_tracker/dashboard.py
```

The dashboard uses the same collection and processing logic as the command-line tool. It can collect data from Twelve Data when `.env` contains an API key, and it can display processed CSV files already saved in `data/processed/`.

## Test

Run the offline test suite:

```bash
uv run pytest
```

The tests use fixture data and mocked API responses. They do not call the live Twelve Data API.
