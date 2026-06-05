# Public GitHub Cleanup

**Status:** Complete
**Date:** 2026-06-04
**Related guidance:** `docs/guidelines/documentation-guidelines.md`, `docs/guidelines/roadmap-process.md`

## Context

This maintenance pass reviewed Finbot's public documentation and tracked data
surfaces for material that could be misread as financial advice, expose private
operational details, or conflict with the repository's human-only authorship
policy.

## Scope

- Strengthened the root README disclaimer to include financial, investment,
  legal, medical, and professional-advice boundaries.
- Added a public documentation boundary note to the README.
- Reworded optimization and planning language to emphasize educational,
  example, and research use rather than personalized recommendations.
- Added ignored local `private/` note patterns while keeping encrypted private
  notes trackable only when an encryption workflow is intentionally used.
- Generalized exact local paths, GitHub Secrets URLs, and token-like examples in
  public guides and archived planning notes.
- Replaced non-human team author labels in research docs with the actual human
  author.
- Preserved the `CLAUDE.md` and `GEMINI.md` relative symlinks to `AGENTS.md`.

## Verification

- Ran targeted exact-pattern searches for personal paths, token-like examples,
  GitHub Secrets URLs, and secret-printing troubleshooting commands.
- Ran the requested broad sensitive-term search; remaining hits are expected
  public finance/domain terms, package integrity hashes, and code redaction key
  names.
- Checked tracked CSVs and `.env.example`; these contain public manifests,
  benchmark outputs, or blank placeholders.
- Checked tracked notebook/docs text for private financial-data indicators,
  including personal holdings and exported brokerage records.
- Verified commit authors across local refs are Jeremy Dawson or
  `dependabot[bot]`.
- Verified `git diff --check`.
- Verified `bash -n scripts/test_testpypi_workflow.sh`.

## Tooling Limits

- `gitleaks` and `trufflehog` were not installed in the available local PATHs,
  so a dedicated secret-scanner run was not completed locally.
- The available Python runtimes lacked a parquet engine, so tracked parquet
  files were reviewed by tracked path/name only. They are frozen public
  `SPY`, `TLT`, and `QQQ` ticker histories used as golden datasets.

## Follow-Up

- Run a dedicated secret scanner in CI or a local environment where `gitleaks`
  or `trufflehog` is available.
- Re-check binary parquet contents if a future maintenance environment includes
  `pyarrow`, `fastparquet`, or equivalent parquet tooling.
