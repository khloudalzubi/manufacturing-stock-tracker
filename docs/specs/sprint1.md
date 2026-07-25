# Sprint 1: Twelve Data Watchlist Foundation

## Problem Statement

Build a Python command-line tool that collects quote data for a manufacturing stock watchlist, saves the raw API response as evidence, and creates a processed CSV for later dashboard/report use.

## User Requirements

1. The user can provide one ticker or a comma-separated list of manufacturing ticker symbols.
2. The tool calls Twelve Data for the selected symbols.
3. The tool saves the raw Twelve Data response in `data/raw/`.
4. The tool writes cleaned quote rows to `data/processed/`.
5. The project includes clear setup and run instructions.

## Plan

Keep the first sprint focused on a reliable project foundation. The command should use Twelve Data because it supports comma-separated symbols for quote requests, which fits the manufacturing watchlist direction better than the earlier Alpha Vantage and FMP attempts. Separate API access, processing, and command-line behavior so later sprints can add validation, tests, logging, and a dashboard without rewriting the project.

## Tasks

1. Configure the project as a uv command-line package.
2. Add `.env.example` with a placeholder `TWELVE_DATA_API_KEY`.
3. Read the real API key from `.env` without committing it.
4. Call the Twelve Data quote endpoint for the requested watchlist.
5. Save the raw JSON response under `data/raw/`.
6. Save processed quote data under `data/processed/`.
7. Document setup, example requests, and run commands in README.

## Out of Scope

- Trading or broker account integration.
- Investment advice or buy/sell recommendations.
- Long-term storage in a database.
- Automated scheduling.
- A deployed dashboard.

## Definition of Done

- The command runs through `uv run manufacturing-stock-tracker`.
- The command can request multiple manufacturing tickers in one run.
- Raw API output is saved in `data/raw/`.
- Processed CSV output is saved in `data/processed/`.
- `.env`, `.venv/`, `data/`, and `logs/` are ignored by Git.
- README explains the API, API docs link, example request, setup, run command, and project direction.
