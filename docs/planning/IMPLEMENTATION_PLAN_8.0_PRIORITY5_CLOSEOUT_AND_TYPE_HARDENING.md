# Implementation Plan v8.0.0: Priority 5 Closeout, Type-Safety Tightening, and Planning Hygiene

**Created:** 2026-02-20
**Updated:** 2026-02-20
**Status:** In Progress (Phases 1-4 complete with Wave 5 strictness extension, Phase 5 in progress)
**Roadmap Anchors:** Priority 5 items 12, 13/40, 42; roadmap/process consistency gaps identified in Priority 5.5-5.7 status rows
**Scope Window:** 5-6 weeks (single-maintainer pace, CI free-tier aware)

## Brief Current-State Summary

Repository review across code, CI workflows, and planning docs indicates the following current state:

1. Core platform architecture is stable and mature:
   - Adapter-first Backtrader path is complete and active.
   - Execution simulator, typed contracts, parity harness, and E6 decision gate are complete.
   - CI is split into lean `ci.yml` and heavier `ci-heavy.yml`, consistent with free-tier constraints.
2. Multiple Priority 5 items are implemented in code/workflows but not consistently reflected in roadmap status rows:
   - Implemented artifacts exist for accessibility, property tests (Hypothesis), performance regression testing, commit linting, release automation, TestPyPI publishing, and Scorecard.
3. Priority 5 true remaining work is narrow and clear:
   - Item 12 (`disallow_untyped_defs` journey) is only partially progressed.
   - Item 13/40 (GitHub Pages docs deployment) has now been verified as operational; ongoing work is maintenance/runbook discipline.
   - Item 42 (logo/branding) is open and human-design dependent.
4. Documentation/process drift is now a measurable maintenance risk:
   - Some status docs conflict with current repo evidence.
   - Planning artifacts need one authoritative synchronization pass before the next implementation sprint.

## Key Unknowns

1. Whether current repo admin permissions are available to enable GitHub Pages immediately.
2. Whether the target docs URL should remain `https://jerdaw.github.io/finbot/` without org/repo migration changes.
3. Whether item 42 (logo/branding) has human-approved design direction available this cycle.
4. The exact weekly hour budget available for sustained mypy annotation work.

## Assumptions

1. Backtrader remains the primary execution path; ADR-011 decision remains `Defer` for Nautilus adoption.
2. CI runtime budget remains constrained; heavy checks should stay scheduled/manual where possible.
3. Work will be executed by one maintainer with incremental, low-risk merges.
4. Type-hardening will follow the existing phased approach (module-level enforcement first, not global strict flip).

## Objectives for This Batch

1. Reconcile roadmap/planning status so tracked state matches repository reality.
2. Close the docs deployment workflow lifecycle (item 13/40) end-to-end, including external settings.
3. Advance stricter mypy adoption beyond audit mode with enforceable module-level strictness in high-value packages.
4. Resolve or formally defer remaining Priority 5 tail items with explicit rationale and decision records.

## Non-Goals

1. Full global strict mypy across all `finbot/utils/*` modules in this batch.
2. Nautilus production migration or live-trading rollout.
3. Large UI redesign outside item 42 branding scope.

## Phased Implementation Plan

## Phase 1: Planning/Status Reconciliation Baseline

**Goal:** Establish a single trustworthy planning baseline before new implementation work.
**Status:** Complete (2026-02-20)

**Deliverables:**
1. Update `docs/planning/roadmap.md` status rows for implemented Priority 5 items that are currently stale.
2. Update `docs/planning/priority-5-6-completion-status.md` to align with current repository evidence and dates.
3. Add/refresh explicit "remaining-open" list (only unresolved items) in roadmap summary section.
4. Record evidence links for each status update (file/workflow/test references).

**Primary Dependencies:**
1. Existing artifacts in repo (workflows, tests, docs, completion summaries).

**Risks:**
1. Missing evidence links for older completions.
2. Overwriting useful historical nuance during trim.

**Mitigations:**
1. Keep detailed rationale in archive/completion docs; trim only roadmap narrative.
2. Require evidence-path references for each updated status.

**Validation:**
1. Manual checklist: each updated status row has at least one evidence artifact.
2. `uv run ruff check docs/` (if docs lint profile is configured) or manual markdown review pass.
3. Peer sanity pass against `.github/workflows/` and `tests/` directories.

---

## Phase 2: Docs Deployment Closure (Item 13/40 End-to-End)

