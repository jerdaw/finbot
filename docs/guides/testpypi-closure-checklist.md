# TestPyPI Closure Checklist

Use this checklist to fully close roadmap item 39 (TestPyPI publishing).

## Preconditions

1. Workflow exists: `.github/workflows/publish-testpypi.yml`
2. Package builds locally:
   ```bash
   uv build
   ```

## One-Time Setup (GitHub UI)

1. Create TestPyPI account and API token.
2. Add GitHub Actions secret:
   - Name: `TEST_PYPI_API_TOKEN`
   - Value: your TestPyPI token

## Publish and Verify

1. Trigger workflow:
   - GitHub Actions -> `Publish to TestPyPI` -> `Run workflow`
2. Verify package metadata exists on TestPyPI:
   ```bash
   uv run python scripts/verify_testpypi_publication.py
   ```
3. (Optional) Verify expected version:
   ```bash
   uv run python scripts/verify_testpypi_publication.py --version 1.0.0
   ```
4. Verify installability:
   ```bash
   uv run --with pip python -m pip install \
     --index-url https://test.pypi.org/simple/ \
     --extra-index-url https://pypi.org/simple/ \
     finbot
   ```

## Roadmap Closeout

After successful publish and install verification:

1. Update item 39 in `docs/planning/roadmap.md` from partial to complete.
2. Update `docs/planning/priority-5-6-completion-status.md` to reflect completion.
3. Record workflow run URL and verified version in implementation notes.
