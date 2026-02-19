# Implementation Plan v7.2.0: Priority 5 Governance and Security Quick Wins

**Created:** 2026-02-19
**Updated:** 2026-02-19
**Status:** Complete (implemented 2026-02-19)
**Roadmap Anchors:** Priority 5 items 25, 27, 35, 40, 41
**Scope:** Close small, high-signal professionalism/security documentation and workflow gaps with low implementation risk.

## Current State Summary

- Priority 6 post-E6 phase 2 (items 69-72) is complete.
- Several Priority 5 small governance/security items remain open in `docs/planning/roadmap.md`.
- `docs.yml` workflow already exists in `.github/workflows/docs.yml`, but roadmap item 40 is still marked not started.
- `README.md` has CI/codecov/docstring badges, but no docs workflow badge.
- No root `DISCLAIMER.md` file is present.
- No `.github/CODEOWNERS` file is present.
- No automated dependency license audit is currently wired in CI.

## Unknowns and Assumptions

### Unknowns

1. Exact package license inventory output may vary by environment resolution.
2. Whether all transitive dependencies expose SPDX-compatible license fields.

### Assumptions

1. Existing docs deployment workflow is acceptable for marking item 40 complete after consistency updates.
2. Quick-win scope should avoid broad refactors and keep CI runtime impact minimal.
3. Human maintainer remains final reviewer for governance ownership entries in CODEOWNERS.

## Objectives

1. Implement roadmap item 25: add root disclaimer and surface it in README, CLI, and dashboard.
2. Implement roadmap item 27: add dependency license audit automation and baseline artifact.
3. Implement roadmap item 35: add CODEOWNERS.
4. Resolve roadmap consistency for docs workflow/badge items 40/41.
5. Update roadmap and this plan checkboxes as each implementation step completes.

## Phased Plan

## Phase 1: Financial Disclaimer Integration (Item 25)

- Deliverables:
  - Add `DISCLAIMER.md` in repository root.
  - Link disclaimer from `README.md`.
  - Add concise disclaimer mention in CLI help text (`finbot/cli/main.py`).
  - Add concise disclaimer notice in dashboard home page (`finbot/dashboard/app.py`).
- Validation:
  - CLI help renders disclaimer note.
  - Dashboard displays disclaimer banner/notice.
  - README has explicit link to `DISCLAIMER.md`.
- Status: [x] Complete

## Phase 2: Dependency License Audit (Item 27)

- Deliverables:
  - Add `pip-licenses` to dev dependency group.
  - Generate `THIRD_PARTY_LICENSES.md` baseline report.
  - Add CI-heavy job step to regenerate/check dependency license report.
- Validation:
  - Command executes: `uv run pip-licenses ...`.
  - CI workflow has explicit license audit step.
  - Report file present and non-empty.
- Status: [x] Complete

## Phase 3: CODEOWNERS and Docs Workflow Consistency (Items 35, 40, 41)

- Deliverables:
  - Add `.github/CODEOWNERS` with practical ownership defaults.
  - Add docs workflow badge to `README.md`.
  - Mark roadmap item 40 complete with existing workflow evidence.
- Validation:
  - CODEOWNERS file parsed by GitHub format conventions.
  - README badge link resolves to docs workflow.
  - Roadmap status/evidence lines are consistent with repository state.
- Status: [x] Complete

## Phase 4: Documentation Sync and Verification

- Deliverables:
  - Update `docs/planning/roadmap.md` statuses/evidence for items 25, 27, 35, 40, 41.
  - Mark this implementation plan complete with per-phase checkoffs.
- Validation:
  - Targeted lint/tests pass for touched Python files.
  - Workflow YAML and documentation references are internally consistent.
- Status: [x] Complete

## Milestones

1. M1: Phase 1 complete.
2. M2: Phase 2 complete.
3. M3: Phase 3 complete.
4. M4: Phase 4 complete and fully checked off in roadmap/plan.

## Rollout and Rollback

### Rollout

- Ship as additive governance/documentation updates with one lightweight CI-heavy enhancement.

### Rollback

- Remove CI license-audit step if it causes unacceptable noise, while retaining generated report.
- Revert disclaimer/CODEOWNERS/doc-badge docs-only changes independently if needed.

## Progress Checklist

- [x] Phase 1 complete
- [x] Phase 2 complete
- [x] Phase 3 complete
- [x] Phase 4 complete

## Manual Follow-Up (External to Local Repo)

1. Enable GitHub Pages in repository settings to fully close roadmap item 40 end-to-end.
