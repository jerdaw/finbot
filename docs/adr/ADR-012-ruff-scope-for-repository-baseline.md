# ADR-012: Ruff Scope for Repository Baseline

**Status:** Accepted
**Date:** 2026-02-19

## Context

Repository-wide `uv run ruff check .` was failing due to Jupyter notebook lint and parsing issues. The notebook files contain exploratory markdown/code cell patterns that are not aligned with strict Ruff Python-source rules, causing high-noise baseline failures unrelated to core package/runtime quality gates.

The project requires a reliable lint baseline for CI on the free GitHub tier.

## Decision

Exclude `notebooks/` from repository-wide Ruff baseline checks by adding `notebooks` to `[tool.ruff].exclude` in `pyproject.toml`.

Keep strict Ruff coverage for application/library/test source code and web backend code.

## Consequences

### Positive

- Restores a stable and actionable `ruff check .` baseline.
- Reduces CI noise and wasted free-tier minutes.
- Keeps lint gate focused on production and test code paths.

### Negative

- Notebook quality is no longer enforced by the repo-wide Ruff command.
- A dedicated notebook lint/validation workflow (e.g., nbQA-focused pass) remains future work.
