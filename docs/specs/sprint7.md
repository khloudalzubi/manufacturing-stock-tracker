# Sprint 7: Release And Demo Readiness

## Problem Statement

The project works as a local data tool, but the final course project must be easy for someone else to install, run, test, and evaluate from the public repository. The next sprint should make the project more release-ready without changing its core manufacturing momentum analysis.

## User Requirements

1. The user can check the installed package version from the command line.
2. A new user can understand how to install and run the project from the README.
3. The package metadata clearly describes the project, license, repository, and audience.
4. The project can be built into Python package artifacts for a GitHub Release.
5. The release process includes a short checklist for final verification before tagging or publishing.

## Plan

Keep the release work focused on packaging, documentation, and repeatable verification. Add a single shared version value, expose it through the CLI, improve package metadata in `pyproject.toml`, and document the install/build/check path in README and a release checklist. Avoid changing the API workflow, dashboard analysis, or report logic unless verification reveals a problem.

## Tasks

1. Add a package version constant that can be reused by the CLI and package exports.
2. Add a `--version` command-line option.
3. Add tests for version behavior and package metadata expectations.
4. Improve `pyproject.toml` metadata for package publication readiness.
5. Add README guidance for installing from source, building package artifacts, and checking release readiness.
6. Add a concise release checklist under `docs/`.
7. Run tests and package build verification.

## Out of Scope

- Publishing to TestPyPI or PyPI in this sprint.
- Changing the selected API provider.
- Adding new financial indicators or forecasting.
- Redesigning the dashboard.
- Changing committed data evidence.

## Definition of Done

- `uv run pytest` passes without calling the live Twelve Data API.
- `uv run manufacturing-stock-tracker --version` prints the package version.
- `uv build --no-sources` creates the required wheel and source archive successfully.
- README explains the source install, test, build, and release-readiness path.
- Release checklist records the remaining steps before final submission and GitHub Release attachment.
