# Sprint 5: Packaging Readiness

## Problem Statement

The project must eventually be installable and published to PyPI. Before publishing, the package should build cleanly, document the packaging workflow, and give a stranger enough information to understand how the command-line entry point is distributed.

## User Requirements

1. The user can build the project into standard Python package artifacts.
2. The user can identify the command installed by the package.
3. The README explains how to run tests before building.
4. The README explains how to build the package locally.
5. Generated build artifacts stay out of Git until a release process needs them.

## Plan

Keep this sprint focused on package readiness rather than actual PyPI publishing. Verify the existing `pyproject.toml` metadata and console script, add README instructions for local builds, ignore generated build artifacts, and run `uv build` to confirm that the package creates a wheel and source distribution.

## Tasks

1. Review `pyproject.toml` package metadata and console script configuration.
2. Add `dist/` and build metadata folders to `.gitignore`.
3. Update README with a packaging section.
4. Run `uv run pytest` before building.
5. Run `uv build` and inspect generated artifacts.
6. Confirm the repository still keeps secrets and generated data out of Git.

## Out of Scope

- Publishing to PyPI.
- Creating a GitHub release.
- Changing the package name.
- Adding Typer or Rich CLI output.
- Dashboard deployment.

## Definition of Done

- `uv run pytest` passes.
- `uv build` creates a wheel and source distribution under `dist/`.
- README documents the package build command.
- `.gitignore` excludes generated package artifacts.
- No secrets, generated data, logs, or virtual environments are staged for Git.
