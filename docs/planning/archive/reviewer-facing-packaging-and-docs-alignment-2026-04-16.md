# Reviewer-Facing Packaging and Docs Alignment

**Status:** ✅ Complete
**Date:** 2026-04-16
**Roadmap Item:** P10.3
**Related ADRs:** None

## Context

Finbot already had strong substance for reviewer evaluation, especially in the
health-economics and research areas, but the public path to that substance was
uneven. Key health-economics links were broken or non-public, several high-
visibility docs carried stale counts or boilerplate, and the first-impression
messaging still read as finance-only even though the project had grown into a
broader quantitative research platform.

This batch was scoped to improve legibility and trust without turning the
repository into an overt admissions-branded artifact.

## Implementation Scope

### Public Health-Economics Path Repair

- Added public docs-site pages for health-economics evidence and methodology.
- Repaired tutorial and API-doc links so the reviewer path resolves through the
  published docs tree plus stable GitHub notebook links.
- Expanded the public research hub so health economics appears as part of the
  research story rather than as an isolated tutorial/API feature.

### Public Claims and Trust Cleanup

- Replaced the frontend boilerplate README with project-specific documentation.
- Reconciled stale strategy/page/router counts across README surfaces.
- Removed fragile hard-coded public metrics where a durable qualitative phrase
  was safer.
- Added `docs/METRICS.md` as a manual source of truth for stable public counts.
- Added a scope note for `docs/applications/` so reflective portfolio material
  is not confused with canonical product documentation.

### First-Impression Reframing

- Updated the root README and docs home to present Finbot as a quantitative
  research platform spanning finance and health economics.
- Promoted Health Economics in the frontend homepage featured surfaces.
- Moved Health Economics into a dedicated clinical-research navigation group.
- Updated frontend metadata and page copy for clearer reviewer comprehension.

### Targeted Docs-Debt Reduction

- Added missing public wrapper pages for leveraged ETF simulation, DCA
  optimization, strategy backtesting, engine-selection guidance, backtesting
  stats, and specific-fund simulation references.
- Used these wrappers to reduce high-signal MkDocs warnings in the public docs
  path without broadening into a full docs-platform cleanup.

## Verification

- `uv run mkdocs build`
- `cd web/frontend && corepack pnpm typecheck`
- `cd web/frontend && corepack pnpm build`
- `rg` consistency sweep for stale reviewer-facing counts and broken health-
  economics references in touched files

## Outcome

- The public health-economics evidence path is now coherent.
- Reviewer-facing surfaces present a more accurate dual-domain narrative.
- High-visibility template/stale-content issues were removed.
- A smaller set of missing public docs pages no longer leaves the published
  docs obviously incomplete in the touched areas.

## Follow-Up

- Follow-up cleanup later the same day repaired the remaining broader MkDocs
  nav/link warnings and added a lightweight public `Project Tour` walkthrough
  page.
- Historical non-human commit authorship remains governed by P9.3 and still
  requires a deliberate rewrite or cutover plan rather than an ad hoc cleanup.
