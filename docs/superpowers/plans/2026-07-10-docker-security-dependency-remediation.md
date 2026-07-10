# Docker Security Dependency Remediation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restore Finbot's CLI and API Docker security gates by replacing the two vulnerable transitive Python packages in the locked dependency graph.

**Architecture:** Keep direct dependency policy unchanged and refresh only the `cryptography` and `soupsieve` lock entries to the first releases identified as fixed by the current Trivy reports. Validate application compatibility locally, then use the repository's existing Docker CI jobs as the real image-boundary proof because Docker is unavailable in this WSL environment.

**Tech Stack:** Python 3.11-3.14, uv, pytest, mypy, pip-audit, Docker, Trivy

## Global Constraints

- Do not suppress, ignore, downgrade, or weaken the existing Trivy gate.
- Do not add direct dependency pins when the existing transitive constraints admit the fixed releases.
- Update only `cryptography` from 46.0.7 to 48.0.1 and `soupsieve` from 2.8.3 to 2.8.4 unless the resolver proves an additional change is required.
- Preserve Google Auth, BeautifulSoup, CLI, API, and supported Python behavior.
- Do not modify Dockerfiles, application source, tests, CI, or direct dependency metadata unless the lock-only hypothesis fails with evidence.
- Keep the documentation-only PR #111 separate from this remediation branch.
- Do not attribute authorship or contribution to automation.

## File Structure

- Create `docs/superpowers/plans/2026-07-10-docker-security-dependency-remediation.md` as the remediation and verification record.
- Modify `uv.lock` only for the targeted fixed transitive releases.
- Modify `docs/planning/roadmap.md` only after both Docker image scans pass, retiring the recurring Docker Security Scan failure item and adding dated completion evidence.

---

### Task 1: Reproduce and scope the two image findings

**Files:**
- Create: `docs/superpowers/plans/2026-07-10-docker-security-dependency-remediation.md`
- Test: GitHub Actions run 29070056991 artifacts and locked dependency graph

**Interfaces:**
- Consumes: `docker-security-report-cli`, `docker-security-report-api`, `uv.lock`, and `uv tree --invert`
- Produces: a patch contract naming the vulnerable versions, fixed versions, dependency paths, and compatibility boundary

- [x] **Step 1: Record the failing image-boundary evidence**

Inspect the CLI and API Trivy reports from GitHub Actions run `29070056991`.

Expected in both images:

```text
GHSA-537c-gmf6-5ccf  cryptography  46.0.7  fixed 48.0.1  HIGH
CVE-2026-49476       soupsieve     2.8.3   fixed 2.8.4   HIGH
CVE-2026-49477       soupsieve     2.8.3   fixed 2.8.4   HIGH
```

- [x] **Step 2: Confirm the current dependency paths**

Run:

```bash
uv tree --frozen --all-groups --invert --package cryptography
uv tree --frozen --all-groups --invert --package soupsieve
```

Expected: `cryptography` is transitive through `google-auth`; `soupsieve` is transitive through `beautifulsoup4`; both are present in the CLI and API all-extras image environment.

### Task 2: Refresh only the vulnerable lock entries

**Files:**
- Modify: `uv.lock`
- Test: resolver diff and locked environment sync

**Interfaces:**
- Consumes: existing direct dependency ranges in `pyproject.toml`
- Produces: locked `cryptography==48.0.1` and `soupsieve==2.8.4` artifacts for all supported platforms

- [x] **Step 1: Run the targeted resolver update**

Run:

```bash
uv lock --upgrade-package cryptography==48.0.1 --upgrade-package soupsieve==2.8.4
```

Expected: the resolver updates only the two named package entries and their distribution hashes.

- [x] **Step 2: Inspect the complete lockfile diff**

Run:

```bash
git diff -- uv.lock
git diff --check
```

Expected: `cryptography 46.0.7 -> 48.0.1` and `soupsieve 2.8.3 -> 2.8.4`; no unrelated package, source, or metadata changes.

- [x] **Step 3: Sync and verify installed versions**

Run:

```bash
uv sync --all-extras --frozen
uv run --frozen python -c "import cryptography, soupsieve; print(cryptography.__version__, soupsieve.__version__)"
```

Expected:

```text
48.0.1 2.8.4
```

### Task 3: Verify preserved behavior locally

**Files:**
- Test: existing full repository gates

**Interfaces:**
- Consumes: the refreshed locked contributor environment
- Produces: compatibility evidence across supported application behavior

- [x] **Step 1: Run dependency and static gates**

Run:

```bash
uv run --frozen --all-extras --with pip-audit pip-audit --local
DYNACONF_ENV=development uv run --frozen mypy --no-incremental finbot/
uv run --frozen ruff check .
uv run --frozen ruff format --check .
```

Expected: all commands exit 0; mypy reports no issues across 415 source files.

Execution note: `pip-audit` is intentionally not part of the locked
contributor environment. The initial direct `uv run pip-audit` invocation
therefore could not spawn it. The plan now uses the repository CI invocation
shape with `--with pip-audit`.

- [x] **Step 2: Run the full test suite**

Run:

```bash
DYNACONF_ENV=development uv run --frozen pytest tests/ -v
```

Expected: all selected tests pass; environment-dependent tests may retain their documented skips.

- [x] **Step 3: Run scoped repository hooks and review**

Run:

```bash
uv run --frozen pre-commit run --files uv.lock docs/superpowers/plans/2026-07-10-docker-security-dependency-remediation.md
git diff --check
git status --short
```

Expected: hooks and diff check exit 0; only the plan and `uv.lock` are changed.

### Task 4: Prove image-level closure in GitHub CI

**Files:**
- Modify after proof: `docs/planning/roadmap.md`
- Modify after proof: `docs/superpowers/plans/2026-07-10-docker-security-dependency-remediation.md`

**Interfaces:**
- Consumes: repository Dockerfiles, locked dependencies, and existing Docker Security Scan matrix
- Produces: passing CLI and API Trivy image scans with the fixed packages

- [ ] **Step 1: Commit, push, and open the security PR**

Commit the plan and lock refresh with:

```bash
git add uv.lock docs/superpowers/plans/2026-07-10-docker-security-dependency-remediation.md
git commit -m "fix(deps): remediate Docker image vulnerabilities"
git push -u origin fix/finbot-docker-security-dependencies
```

Open a PR against `main` with the exact vulnerable/fixed versions and local verification results.

- [ ] **Step 2: Verify the existing Docker image gates**

Wait for the PR's GitHub Actions run.

Expected: both `Docker Security Scan (cli)` and `Docker Security Scan (api)` pass without ignore-file changes; all other required checks pass.

- [ ] **Step 3: Close the roadmap item after proof**

In `docs/planning/roadmap.md`:

- update `Last Updated` to `2026-07-10`;
- remove the deferred item beginning `Investigate current CI Docker Security Scan image failures`;
- add a completed-items row naming the two package upgrades and the passing CLI/API image scans.

Mark this plan complete, run scoped hooks and `git diff --check`, commit with
`docs: record Docker security remediation`, push, and verify the resulting CI
run before merge.
