# Sprint 3: Streamlit Manufacturing Watchlist Dashboard

## Problem Statement

The project has a tested Twelve Data quote pipeline, but the results need to be visible in a form that is useful for reviewing several manufacturing companies at once. This sprint adds a local dashboard while keeping the command-line workflow intact.

## User Requirements

1. The user can enter multiple manufacturing ticker symbols in the dashboard.
2. The dashboard can collect the latest quote data through the same project logic as the CLI.
3. The dashboard displays the latest watchlist quotes in a table.
4. The dashboard includes simple visuals for price and percent-change comparisons.
5. The dashboard can load processed CSV output that already exists locally.

## Plan

Build a Streamlit dashboard on top of the shared collection pipeline instead of duplicating API and processing logic. Keep the dashboard local for this practicum. Use the dashboard to show the project direction: a manufacturing market watchlist that can compare multiple companies from one Twelve Data response.

## Tasks

1. Add Streamlit as a dependency.
2. Create `src/manufacturing_stock_tracker/dashboard.py`.
3. Reuse `collect_symbols` from the pipeline.
4. Add sidebar controls for ticker input and collection.
5. Display processed quote rows in a table.
6. Add bar charts for current price and percent change.
7. Update README with dashboard instructions.

## Out of Scope

- Dashboard deployment.
- User authentication.
- Investment advice.
- Real-time streaming data.
- Complex portfolio analytics.

## Definition of Done

- `uv run streamlit run src/manufacturing_stock_tracker/dashboard.py` starts the dashboard locally.
- The dashboard uses the same pipeline as the CLI.
- The dashboard can display processed Twelve Data quote CSV data.
- CLI behavior from earlier sprints still works.
- Tests still pass.
