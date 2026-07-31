# Sprint 6: Historical Manufacturing Momentum

## Problem Statement

The project currently shows current quote data for a manufacturing watchlist. To make the final project more analytical, it should compare recent historical movement and answer a clearer sector question: which manufacturing companies have shown the strongest short-term stock momentum?

## User Requirements

1. The user can collect historical daily prices for the manufacturing watchlist.
2. The tool saves raw historical Twelve Data responses as evidence.
3. The tool writes processed historical price rows for analysis.
4. The tool calculates each symbol's return over the collected period.
5. The dashboard compares symbols with a normalized historical price chart.

## Plan

Add a historical workflow beside the existing current-quote workflow. Use Twelve Data's `/time_series` endpoint with `interval=1day` and a configurable `outputsize`. Keep the same project architecture: API calls in `api.py`, runtime validation in `models.py` and `process.py`, shared workflow in `pipeline.py`, CLI access in `cli.py`, and dashboard presentation in Streamlit.

## Tasks

1. Add a Twelve Data time-series API client function.
2. Add Pydantic models for historical time-series responses.
3. Convert historical responses into processed CSV rows.
4. Calculate momentum summary rows with start close, end close, return, and observation count.
5. Add CLI options for historical collection.
6. Add dashboard controls and charts for historical momentum.
7. Add offline fixtures and tests for historical processing and controlled API behavior.
8. Update README with the historical comparison question and commands.

## Out of Scope

- Investment advice.
- Intraday trading signals.
- Forecasting future prices.
- Database storage.
- Automatically scheduled collection.

## Definition of Done

- `uv run pytest` passes without calling the live Twelve Data API.
- The CLI can collect quote data and historical momentum data.
- Raw historical responses are saved in `data/raw/`.
- Processed historical rows and momentum summaries are saved in `data/processed/`.
- The dashboard can display a normalized historical trend and momentum table.
- README explains the manufacturing-sector question and historical workflow.
