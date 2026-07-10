# Nautilus Mypy Roadmap Reconciliation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Retire the stale Nautilus adapter mypy backlog item after proving that the locked contributor environment passes a fresh full-package type check.

**Architecture:** This is a documentation-only closeout. Preserve the historical 2026-06-28 failure in the archived overnight plan, remove only the now-stale unchecked roadmap entry, and add a dated completion-table row with reproducible verification evidence.

**Tech Stack:** Markdown, Git, uv, mypy 1.20.1

## Global Constraints

- Do not change Python source, dependency metadata, lockfiles, tests, CI, or runtime behavior.
- Keep the historical failure record in `docs/planning/archive/autonomous-overnight-work-plan-2026-06-28.md` unchanged.
- Use the locked all-extras contributor environment.
- Run mypy without incremental cache before claiming the follow-up is resolved.
- Do not attribute authorship or contribution to automation.

## File Structure

- Create `docs/superpowers/plans/2026-07-10-nautilus-mypy-roadmap-reconciliation.md` as the durable execution record for this batch.
- Modify `docs/planning/roadmap.md` to remove the stale deferred item and record its verified closeout.

---

### Task 1: Reconcile the Nautilus mypy roadmap state

**Files:**
- Create: `docs/superpowers/plans/2026-07-10-nautilus-mypy-roadmap-reconciliation.md`
- Modify: `docs/planning/roadmap.md`
- Test: documentation and full-package verification commands

**Interfaces:**
- Consumes: the locked `uv.lock` contributor environment and `[tool.mypy]` configuration in `pyproject.toml`
- Produces: a roadmap with no stale Nautilus mypy backlog item and a dated completion record

- [x] **Step 1: Confirm the isolated baseline is clean**

Run:

```bash
git status --short --branch
uv sync --all-extras --frozen
```

Expected: the branch is `chore/finbot-mypy-roadmap-closeout`; the only committed batch change before this plan is the `.worktrees/` ignore rule; dependency sync exits 0 without changing tracked files.

- [x] **Step 2: Verify the reported type-check failures are absent without cache**

Run:

```bash
DYNACONF_ENV=development uv run --frozen mypy --no-incremental finbot/
```

Expected:

```text
Success: no issues found in 415 source files
```

- [x] **Step 3: Update the active roadmap**

In `docs/planning/roadmap.md`:

- change `Last Updated` from `2026-07-05` to `2026-07-10`;
- remove the unchecked deferred-backlog line that asks to resolve Nautilus adapter mypy failures at lines 396, 594, and 967;
- add this row at the top of the completed-items table:

```markdown
| Nautilus adapter mypy follow-up closeout                           | 2026-07-10 | Retired the stale 2026-06-28 follow-up after a locked all-extras sync and a fresh non-incremental `uv run mypy finbot/` completed with no issues across 415 source files. The archived overnight plan retains the original three-error observation for historical context. |
```

- [x] **Step 4: Verify roadmap consistency and formatting**

Run:

```bash
rg -n "Nautilus adapter mypy follow-up closeout|Resolve the Nautilus adapter full-repo mypy failures|Last Updated" docs/planning/roadmap.md
git diff --check
uv run --frozen pre-commit run --all-files
```

Expected: the dated closeout row and `Last Updated: 2026-07-10` are present; the stale `Resolve the Nautilus adapter full-repo mypy failures` line is absent; diff check and pre-commit exit 0.

Execution note: the first all-files pre-commit run found pre-existing missing
EOF newlines in three unrelated `docs_site/research/` files and modified them.
Those hook-generated edits were restored immediately. The same hook suite then
passed when scoped to `.gitignore`, the roadmap, and this plan.

- [x] **Step 5: Re-run the full-package type gate**

Run:

```bash
DYNACONF_ENV=development uv run --frozen mypy --no-incremental finbot/
```

Expected:

```text
Success: no issues found in 415 source files
```

- [x] **Step 6: Review and commit the batch**

Run:

```bash
git diff -- .gitignore docs/planning/roadmap.md docs/superpowers/plans/2026-07-10-nautilus-mypy-roadmap-reconciliation.md
git status --short
git add docs/planning/roadmap.md docs/superpowers/plans/2026-07-10-nautilus-mypy-roadmap-reconciliation.md
git commit -m "docs: close stale Nautilus mypy follow-up"
```

Expected: only the worktree ignore setup, plan record, and roadmap reconciliation belong to this branch; the documentation commit succeeds with repository hooks passing.
