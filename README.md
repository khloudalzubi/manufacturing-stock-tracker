# Manufacturing Stock Tracker

Manufacturing Stock Tracker is a command-line data tool that collects daily stock data for selected manufacturing and industrial companies, saves the raw API response as evidence, and writes a processed CSV for analysis.

## API

This project uses the Alpha Vantage API, especially the Time Series Daily endpoint.

Docs: https://www.alphavantage.co/documentation/

Example request:

```text
https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=CAT&outputsize=compact&apikey=YOUR_KEY
```

The response contains metadata about the request and a daily time series with open, high, low, close, and volume values.

## What This Will Build

This project will become a reproducible tool for comparing selected manufacturing company stock trends and preparing the data for a dashboard or report.

## Setup

```bash
uv sync
cp .env.example .env
```

Add your Alpha Vantage API key to `.env`:

```env
ALPHA_VANTAGE_API_KEY=your_real_key_here
```

## Run

Fetch Caterpillar daily stock data:

```bash
uv run manufacturing-stock-tracker --symbol CAT
```

Fetch another manufacturing company:

```bash
uv run manufacturing-stock-tracker --symbol DE
```

The command saves files under:

```text
data/raw/
data/processed/
```

The `data/` folder is ignored by Git because it contains generated API output.