**Goal:** Move docs deploy from "workflow present" to fully operational production path.
**Status:** Complete (2026-02-20)

**Deliverables:**
1. Enable GitHub Pages in repository settings (external action).
2. Confirm `.github/workflows/docs.yml` deploy succeeds from `main` and from `workflow_dispatch`.
3. Verify published docs availability at configured `site_url`.
4. Add a short operational runbook for docs deployment verification and incident recovery.
5. Mark roadmap item 13/40 as complete with exact completion date and evidence links.

**Primary Dependencies:**
1. Maintainer admin access to repo settings.
2. Existing MkDocs build stability.

**Risks:**
1. GitHub Pages source misconfiguration (branch/folder mismatch).
2. Deploy token/permissions edge cases on first run.

**Mitigations:**
1. Use manual dispatch as first controlled rollout.
2. Capture first successful deployment run URL in roadmap evidence.

**Validation:**
1. `uv run mkdocs build` passes locally.
2. At least one successful Actions run in `docs.yml` after Pages enablement.
3. Public docs URL serves updated content.

---

## Phase 3: Type-Safety Tightening Wave 1 (Priority 5 Item 12)

**Goal:** Enforce stricter typed function signatures in highest-value, lowest-churn modules.
**Status:** Complete (2026-02-20)

**Target Modules (Wave 1):**
1. `finbot.core.*`
2. `finbot.services.execution.*`
3. `finbot.core.contracts.*` (if not already clean under stricter flags)

**Deliverables:**
1. Add module-level mypy overrides with:
   - `disallow_untyped_defs = true`
   - `disallow_incomplete_defs = true`
2. Annotate/fix surfaced function signatures and related type issues in Wave 1 modules.
3. Add/update typing guidance notes in contribution docs for new code in strict modules.

**Primary Dependencies:**
1. Stable baseline mypy execution (`uv run mypy finbot/`) passing before changes.
2. Existing mypy audit artifacts in `docs/planning/mypy-phase1-audit-report.md`.

**Risks:**
1. Third-party typing friction (Backtrader/pandas/quantstats boundaries).
2. Annotation churn producing noisy PRs.

**Mitigations:**
1. Keep Wave 1 limited to modules already identified as low-error/high-readiness.
2. Use narrow, explicit ignores only when third-party typing is the root cause.

**Validation:**
1. `uv run mypy finbot/` passes.
2. Targeted regression tests:
   - `uv run pytest tests/unit/test_core_contracts.py -v`
   - `uv run pytest tests/unit/test_order_lifecycle.py tests/unit/test_latency_simulation.py tests/unit/test_risk_controls.py tests/unit/test_checkpoint_recovery.py -v`
3. CI `type-check` job remains green.

---

## Phase 4: Type-Safety Tightening Wave 2 + Guardrails

**Goal:** Extend strictness to additional critical runtime paths without flipping global strict mode.
**Status:** Complete (2026-02-20)

**Target Modules (Wave 2):**
1. `finbot.services.backtesting.*` (non-strategy modules first)
2. `finbot.libs.api_manager.*`
3. `finbot.libs.logger.*`

**Progress Snapshot (2026-02-20):**
1. `finbot.services.backtesting.*` strict overrides are enabled and passing.
2. `finbot.libs.api_manager.*` strict overrides are enabled and passing.
3. `finbot.libs.logger.*` strict overrides are enabled and passing.
4. Wave 3 extension strict overrides are enabled and passing for:
   - `finbot.services.data_quality.*`
   - `finbot.services.health_economics.*`
   - `finbot.services.optimization.*`
5. Wave 4 extension strict overrides are enabled and passing for:
   - `finbot.utils.request_utils.*`
6. Wave 5 extension strict overrides are enabled and passing for:
   - `finbot.utils.pandas_utils.*`
7. Strict-module tracker and policy references are published in:
   - `docs/guides/mypy-strict-module-tracker.md`
   - `CONTRIBUTING.md`

**Deliverables:**
1. Add second set of module-level mypy strict overrides.
2. Resolve surfaced typing errors in selected modules.
3. Introduce a maintained strict-coverage tracker document (module status + error counts).
4. Define "strict by default" policy for net-new modules in these namespaces.

**Primary Dependencies:**
1. Successful completion of Wave 1.
2. Stable mypy behavior under current dependency versions.

**Risks:**
1. Scope expansion into high-error files can exceed time budget.
2. CI instability if strictness is enabled too broadly in one change.

**Mitigations:**
1. Gate expansion file-by-file or package-by-package.
2. If needed, stage Wave 2 into sub-phases (4A backtesting, 4B libs).

