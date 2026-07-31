# Manufacturing Stock Tracker

Manufacturing Stock Tracker is a command-line data tool that collects quote data for a manufacturing stock watchlist, saves the raw API response as evidence, and writes processed CSV files for analysis and dashboard use.

## API

This project uses the Twelve Data API, especially the quote endpoint.

Docs: https://twelvedata.com/docs

Example request:

```text
https://api.twelvedata.com/quote?symbol=CAT,DE,HON&apikey=YOUR_KEY
```

The quote response contains one object per ticker with fields such as symbol, company name, exchange, currency, datetime, open, high, low, close, volume, previous close, change, and percent change. The project also uses Twelve Data's `/time_series` endpoint to collect daily historical prices for momentum comparisons.

## Why Twelve Data

The project started with Alpha Vantage, but its free request limit made multi-ticker collection difficult. Financial Modeling Prep was tested next, but the batch quote endpoint returned `HTTP 402 Payment Required` for the available key/plan. Twelve Data is a better fit for the project direction because its documentation supports comma-separated symbols for the `/quote` endpoint.

## What This Will Build

This project is becoming a reproducible manufacturing market monitor. Its main analytical question is: which major manufacturing and industrial companies show the strongest recent stock momentum compared with their peers?


## Documentation

- [Data dictionary](docs/data-dictionary.md)
- [Contributor and agent guidance](AGENTS.md)
- [License](LICENSE)
- [Sprint specs](docs/specs/)
- [Report source](reports/manufacturing_momentum.qmd) and [rendered PDF](reports/manufacturing_momentum.pdf)

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

Collect historical daily prices and calculate recent momentum:

```bash
uv run manufacturing-stock-tracker --symbols CAT,DE,HON,GE,MMM --history --history-outputsize 30
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

Historical collection also writes:

```text
data/processed/manufacturing_watchlist_history.csv
data/processed/manufacturing_watchlist_momentum.csv
```

The `logs/` folder is ignored by Git because it contains generated local output. For Practicum 6, the current `data/` folder is committed as review evidence, but `.env` remains ignored because it contains the API key.

## Data Quality

The pipeline validates Twelve Data responses with Pydantic before writing processed CSV output. It also checks that every requested symbol appears in the returned quote rows. If Twelve Data omits a requested ticker, the command fails clearly instead of silently saving an incomplete watchlist.

## Dashboard

Run the local Streamlit dashboard:

```bash
uv run streamlit run src/manufacturing_stock_tracker/dashboard.py
```

The dashboard uses the same collection and processing logic as the command-line tool. It can collect data from Twelve Data when `.env` contains an API key, and it can display processed CSV files already saved in `data/processed/`. It highlights summary metrics such as average price, top gainer, top decliner, and how many watchlist symbols are up, down, or flat. In historical mode, it shows normalized close-price trends and ranks symbols by period return so the watchlist becomes a short manufacturing-sector momentum story.


## Report

The reproducible report answers the project's main analytical question using the committed Twelve Data outputs:

```text
Which major manufacturing and industrial companies show the strongest recent stock momentum compared with their peers?
```

Report source:

```text
reports/manufacturing_momentum.qmd
```

Rendered PDF:

```text
reports/manufacturing_momentum.pdf
```

Rebuild the PDF from PowerShell after `uv sync`:

```powershell
$env:QUARTO_PYTHON = (Resolve-Path .venv\Scripts\python.exe).Path
quarto render reports\manufacturing_momentum.qmd --to pdf
```

## Test

Run the offline test suite:

```bash
uv run pytest
```

The tests use fixture data and mocked API responses. They do not call the live Twelve Data API. The GitHub Actions workflow in `.github/workflows/tests.yml` runs `uv run pytest` automatically on push and pull requests.

## Package Build

Run tests before building package artifacts:

```bash
uv run pytest
```

Build the package locally:

```bash
uv build
```

The package installs the command:

```text
manufacturing-stock-tracker
```

Build artifacts are written to `dist/`, which is ignored by Git. The final project will later need to publish a release package to PyPI.
