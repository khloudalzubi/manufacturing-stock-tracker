# AGENTS.md

## Project Purpose

Manufacturing Stock Tracker is a Python data tool for comparing a watchlist of manufacturing and industrial stocks. It pulls quote and historical price data from Twelve Data, saves raw API responses as evidence, creates processed CSV outputs, and presents the results through a CLI and Streamlit dashboard.

The main analytical question is: which major manufacturing and industrial companies show the strongest recent stock momentum compared with their peers?

## Setup

Use `uv` for environment and dependency management.

```bash
uv sync
cp .env.example .env
```

Add a local Twelve Data API key to `.env`:

```env
TWELVE_DATA_API_KEY=your_real_key_here
```

Never commit `.env` or real API keys.

## Common Commands

Run the offline test suite:

```bash
uv run pytest
```

Collect current quote data:

```bash
uv run manufacturing-stock-tracker --symbols CAT,DE,HON,GE,MMM
```

Collect historical momentum data:

```bash
uv run manufacturing-stock-tracker --symbols CAT,DE,HON,GE,MMM --history --history-outputsize 30
```

Run the dashboard:

```bash
uv run streamlit run src/manufacturing_stock_tracker/dashboard.py
```

Build package artifacts:

```bash
uv build
```

Render the Quarto report after the report exists:

```bash
uv run quarto render reports/manufacturing_momentum.qmd --to pdf
```

## Repository Navigation

- `src/manufacturing_stock_tracker/api.py`: Twelve Data HTTP boundary and sanitized API errors.
- `src/manufacturing_stock_tracker/models.py`: Pydantic models for incoming Twelve Data responses.
- `src/manufacturing_stock_tracker/process.py`: validation, row conversion, data-quality checks, and summaries.
- `src/manufacturing_stock_tracker/pipeline.py`: shared workflows used by both CLI and dashboard.
- `src/manufacturing_stock_tracker/cli.py`: command-line interface.
- `src/manufacturing_stock_tracker/dashboard.py`: local Streamlit dashboard.
- `tests/`: offline tests using fixtures and mocks; tests must not call the live API.
- `tests/fixtures/`: committed sample API responses for repeatable tests.
- `docs/`: sprint specs, data dictionary, and practicum notes.
- `reports/`: Quarto report source and rendered PDF.
- `data/raw/`: raw API responses used as evidence for the course submission.
- `data/processed/`: processed CSV outputs used by the dashboard and report.

## Source Of Truth

Project logic should live in `src/manufacturing_stock_tracker/`. The CLI, dashboard, and report should call reusable project functions rather than duplicating parsing, validation, or analysis logic.

The report should use committed data and project functions. Do not recreate momentum formulas in report cells if the function already exists in `process.py`.

## Testing And Data Rules

Tests must pass without a live API call. Use fixtures and monkeypatch/mocks for API-boundary behavior.

Runtime code should fail clearly when:

- required API response fields are missing,
- numeric values cannot be parsed,
- Twelve Data returns a symbol-level error,
- requested symbols are missing from returned rows,
- empty data would be saved or summarized.

## Documentation Conventions

Keep documentation specific and direct. README should give the fastest path to a working result, then link to detailed docs. The data dictionary defines structured output fields. Docstrings should explain purpose, inputs, outputs, and important failure behavior without repeating obvious code.