**Validation:**
1. `uv run mypy finbot/` passes with new overrides.
2. Core suite smoke:
   - `uv run pytest tests/unit/test_backtrader_adapter.py tests/integration/test_backtest_parity_ab.py -v`
3. No reduction in coverage gate compliance.

---

## Phase 5: Priority 5 Tail Closure and Decision Gate

**Goal:** Leave Priority 5 with only deliberate, documented open items.
**Status:** In Progress (2026-02-20)

**Progress Snapshot (2026-02-20):**
1. Item 42 is explicitly deferred with rationale and re-entry criteria in roadmap/status docs.
2. Item 39 remains partially complete pending external maintainer token/publish verification.
3. External closure support is now prepared:
   - `docs/guides/testpypi-closure-checklist.md`
   - `scripts/verify_testpypi_publication.py`
4. Verification script execution confirms external dependency remains:
   - `uv run python scripts/verify_testpypi_publication.py` currently returns `Package 'finbot' not found on TestPyPI.`
5. Maintenance pass completed:
   - strict typing expanded into `finbot.utils.request_utils.*` and `finbot.utils.pandas_utils.*`
   - targeted regression tests added for batched dataframe saves
   - global mypy surfaced yfinance typing regressions were fixed and validated
6. Final v8.0 completion summary and archival are pending closure of external follow-up.

**Deliverables:**
1. Item 42 decision:
   - Option A: Implement approved SVG logo + integrate into README/docs site.
   - Option B: Defer with explicit reason, owner, and re-entry condition/date.
2. Publish completion summary for v8.0 execution.
3. Archive completed plan to `docs/planning/archive/` after implementation closure.

**Primary Dependencies:**
1. Human design approval (if Option A).
2. Completion of earlier phases.

**Risks:**
1. Logo scope creep into broader brand redesign.

**Mitigations:**
1. Keep logo deliverable minimal (single SVG + two integrations).
2. Timebox design iteration; defer if no approval by gate date.

**Validation:**
1. If implemented: logo renders in README and MkDocs pages.
2. If deferred: roadmap has explicit defer rationale and next review date.

## Timeline and Milestones

## Timeline (Target)

1. **Week 1 (2026-02-23 to 2026-02-27):** Phase 1 complete.
2. **Week 2 (2026-03-02 to 2026-03-06):** Phase 2 complete (pending external settings enablement).
3. **Weeks 3-4 (2026-03-09 to 2026-03-20):** Phase 3 complete.
4. **Weeks 5-6 (2026-03-23 to 2026-04-03):** Phase 4 complete and Phase 5 decision gate executed.

## Milestones

1. **M1 (2026-02-27):** Roadmap/status docs reconciled to repository reality.
2. **M2 (2026-03-06):** Docs deployment confirmed operational end-to-end.
3. **M3 (2026-03-20):** Wave 1 strict mypy enforcement merged and stable.
4. **M4 (2026-04-03):** Wave 2 strictness + Priority 5 tail decision completed.

## Rollout and Rollback Strategy

## Rollout Approach

1. Land Phase 1 as docs-only changes first.
2. Land Phase 2 with external settings action + workflow verification evidence.
3. Land Phase 3 and 4 in small, reviewable PRs by module/package.
4. Gate each phase on passing mypy + targeted tests before proceeding.

## Rollback Approach

1. **Docs/process rollback:** Revert specific docs commits; no runtime impact.
2. **Type strictness rollback:** Remove or narrow newly-added mypy overrides per module while keeping annotations already added.
3. **CI impact rollback:** If CI time/cost spikes, keep strict checks on critical modules only and defer expanded scope to next batch.

## Progress Tracking and Validation Cadence

1. Weekly status update in roadmap with exact date stamps.
2. Per-phase completion checklist updated in this plan.
3. End-of-phase validation command set captured in summary notes.

## Phase Completion Checklist

- [x] Phase 1 complete
- [x] Phase 2 complete
- [x] Phase 3 complete
- [x] Phase 4 complete
- [ ] Phase 5 complete

## Exit Criteria for v8.0.0

1. Roadmap and status documents are internally consistent with repository artifacts.
2. Docs deployment is fully operational (not partially complete).
3. Priority 5 item 12 is materially advanced with enforceable strictness in at least Wave 1 modules.
4. Priority 5 item 42 is either implemented or explicitly deferred with re-entry criteria.
5. v8.0 completion summary is published and plan archived after execution.
