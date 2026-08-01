# Sprint 10: Persistent Watchlist History With SQLite

## Problem Statement

The tracker saves raw JSON and processed CSV evidence for each run, but a real market monitor should also be able to accumulate repeated watchlist snapshots over time. Adding a small local SQLite database makes the project more useful and gives the final project a self-taught capability beyond the course floor.

## User Requirements

1. The user can optionally save quote collection runs to a local SQLite database.
2. The user can keep repeated watchlist snapshots without replacing the latest CSV files.
3. The dashboard can show recent saved database runs for demo and inspection.
4. The database feature does not store API keys or require live API calls in tests.
5. Existing raw JSON and processed CSV outputs continue to work as before.

## Plan

Add a small `storage.py` module using Python's standard `sqlite3` library. Keep database persistence optional through a CLI flag and dashboard checkbox. Store quote run metadata and quote rows in normalized tables. Use temporary databases in tests so the feature is fully covered without contacting Twelve Data.

## Tasks

1. Add SQLite schema creation for quote runs and quote rows.
2. Add helper functions to save quote rows and load recent run summaries.
3. Add optional database persistence to the quote collection pipeline.
4. Add CLI options for saving to SQLite and choosing a database path.
5. Add dashboard controls and a recent-run history table.
6. Add tests for storage and pipeline integration using temporary SQLite files.
7. Update README and data dictionary with the database feature.

## Out of Scope

- Replacing CSV outputs.
- Storing API keys or raw secrets in the database.
- Historical price database persistence.
- Database migrations beyond the first schema.
- Multi-user or server database deployment.

## Definition of Done

- `uv run pytest` passes without calling the live Twelve Data API.
- The CLI can save quote runs with `--save-db`.
- The dashboard can display recent saved SQLite quote runs.
- CSV and raw JSON outputs still work.
- README explains why SQLite was added and how to use it.
