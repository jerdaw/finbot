# Docs Maintenance and Roadmap Reconciliation

**Status:** ✅ Complete
**Date:** 2026-04-16
**Roadmap Item:** Post-P10.3 maintenance follow-up
**Related ADRs:** None

## Context

The public-packaging pass closed the highest-signal trust and correctness gaps,
but the repository still had follow-up maintenance to finish before a clean
closeout: a small set of lingering markdown-style diagnostics, a final
notebook-facing audience-specific phrase, stale references to retired planning files,
and routine repo hygiene work around agent-file ownership, branch state, and
GitHub surfaces.

This pass was scoped to complete that cleanup without changing product scope or
expanding the frontend roadmap.

## Implementation Scope

### Public Docs Finalization

- Normalized the remaining markdown-style diagnostics in `docs_site/index.md`
  and the missing fenced-code language in the fund-simulator API page.
- Removed the last notebook-facing audience-specific phrasing from the public
  health-economics demo notebook.

### Planning and Roadmap Hygiene

- Reconciled archive references that still pointed at retired planning files.
- Recorded this closeout as an archived maintenance pass and updated the
  roadmap’s current-plan metadata.
- Kept the remaining roadmap limited to unfinished P10 items with real product
  value: deeper workflow coverage, responsive fixes, and deployment config.

### Repository Hygiene

- Verified `CLAUDE.md` and `GEMINI.md` remained relative symlinks to
  `AGENTS.md`.
- Expanded CODEOWNERS coverage to include the canonical agent file plus both
  symlink surfaces.
- Confirmed there were no open pull requests, no extra local branches, and no
  lingering remote branches beyond `main` and `gh-pages`.
- Re-checked commit authorship history to confirm only the human maintainer was
  present in repository history.

## Verification

- `uv run mkdocs build`
- `uv run ruff check .`
- `uv run pytest tests/ -q`
- `gh pr list`
- `git branch -vv`
- `git branch -r`
- `git log --format='%an <%ae>' | sort | uniq -c`

## Outcome

- Public docs, notebook content, roadmap metadata, and archive references are
  internally consistent.
- Human-only authorship policy remains explicit in the agent guidance and
  validated in git history.
- No GitHub PR or branch cleanup was required because the repository was
  already clear of open PRs and non-primary branches.

## Follow-Up

- Continue P10 work on broader Playwright workflow coverage when GitHub Actions
  minutes allow.
- Address responsive/mobile issues and production deployment configuration as
  the remaining frontend scope.
