# GitHub Pages Docs Deploy Runbook

This runbook verifies and maintains the Finbot MkDocs deployment path.

## Scope

- Workflow: `.github/workflows/docs.yml`
- Source content: `docs_site/` + `mkdocs.yml`
- Expected URL: `https://jerdaw.github.io/finbot/`

## Quick Verification Checklist

1. Run local build:
   ```bash
   uv run mkdocs build
   ```
2. Confirm workflow file exists and targets `main`:
   - `.github/workflows/docs.yml`
3. Verify live site responds:
   ```bash
   curl -I -L https://jerdaw.github.io/finbot/
   ```
   Expected: `HTTP/2 200` (or equivalent `200 OK` response).
4. Trigger workflow manually:
   - GitHub Actions -> `Deploy Documentation` -> `Run workflow`.
5. Confirm deployment completed successfully in Actions logs.

## Manual Setup (GitHub UI) - If Not Already Enabled

These steps require repository admin permissions.

1. Open repository settings:
   - `https://github.com/jerdaw/finbot/settings/pages`
2. In **Build and deployment**:
   - Source: `Deploy from a branch` (or keep GitHub Actions-managed Pages setup if already active).
   - Branch: `gh-pages` (if using `mkdocs gh-deploy` workflow path).
3. Save settings.
4. Re-run the `Deploy Documentation` workflow.
5. Re-check `https://jerdaw.github.io/finbot/`.

## Rollback

If a docs deploy introduces a bad version:

1. Re-run a known-good commit with `workflow_dispatch`.
2. If needed, temporarily disable the docs workflow trigger in `.github/workflows/docs.yml` while fixing source docs.
3. Restore trigger after validation.

## Known Operational Notes

1. Local `mkdocs build` currently succeeds but emits pre-existing navigation/link warnings.
2. Warnings do not currently block deployment; they should be tracked as documentation quality debt.
