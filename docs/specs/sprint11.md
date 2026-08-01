# Sprint 11: Dashboard Analytical Depth

## Problem Statement

The dashboard looks more polished, but it still does not show enough context for a final project demo. A viewer should be able to understand the momentum result, inspect supporting quote data, compare risk and return, and drill into one company without leaving the dashboard.

## User Requirements

1. The user can see data freshness and historical period coverage.
2. The user can compare return and price range side by side.
3. The user can inspect current quote context next to historical momentum.
4. The user can select one symbol and see a focused detail panel.
5. The dashboard remains usable from saved processed data without live API calls.

## Plan

Use existing processed CSV outputs to add more dashboard context. Add richer summary rows, a risk-return scatter plot, quote snapshot table, and selected-symbol detail panel. Keep data collection and validation unchanged.

## Tasks

1. Add helper functions for data freshness, period label, and selected-symbol details.
2. Add a risk-return chart using momentum return and price range.
3. Add a current quote context section to the historical dashboard view.
4. Add a selected-symbol detail panel.
5. Keep evidence expanders for processed data.
6. Run the offline test suite.

## Out of Scope

- New API requests.
- Forecasting or investment recommendations.
- Portfolio optimization.
- New database schema.
- Dashboard deployment.

## Definition of Done

- Historical dashboard view shows period coverage and quote freshness.
- Historical dashboard view includes return/range comparison and selected-symbol detail.
- Dashboard still works with saved CSV files.
- `uv run pytest` passes without calling the live Twelve Data API.
