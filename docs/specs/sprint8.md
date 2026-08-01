# Sprint 8: Dashboard Story Polish

## Problem Statement

The project has a working dashboard, but the final demo needs the dashboard to communicate the manufacturing-sector question quickly to a viewer. The dashboard should make it obvious what data is being shown, whether it is using saved data or live API collection, and what the historical momentum result means.

## User Requirements

1. The user can immediately see the dashboard's main analytical question.
2. The user can use saved processed data for a demo without making a live API request.
3. The dashboard explains normalized close values in user-friendly language.
4. The dashboard highlights a short interpretation of the strongest and weakest momentum results.
5. The dashboard keeps using shared project logic instead of duplicating analysis formulas.

## Plan

Move reusable dashboard story helpers into the reporting layer, then update the Streamlit dashboard to use those helpers. Keep the current quote and historical workflows intact. Add clearer section names, saved-data status messages, and a compact interpretation panel for the historical momentum view.

## Tasks

1. Add reporting helpers for quote and momentum story text.
2. Reuse the existing normalized close helper in the dashboard.
3. Update the dashboard title, captions, sidebar labels, and data-source status messages.
4. Add a historical interpretation panel that summarizes the strongest, weakest, and overall direction.
5. Add tests for the new story helpers.
6. Run the offline test suite.

## Out of Scope

- New API provider changes.
- New financial indicators beyond the existing quote and momentum summaries.
- Forecasting or investment recommendations.
- Dashboard deployment.
- Changing the committed data evidence.

## Definition of Done

- The dashboard can still show current quotes and historical momentum.
- Historical mode includes a plain-language interpretation of the momentum result.
- Saved-data behavior is clear enough for a screen-recorded demo.
- Dashboard calculations come from shared processing/reporting helpers.
- `uv run pytest` passes without calling the live Twelve Data API.
