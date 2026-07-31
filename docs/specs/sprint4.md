# Sprint 4: CI and Dashboard Polish

## Problem Statement

The project has a working Twelve Data pipeline, offline tests, logging, and a local dashboard. The next step is to make it more dependable for a final project by running tests automatically on GitHub and making the dashboard easier to understand during a demo.

## User Requirements

1. The user can trust that tests run automatically when project code is pushed to GitHub.
2. The user receives a clear error if Twelve Data does not return quote data for every requested ticker.
3. The dashboard highlights the watchlist's top gainer and top decliner.
4. The dashboard shows simple summary metrics before detailed tables.
5. The README explains the automated test workflow.

## Plan

Add a GitHub Actions workflow that installs the project with uv and runs pytest on push and pull requests. Strengthen the pipeline by checking that the processed API response contains every requested symbol. Improve the Streamlit dashboard with metric cards and clearer data-quality feedback while continuing to reuse the same project pipeline as the CLI.

## Tasks

1. Add `.github/workflows/tests.yml` for CI.
2. Add a helper that compares requested symbols with returned quote rows.
3. Make the pipeline fail clearly when requested symbols are missing from the API response.
4. Extend summary output with top gainer, top decliner, and counts of up/down/flat symbols.
5. Update CLI output to include the new summary fields.
6. Improve the dashboard layout with metric cards and sorted comparison tables.
7. Add tests for the missing-symbol quality check and new summary fields.
8. Update README with CI information.

## Out of Scope

- Publishing to PyPI.
- Replacing the CLI framework with Typer.
- Scheduling automated data collection.
- Database storage.
- Dashboard deployment.

## Definition of Done

- `uv run pytest` passes locally.
- CI workflow exists and runs `uv run pytest` on push and pull requests.
- Pipeline raises a clear `StockDataError` when requested symbols are missing from processed rows.
- Dashboard displays summary metrics for the current processed watchlist.
- README documents the local test command and GitHub Actions workflow.
