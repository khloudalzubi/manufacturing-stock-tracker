# Manufacturing Stock Tracker

Manufacturing Stock Tracker is a reproducible Python data tool for comparing a watchlist of manufacturing and industrial stocks. It collects real quote and historical price data from Twelve Data, keeps raw JSON responses as evidence, writes processed CSV files, and presents the results through a command-line interface, Streamlit dashboard, and Quarto report.

The main analytical question is: which major manufacturing and industrial companies show the strongest recent stock momentum compared with their peers?

## API

This project uses the Twelve Data API.

Docs: https://twelvedata.com/docs

Example quote request:

```text
https://api.twelvedata.com/quote?symbol=CAT,DE,HON&apikey=YOUR_KEY
```

The quote response contains one object per ticker with fields such as symbol, company name, exchange, currency, datetime, open, high, low, close, volume, previous close, change, and percent change. The project also uses Twelve Data's `/time_series` endpoint to collect daily historical prices for momentum comparisons.

## Why Twelve Data

The project started with Alpha Vantage, but its free request limit made multi-ticker collection difficult. Financial Modeling Prep was tested next, but the batch quote endpoint returned `HTTP 402 Payment Required` for the available key/plan. Twelve Data is a better fit for the project direction because its documentation supports comma-separated symbols for the `/quote` endpoint.

## Documentation

- [Data dictionary](docs/data-dictionary.md)
- [Contributor and agent guidance](AGENTS.md)
- [Release checklist](docs/release-checklist.md)
- [License](LICENSE)
- [Sprint specs](docs/specs/)
- [Report source](reports/manufacturing_momentum.qmd) and [rendered PDF](reports/manufacturing_momentum.pdf)

## Setup From Source

Clone the repository, install dependencies, and create a local environment file:

```bash
git clone https://github.com/khloudalzubi/manufacturing-stock-tracker.git
cd manufacturing-stock-tracker
uv sync
cp .env.example .env
```

Add a Twelve Data API key to `.env`:

```env
TWELVE_DATA_API_KEY=your_real_key_here
```

`.env` is ignored by Git and should never be committed.

## Run The CLI

Show command help:

```bash
uv run manufacturing-stock-tracker --help
```

Show the installed package version:

```bash
uv run manufacturing-stock-tracker --version
```

Fetch the default manufacturing watchlist:

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

Save quote runs to a local SQLite database while still writing raw and processed files:

```bash
uv run manufacturing-stock-tracker --symbols CAT,DE,HON,GE,MMM --save-db
```

Write console and file logs:

```bash
uv run manufacturing-stock-tracker --symbols CAT,DE,HON --log-level DEBUG --log-file logs/tracker.log
```

The command saves raw evidence and processed outputs under:

```text
data/raw/
data/processed/
```

SQLite persistence is optional. When enabled, quote run summaries and quote rows are stored in `data/tracker.db`, which is ignored by Git because it is generated local history.

Historical collection also writes:

```text
data/processed/manufacturing_watchlist_history.csv
data/processed/manufacturing_watchlist_momentum.csv
```

The `logs/` folder is ignored by Git because it contains generated local output. For course review, the current `data/` folder is committed as evidence, but `.env` remains ignored because it contains the API key.

## Data Quality

The pipeline validates Twelve Data responses with Pydantic before writing processed CSV output. It also checks that every requested symbol appears in the returned quote or history rows. If Twelve Data omits a requested ticker, returns an error, or sends required numeric fields that cannot be parsed, the command fails clearly instead of silently saving incomplete data.

## Dashboard

Run the local Streamlit dashboard:

```bash
uv run streamlit run src/manufacturing_stock_tracker/dashboard.py
```

The dashboard uses the same collection, processing, and optional SQLite persistence logic as the command-line tool. It can collect data from Twelve Data when `.env` contains an API key, and it can display processed CSV files already saved in `data/processed/`. It highlights average price, top gainer, top decliner, and how many watchlist symbols are up, down, or flat. In historical mode, it shows normalized close-price trends and ranks symbols by period return so the watchlist becomes a short manufacturing-sector momentum story.

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

## Package Build And Release Evidence

Build the package artifacts required for the course project:

```bash
uv build --no-sources
```

This creates a wheel ending in `.whl` and a source archive ending in `.tar.gz` under `dist/`. Attach both files to the exact GitHub Release submitted for grading.

The package installs the command:

```text
manufacturing-stock-tracker
```

Build artifacts are written to `dist/`, which is ignored by Git. Before a final release, verify the package with tests, `--version`, `uv build --no-sources`, and the release checklist. Publishing to TestPyPI or PyPI is optional.

## Demo Path

A concise demo can show the project in this order:

1. README purpose and API source.
2. `uv run pytest` to show offline tests.
3. `uv run manufacturing-stock-tracker --version` to show package identity.
4. CLI quote or historical collection command.
5. Raw and processed files in `data/`.
6. Streamlit dashboard.
7. Quarto PDF report.
