# Sprint 1: Reliable Alpha Vantage Data Pipeline

## Problem Statement

Build on the first Alpha Vantage command-line tool so the project can reliably collect, validate, and process manufacturing stock data in a way that is safe to grow into the final course project.

## User Requirements

1. The user can run the project as a repeatable command for a stock ticker.
2. The tool saves the raw Alpha Vantage response in `data/raw/`.
3. The tool saves a processed CSV version in `data/processed/`.
4. The tool fails clearly when the API key is missing or the API response is not usable.
5. The project includes enough documentation for another person to install and run the first version.

## Plan

Keep the first sprint narrow and focused on the foundation. The command should continue to use Alpha Vantage daily stock data for a manufacturing-related ticker such as `CAT`. The code should separate API access, processing, and command-line behavior so later sprints can add tests, multiple tickers, richer summaries, and a dashboard without rewriting the whole project.

## Tasks

1. Confirm the `uv` project runs through the configured command.
2. Confirm `.env.example` exists and `.env` is ignored by Git.
3. Confirm generated API output is written under `data/raw/` and `data/processed/`.
4. Confirm `data/`, `.env`, and `.venv/` are ignored by Git.
5. Review README setup and run instructions for a new user.
6. Run the command with a real Alpha Vantage key and inspect the generated output.

## Out of Scope

- Multi-ticker comparison.
- Dashboard or report generation.
- Automated tests and GitHub Actions.
- PyPI publishing.
- Long-term data storage beyond generated raw and processed files.

## Definition of Done

- The repository is a clean `uv` project with a command entry point.
- The command successfully calls Alpha Vantage for at least one ticker.
- The command saves one raw JSON response and one processed CSV locally.
- Secrets and generated data are excluded from Git.
- README explains the API, example request, response contents, setup, and run command.
- The first sprint is committed and pushed to the public GitHub repository.
