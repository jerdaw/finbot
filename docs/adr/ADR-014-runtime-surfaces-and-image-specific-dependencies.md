# ADR-014: Separate Runtime Surfaces and Image-Specific Dependencies

**Status:** Accepted
**Date:** 2026-03-23

## Context

Finbot's Python dependency set had grown into a single broad runtime surface that mixed:

- core CLI/runtime functionality
- Streamlit dashboard dependencies
- FastAPI backend dependencies
- NautilusTrader dependencies
- notebook tooling

That approach had three concrete problems:

1. The default install and root Docker image carried packages that many runtime paths never used.
2. Scheduled Docker security scans reported vulnerabilities from optional application surfaces,
   creating recurring noise and unnecessary update churn.
3. The backend container referenced a nonexistent `web` dependency group instead of a declared
   package extra, which made the packaging model inconsistent between local installs and Docker.

## Decision

### Base install is the core CLI/runtime surface

`project.dependencies` remains the default install target for the core CLI/runtime path only.
Packages that are clearly dashboard-only, backend-only, notebook-only, or Nautilus-only move to
explicit extras.

### Optional surfaces use named extras

The package exposes these extras:

- `dashboard` for Streamlit support
- `web` for FastAPI, Pydantic, Pydantic Settings, and Uvicorn
- `nautilus` for NautilusTrader
- `notebooks` for Jupyter

Contributor and CI installs use `uv sync --all-extras` so the full repository remains easy to work
on, while production/runtime installs stay minimal by default.

### Docker images install only the dependencies they need

- The root `Dockerfile` builds the CLI image by default.
- The root image accepts `FINBOT_EXTRAS` only for explicit optional surfaces such as the dashboard.
- `web/Dockerfile.backend` installs the `web` extra instead of relying on an undeclared dependency
  group.

### Security scanning is per image, not per repository-wide image

CI and scheduled security workflows build and scan the CLI and API images independently and report
findings per image. Push CI gates on library vulnerabilities that are typically remediable within the
repository, while the scheduled monitor continues to report broader OS and base-image findings.
Workflow summaries and uploaded artifacts keep actionable package-level detail without depending on a
repeatedly reopened GitHub issue thread.

## Consequences

**Positive:**

- Smaller default runtime and CLI image.
- Lower vulnerability exposure for deployments that do not need dashboard or API dependencies.
- Clearer packaging model for local installs, Docker builds, and CI.
- Security findings become actionable because they identify the affected image and package surface.
- Push CI is less likely to fail on transient upstream Debian churn that is not yet fixable in-repo.

**Negative:**

- Optional commands such as `finbot dashboard` now require the matching extra to be installed.
- CI and contributor installs are slightly more explicit because full-repo workflows must use
  `--all-extras`.
- There are now multiple runtime surfaces to keep documented and tested.
- Some OS-level container findings may be visible in the scheduled monitor before they are practical to
  remediate in push-time CI.
