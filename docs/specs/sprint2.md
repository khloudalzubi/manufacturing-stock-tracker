# Sprint 2: Trust the Twelve Data Boundary

## Problem Statement

The project can call Twelve Data and save quote data, but it needs stronger validation and tests before it grows into a larger course project. The next sprint should make the data pipeline safer, easier to trust, and testable without depending on the live API.

## User Requirements

1. The user receives a clear error when Twelve Data returns an unusable response.
2. The user can trust that processed quote rows have required fields such as symbol and close price.
3. The project can be tested without contacting the live Twelve Data API.
4. The project includes sample fixture data that represents a Twelve Data quote response.
5. The tool keeps API keys out of saved data, logs, and committed files.

## Plan

Add validation around the boundary where external data enters the project. Keep API access separate from processing so tests can use fixture JSON and mocked HTTP responses instead of making network requests. Focus tests on stable behavior: requesting a watchlist, turning Twelve Data quote JSON into rows, summarizing prices, and failing clearly when required fields are missing.

## Tasks

1. Create committed fixture JSON that looks like a Twelve Data quote response.
2. Add Pydantic models for incoming quote data.
3. Validate response data before writing processed CSV output.
4. Add tests for successful quote processing.
5. Add tests for missing fields, invalid numeric values, and API failure responses.
6. Add logging that can write to the console and a local file without exposing secrets.

## Out of Scope

- Calling the live API from tests.
- Full historical trend analysis.
- Database storage.
- Dashboard design beyond verifying that the shared pipeline can support it.
- Financial recommendations.

## Definition of Done

- `uv run pytest` passes without calling the live Twelve Data API.
- Tests cover successful mocked API responses and failed responses.
- Pydantic validation rejects malformed quote data with a clear error.
- Logging can be controlled with command-line options.
- Logs do not include the API key.
