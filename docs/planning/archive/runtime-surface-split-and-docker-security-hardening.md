# Runtime Surface Split and Docker Security Hardening

**Status:** ✅ Complete
**Date:** 2026-03-23
**Roadmap Item:** P9.4
**Related ADR:** `docs/adr/ADR-014-runtime-surfaces-and-image-specific-dependencies.md`

## Context

The scheduled Docker security issue kept reopening because the default image carried optional
dependencies that were not required for every runtime path. The implementation goal was to minimize
the default runtime image, separate optional application surfaces, and make the Docker security
automation report actionable per image.

## Implementation Scope

### Packaging

- Keep only the core CLI/runtime dependency set in `project.dependencies`.
- Move optional surfaces to extras:
  - `dashboard`
  - `web`
  - `nautilus`
  - `notebooks`
- Regenerate `uv.lock` so the extras are locked and reproducible.

### Containers

- Make the root `Dockerfile` build a CLI-focused image by default.
- Add `FINBOT_EXTRAS` for explicit optional surfaces such as the dashboard.
- Update `web/Dockerfile.backend` to install the `web` extra in a hardened multi-stage build.
- Build dashboard support from the root Dockerfile with `FINBOT_EXTRAS=dashboard`.

### Security Automation

- Scan the CLI and API images separately in CI and scheduled workflows.
- Keep the failure threshold at `HIGH,CRITICAL`.
- Include image name, package, installed version, fixed version, severity, and CVE in the managed
  issue body and follow-up comments.
- Update the local scan script to build and scan both Python images.

### Documentation and Developer Ergonomics

- Document the new install surfaces in `README.md`, `web/README.md`, `AGENTS.md`, and docs-site.
- Add a clean dashboard install hint when Streamlit is not installed.
- Add a `make docker-dashboard` target for the new dashboard compose service.

## Verification

- `uv lock`
- `uv sync --all-extras`
- `uv run --all-extras --with pip-audit pip-audit --local`
- `DYNACONF_ENV=development uv run --extra web python -c "from web.backend.main import app; print(app.title)"`
- `uv run pytest tests/ -q`

## Outcome

- Base installs are smaller and no longer pull in dashboard, API, Nautilus, or notebook tooling by
  default.
- The root image is CLI-first, while dashboard and API images opt into the dependencies they need.
- Docker security findings are now tracked per image, reducing scan noise and making remediation
  faster.
