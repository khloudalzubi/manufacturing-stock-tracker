# Sprint 9: Dashboard Visual Polish

## Problem Statement

The dashboard communicates the project results, but it still feels too basic for a final project demo. The final screen-shared video needs a dashboard that looks intentional, professional, and easy to follow while preserving the same trusted data pipeline.

## User Requirements

1. The user sees a polished first screen centered on the manufacturing momentum question.
2. The user can scan key results from compact metric cards before reading tables.
3. The user can understand the main market story from a highlighted interpretation panel.
4. The user can compare normalized trend and momentum ranking without excessive scrolling.
5. The user can still inspect raw processed tables as evidence.

## Plan

Keep Streamlit as the dashboard framework and add modest custom CSS for visual hierarchy. Reorganize historical momentum as the primary view with a hero band, KPI cards, a story panel, side-by-side trend and ranking sections, and expandable evidence tables. Keep current quotes as a secondary but polished view.

## Tasks

1. Add dashboard CSS for page spacing, hero text, story panels, and evidence labels.
2. Add helper functions for styled sections and metric formatting.
3. Reorganize the historical momentum view around a demo-ready narrative flow.
4. Reorganize the current quote view with consistent panels and evidence tables.
5. Keep saved-data status visible for demos without live API calls.
6. Run the offline test suite.

## Out of Scope

- Changing API collection behavior.
- Adding new charting dependencies.
- Deploying the dashboard.
- Replacing Streamlit with another framework.
- Adding investment advice or predictive claims.

## Definition of Done

- Dashboard opens to a polished historical momentum view.
- Current quote and historical views still work from saved processed data.
- Saved data paths and evidence tables remain visible.
- The dashboard layout is stronger for a screen-shared final demo.
- `uv run pytest` passes without calling the live Twelve Data API.
