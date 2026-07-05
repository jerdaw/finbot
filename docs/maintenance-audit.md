# Maintenance Audit

## Documentation And Code Professionalization Pass - 2026-07-05

### Metadata

- Audit date: 2026-07-05
- Target repository root: `/home/jer/repos/finbot`
- Branch/status at inventory time: `main...origin/main` with local professionalization edits
- Prompt-pack root used for this pass: `/mnt/c/Users/jer/Downloads/codex-repo-health-goal-prompts-entrypoint-v6-professionalization/codex-repo-health-goals-entrypoint-v6-professionalization`
- Prompt-pack files read: `RUN_THIS_FIRST.md`, `codex-goals/00-shared-repo-native-autonomous-safety-contract.md`, `codex-goals/00A-deep-evidence-and-coverage-gates.md`, `codex-goals/07A-documentation-code-professionalization.md`
- Earlier path note: `PROMPT_PACK_ROOT` was not set in the shell. The v5 prompt-pack path recorded by the older audit section was no longer present, so the matching v6 professionalization prompt pack under `Downloads/` was resolved and used read-only.
- Report location: this existing `docs/maintenance-audit.md` file, following the shared contract's least-intrusive reporting rule.

### Audience And Maturity Assessment

Finbot presents as a public, reviewable quantitative research platform with finance, simulation, backtesting, analytics, health-economics, Streamlit, FastAPI, and Next.js surfaces. The README, docs site, package metadata, disclaimers, and planning docs describe an educational/research project with a stable baseline, not a guaranteed production trading or clinical decision system. Professional wording for this repo should therefore be factual, durable, modest about maturity, and explicit about limitations.

### Inventory And Coverage Tier

Inventory commands run for this pass:

- `pwd`
- `git rev-parse --show-toplevel`
- `git status --short --branch`
- `git ls-files | wc -l`
- `git ls-files | awk ...`
- `git ls-files | rg '\.(py|ts|tsx|js|mjs|md|rst|yml|yaml|toml|json|css|sh)$' | xargs wc -l | tail -n 1`
- `git diff --name-only`

Inventory results:

- Tracked files: `1013`
- Reviewable text lines across common source/docs/config extensions: about `163883`
- Category counts from tracked files: `finbot/` 430, `web/backend/` 32, `web/frontend/` 124, `tests/` 126, `docs/` plus `docs_site/` 232, `scripts/` 11, `.github/` 14
- Coverage tier: large repository. This pass used risk-based coverage with broad static searches plus manual review of public, central, and representative code-adjacent surfaces.
- Exclusions: dependency/build/cache trees such as `.git/`, `.venv/`, `node_modules/`, `.next/`, `.ruff_cache/`, `.mypy_cache/`, `.pytest_cache/`, and generated build output. Lockfiles were treated as generated/dependency artifacts and not edited.

### Surfaces Inspected

Manual review covered these representative surfaces:

- Repo instructions and metadata: `AGENTS.md`, `README.md`, `pyproject.toml`, `mkdocs.yml`
- Existing audit/report location: `docs/maintenance-audit.md`
- Contributor/security/governance surfaces already present: `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `.github/ISSUE_TEMPLATE/bug_report.md`, `.github/ISSUE_TEMPLATE/feature_request.md`, `.github/PULL_REQUEST_TEMPLATE.md`
- Public docs and docs-site pages: `docs_site/index.md`, `docs_site/user-guide/getting-started.md`, `docs_site/user-guide/data-quality-guide.md`, `docs_site/api/services/backtesting/strategies.md`, `docs/guides/data-quality-guide.md`, `docs/guides/choosing-backtest-engine.md`, `docs/guides/updating-performance-baseline.md`, `docs/adr/ADR-010-cost-models-corporate-actions.md`, `docs/blog/why-i-built-finbot.md`
- Web docs and metadata: `web/README.md`, `web/frontend/README.md`, `web/frontend/package.json`
- CLI/help and script text: `finbot/cli/main.py`, `finbot/cli/commands/backtest.py`, `scripts/test_nautilus_backtest.py`
- Comments/docstrings in code-adjacent utility/config modules: `finbot/config/settings.yaml`, `finbot/constants/host_constants.py`, `finbot/libs/api_manager/_utils/api.py`, `finbot/libs/api_manager/_utils/api_resource_group.py`, `finbot/utils/data_collection_utils/bls/_bls_utils.py`, `finbot/utils/data_collection_utils/fred/correlate_fred_to_price.py`, `finbot/utils/data_collection_utils/scrapers/msci/_utils.py`, `finbot/utils/data_science_utils/data_cleaning/data_integrity_handlers/type_and_format_consistency.py`, `finbot/utils/data_science_utils/data_transformation/scalers_normalizers/logarithmic_scaler.py`, `finbot/utils/datetime_utils/get_missing_us_business_dates.py`, `finbot/utils/finance_utils/get_investment_event_horizon.py`, `finbot/utils/finance_utils/get_theta_decay.py`, `finbot/utils/function_utils/log_with_header_footer.py`
- Tests were covered by tracked-file wording probes; no test names/comments required safe edits in this pass.

### Searches And Probes Run

Professionalization probes were run against tracked files to avoid local caches:

- `git grep -n -I -i -E "vibe|quick.?and.?dirty|kludge|lol|wtf|stupid|dumb|ugly|gross|yolo|whatever|good enough|don't judge|sorry|short on time|fix later|ask the user|the user|medical school|med school|sleep|weekend" -- . ':!uv.lock' ':!THIRD_PARTY_LICENSES.md'`
- `git grep -n -I -i -E "ChatGPT|Codex|Claude|AI generated|generated by AI|assistant|prompt|LLM|agent" -- . ':!uv.lock' ':!THIRD_PARTY_LICENSES.md'`
- `git grep -n -I -E "\b(TODO|FIXME|HACK|XXX|BUG)\b" -- . ':!uv.lock' ':!THIRD_PARTY_LICENSES.md'`
- `git grep -n -I -i -E "Jeremy|author|personal|private|my | I " -- README.md docs docs_site tests finbot scripts web .github ':!uv.lock' ':!THIRD_PARTY_LICENSES.md'`
- `git grep -n -I -i -E "magic|probably fine|not great|bad|messy|painful|frustrating|crown jewel|boring|killer|harder than I do|impressed|WIP|work in progress|not yet been verified|better way|make this more readable" -- README.md docs docs_site finbot scripts tests web .github ':!uv.lock' ':!THIRD_PARTY_LICENSES.md'`
- `git grep -n -I -i -E "publication-ready|research-grade|comprehensive platform|battle-tested|production-ready|enterprise|robust|disaster resilience|crown jewel|state-of-the-art|best-in-class" -- README.md docs docs_site finbot scripts web .github ':!uv.lock' ':!THIRD_PARTY_LICENSES.md'`
- `rg -nP "[\x{1F300}-\x{1FAFF}]" README.md docs_site/index.md docs/guides/choosing-backtest-engine.md web/README.md scripts/test_nautilus_backtest.py finbot/config/settings.yaml finbot/cli/main.py`
- `git diff --check`
- `git diff --stat`

Prompt-pack resolution probes:

- `printf '%s\n' "${PROMPT_PACK_ROOT:-}"`
- targeted `find` searches under `/mnt/c/Users/jer/.codex`, `/home/jer`, `/home/jer/repos/finbot`, and `/mnt/c/Users/jer/Downloads` for `00-shared-repo-native-autonomous-safety-contract.md` and `00A-deep-evidence-and-coverage-gates.md`

### Candidate Wording Ledger

| Candidate | Status | Decision |
| --- | --- | --- |
| Personal/static-config complaint in `finbot/config/settings.yaml` | Fixed | Rewritten as a neutral explanation of static settings vs runtime-derived logger settings. |
| README and docs-site claims such as production-ready, production-grade, publication-ready, and research-grade | Fixed where in current public Finbot surfaces | Replaced with operational, research-workflow, reproducible-output, or methodology wording. |
| `docs/guides/choosing-backtest-engine.md` overstating Backtrader/Nautilus maturity in Finbot guidance | Fixed | Reworded to widely used/live-trading-oriented/live-execution features while preserving the engine recommendation. |
| Casual invalid examples in `docs/guides/updating-performance-baseline.md` | Fixed | Replaced personal phrasing with neutral invalid-rationale examples. |
| `docs/adr/ADR-010-cost-models-corporate-actions.md` "good enough" wording | Fixed | Rewritten to state the scope where simple cost models are suitable. |
| Template TODOs in `docs/guides/data-quality-guide.md` and `docs_site/user-guide/data-quality-guide.md` | Fixed | Converted generic TODO comments and error text into provider-specific implementation notes. |
| Vague or stale TODO/HACK comments in selected source utility modules | Fixed | Converted to durable notes or removed when the comment no longer added information. |
| `scripts/test_nautilus_backtest.py` chatty output and decorative status glyphs | Fixed | Rewritten as neutral smoke-test output and missing-capability guidance. |
| Public blog phrase "crown jewel" | Fixed | Softened to "core component" while preserving the intentionally first-person blog voice. |
| `web/README.md` "Professional web application" | Fixed | Rewritten as a neutral web-application description. |
| First-person blog posts under `docs/blog/` | Intentionally unchanged except one phrase | The blog format is personal narrative by design and is legitimate provenance, not code/session residue. |
| Human author names, maintainer email, citation metadata, and CODEOWNERS handles | Intentionally unchanged | These are deliberate project metadata and support/security contact surfaces. |
| AI/agent terms in `AGENTS.md`, docs guidelines, authorship policy, and prior audit report | Intentionally unchanged | These are deliberate repo policy or audit-history references, not stray assistant attribution. |
| `WIP` and bad-message examples in commit guidance | Intentionally unchanged | They are examples of invalid commit messages. |
| Archived planning docs with agent/session history or older production-ready wording | Deferred | They are historical archive artifacts; broad rewriting would risk erasing useful project history and create high churn. |
| CLI disclaimer warning glyphs | Intentionally unchanged | They are part of a warning notice, not casual decoration, and changing them would affect visible CLI output beyond this wording pass's main targets. |
| Lockfile matches and dependency-package names | Not an issue | Generated/dependency metadata; no source wording change appropriate. |

### Changes Made

This pass made small wording-only edits in current source, docs, script, and README surfaces:

- Softened public maturity and marketing-adjacent claims in `README.md`, `docs_site/index.md`, `docs_site/user-guide/getting-started.md`, `docs_site/api/services/backtesting/strategies.md`, `docs/guides/choosing-backtest-engine.md`, `docs/blog/why-i-built-finbot.md`, and `web/README.md`.
- Rewrote code-adjacent comments/docstrings in `finbot/config/settings.yaml`, `finbot/constants/host_constants.py`, `finbot/libs/api_manager/_utils/api.py`, `finbot/libs/api_manager/_utils/api_resource_group.py`, `finbot/utils/data_collection_utils/bls/_bls_utils.py`, `finbot/utils/data_collection_utils/fred/correlate_fred_to_price.py`, `finbot/utils/data_collection_utils/scrapers/msci/_utils.py`, `finbot/utils/data_science_utils/data_cleaning/data_integrity_handlers/type_and_format_consistency.py`, `finbot/utils/data_science_utils/data_transformation/scalers_normalizers/logarithmic_scaler.py`, `finbot/utils/datetime_utils/get_missing_us_business_dates.py`, `finbot/utils/finance_utils/get_investment_event_horizon.py`, `finbot/utils/finance_utils/get_theta_decay.py`, and `finbot/utils/function_utils/log_with_header_footer.py`.
- Rewrote `scripts/test_nautilus_backtest.py` status text to describe the script as a smoke test and report missing adapter capabilities without assistant/session-like wording.
- Clarified data-provider template wording in both repository and docs-site data-quality guides.
- Removed generated local verification artifacts after the maintenance pass, including tool caches, docs build output, Python bytecode caches, and the local Interrogate badge. Existing ignore rules already covered these artifacts, so `.gitignore` did not need changes.

Example rewrite patterns applied:

- Personal rationale became neutral project rationale: settings comments now describe runtime-derived settings rather than preserving personal commentary.
- Promotional maturity claims became evidence-bounded claims: production-ready/publication-ready wording became operational, research-workflow, or reproducible-output wording.
- Generic TODOs became specific notes: placeholder provider comments now name provider-specific fetching logic, and implementation-reserved fields now say what future integration they are reserved for.
- Chatty script output became neutral status output: the Nautilus helper now reports smoke-test status and missing capabilities.

### Change-Gate Decisions

Implemented edits passed the repo-native change gate because they are local, reviewable, behaviour-preserving wording changes; they follow existing Markdown, Python, YAML, and script style; they do not add tools, processes, governance, licenses, APIs, dependencies, or architecture; and they keep real limitations and disclaimers visible.

Deferred items were not changed when the concern was historical, generated/vendor, a deliberate policy disclosure, a legitimate contact/attribution surface, a commit-message example, or too subjective for an unattended rewrite.

### Verification Results

Verification performed before this report insertion:

| Command | Result |
| --- | --- |
| `git diff --check` | Passed |
| Professionalization keyword reruns | Passed for current public/source targets; remaining matches were archive history, deliberate examples, generated/dependency metadata, or prior audit text |
| Prompt-pack reads | Passed for v6 `00`, `00A`, and `07A`; earlier v5 path was stale and unavailable |

Final repo-native verification after this report update:

| Command | Result |
| --- | --- |
| `git diff --check` | Passed |
| `uv run ...` initial attempts | Failed before execution because `uv` was not on the default shell `PATH`; `/home/jer/.local/bin/uv` and `/tmp/codex-uv/uv` were then located |
| `PATH=/home/jer/.local/bin:$PATH uv run ruff check ...changed Python files...` | Passed; `All checks passed!` |
| `PATH=/home/jer/.local/bin:$PATH uv run ruff format --check ...changed Python files...` | Passed; `13 files already formatted` |
| `PATH=/home/jer/.local/bin:$PATH uv run zensical build --clean --strict` | Passed; `No issues found` |
| `PATH=/home/jer/.local/bin:$PATH DYNACONF_ENV=development uv run pytest tests/unit/test_imports.py -q -s` | Passed; `43 passed, 2 warnings in 8.93s` with existing Streamlit bare-mode warnings during import coverage |
| `PATH=/home/jer/.local/bin:$PATH make check` | Passed; Ruff check/format, mypy on 422 source files, Interrogate at `79.6%` versus `73.0%` threshold, and Bandit with no medium/high issues |
| `git status --short --ignored` | Passed for tracked review; generated cache/build artifacts were cleaned after verification; `.venv/`, `web/frontend/node_modules/`, and ignored local data caches remain untracked by design |

### Risks, Assumptions, And Follow-Ups

- This was a large-repo, risk-based pass, not an exhaustive line-by-line review of all 1013 tracked files.
- Archived planning docs still contain older agent/session and production-ready wording. They were left as historical records; a separate archive-curation decision would be needed before rewriting them.
- The CLI disclaimer still uses warning glyphs and box drawing. It was left unchanged because it is a deliberate user-facing warning surface.
- No public API, command name, test semantics, data format, dependency, CI policy, release process, licensing, or governance artifact was changed.
- Recommended follow-up: if maintainers want a stricter public-docs tone, run a focused docs-site editorial pass over `docs_site/` and current non-archive `docs/` pages only.

## Audit Metadata

- Audit date: 2026-07-05
- Target repository root: `/home/jer/repos/finbot`
- Branch: `codex/maintenance-audit-2026-07-05`
- User-supplied prompt-pack path: `/mnt/c/Users/jer/Downloads/codex-repo-health-goal-prompts-entrypoint-v5-deep-evidence`
- Resolved prompt-pack root: `/mnt/c/Users/jer/Downloads/codex-repo-health-goal-prompts-entrypoint-v5-deep-evidence/codex-repo-health-goals-entrypoint-v5-deep-evidence`
- Resolution note: the supplied path was the parent of one extracted directory containing `RUN_THIS_FIRST.md` and `codex-goals/`.
- Report location: `docs/maintenance-audit.md`, using the existing `docs/` tree.

## Prompt-Pack Files Read

Required files read from the resolved prompt-pack root:

1. `RUN_THIS_FIRST.md`
2. `MANIFEST.md`
3. `codex-goals/00-shared-repo-native-autonomous-safety-contract.md`
4. `codex-goals/00A-deep-evidence-and-coverage-gates.md`
5. `codex-goals/12-single-goal-sequential-repo-health-suite.md`

Pass files read and applied in the required suite order:

1. `codex-goals/01-general-code-quality-docs-maintenance.md`
2. `codex-goals/04-test-coverage-regression.md`
3. `codex-goals/03-security-privacy-secrets.md`
4. `codex-goals/05-ci-automation-developer-workflow.md`
5. `codex-goals/06-dependency-package-hygiene.md`
6. `codex-goals/07-documentation-onboarding.md`
7. `codex-goals/02-architecture-maintainability.md`
8. `codex-goals/09-performance-scalability.md`
9. `codex-goals/10-database-data-migration-health.md`
10. `codex-goals/08-release-readiness.md`
11. `codex-goals/11-public-repo-presentation.md`

## Repo Profile

Finbot is a Python financial data collection, simulation, optimization, analytics, backtesting, and dashboard platform with a FastAPI backend and a Next.js frontend. The repository is public/reviewable in presentation, but its unattended maintenance risk is medium because finance simulations, data-provider credentials, generated data files, Docker/release workflows, and package metadata can affect reproducibility or external users.

Stack inferred from repository evidence:

- Python package/runtime: `pyproject.toml`, `uv.lock`, `finbot/`, `scripts/`, `tests/`
- Package manager: uv for Python, Corepack/pnpm for `web/frontend`
- Python verification: Ruff, mypy, pytest, Bandit, Interrogate, Zensical
- Frontend verification: TypeScript `tsc`, Next.js build, Playwright in CI
- Backend/API: FastAPI under `web/backend`
- Docs: Zensical with `mkdocs.yml`, source docs in `docs_site/`, long-form docs in `docs/`
- CI/CD: GitHub Actions under `.github/workflows/`
- Deployment/infrastructure: root `Dockerfile`, `docker-compose.yml`, `web/Dockerfile.backend`, `web/Dockerfile.frontend`

Repo-local instructions and conventions considered:

- `AGENTS.md`, with `CLAUDE.md` and `GEMINI.md` as symlinks
- `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `DISCLAIMER.md`, `CHANGELOG.md`
- `pyproject.toml`, `Makefile`, `.pre-commit-config.yaml`, `.github/workflows/*.yml`
- `docs/adr/ADR-011-nautilus-decision.md`, `docs/adr/ADR-016-zensical-docs-platform.md`, `docs/guides/*`
- Existing style: small targeted edits, uv-managed dependencies, Ruff formatting, pytest tests, no broad architecture rewrites

## Reviewable Inventory And Coverage Tier

Inventory commands run:

- `pwd`
- `git rev-parse --show-toplevel`
- `git status --short --branch`
- `git ls-files | wc -l`
- `git ls-files | awk ...`
- `git ls-files | rg '\.(py|ts|tsx|js|mjs|md|rst|yml|yaml|toml|json|css|sh)$' | xargs wc -l | tail -n 1`
- `find . -maxdepth 2 -type d | sort`

Inventory results:

- Tracked files: `1012`
- Reviewable text lines across common source/docs/config extensions: about `163001`
- Python text total from tracked `*.py`: `81077` lines
- Category counts from tracked files:
  - `finbot/`: `430`
  - `web/backend/`: `32`
  - `web/frontend/`: `124`
  - `tests/`: `126`
  - `docs/` and `docs_site/`: `231`
  - `scripts/`: `11`
  - `.github/`: `14`
  - Docker/container files: `2` root-level matches, plus `web/Dockerfile.backend` and `web/Dockerfile.frontend`
  - root package/config files counted by the inventory expression: `5`

Coverage tier: large repository. This run used risk-based coverage rather than claiming a full file-by-file review.

Coverage emphasis:

- repo instructions, root README/setup/docs, package manifests, lockfiles, Makefile, CI workflows, Docker/deploy surfaces;
- Python public entry points, config/accessors, API constants, simulation modules, Nautilus helper scripts, test suites around touched behavior;
- FastAPI backend entry/config/router/schema surfaces;
- Next.js frontend package/scripts/env usage and build/typecheck path;
- docs site setup/config/getting-started/API/contributing pages and notebook docs;
- security-sensitive API-key, env var, CORS, client/server env, and workflow secret-reference surfaces;
- data/storage surfaces: parquet/file-backed data constants, contract schema/versioning, API schemas, and absence of ORM/SQL migration stack.

Excluded from manual review except for presence/status:

- `.git/`, `.venv/`, `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/`, `.hypothesis/`, `__pycache__/`, `site/`, `logs/`
- lockfiles were reviewed for intentional change/presence and verification, not line-by-line
- tracked generated/legal/license artifacts such as `THIRD_PARTY_LICENSES.md` were checked for presence only
- ignored/generated local artifacts were cleaned only when clearly reproducible; dependency installs and local data caches were left intact

## Command And Search Ledger

| Command/probe | Purpose | Result |
| --- | --- | --- |
| `git status --short --branch` | Preserve current worktree and branch context | Passed; dirty maintenance branch, no staged files |
| `git diff --stat` / `git diff --name-only` | Review diff coherence | Passed; targeted code/docs/config/test/lockfile/report diff |
| `rg --files ...prompt-pack...` | Locate v5 prompt-pack files | Passed; valid root found one level below supplied path |
| `wc -l .../codex-goals/*.md` | Confirm prompt pass inventory size | Passed; all required pass files present |
| `find . -maxdepth 2 -type d | sort` | Repo structure inventory | Passed |
| `git ls-files | awk ...` | File category inventory | Passed; counts recorded above |
| `rg -n '\b(TODO|FIXME|HACK|XXX)\b' ...` | Code/docs maintenance markers | Passed; 30 matches across 15 files, mostly archived docs/WIP utilities |
| `rg -n 'except (Exception|BaseException)|except:' finbot web/backend scripts` | Broad exception probe | Passed; 130 matches, mostly API/router defensive boundaries and fallback helpers |
| `git ls-files '*.py' | xargs wc -l | sort -nr | head -n 20` | Large/hotspot Python files | Passed; largest source hotspots include Nautilus adapter, backtesting router, scrapers |
| `rg -l -i '(secret|token|password|private key|credential|api...` | Security/privacy surface discovery | Passed; 143 files with security/env/auth terms, reviewed by path and targeted manual inspection |
| `rg -n 'ALPHA_VANTAGE|RAPIDAPI|ALPACA|TWELVEDATA|NASDAQ|BUREAU|GOOGLE_FINANCE|DYNACONF|NEXT_PUBLIC_API_URL|CORS|allow_origins' ...` | Env var and client/server config comparison | Passed; missing RapidAPI `.env.example` placeholder fixed |
| `rg -n 'NEXT_PUBLIC_|process\.env|import\.meta\.env' web/frontend/...` | Client-visible env probe | Passed; only `NEXT_PUBLIC_API_URL` found in frontend source/docs |
| `rg -l -i '(sqlalchemy|alembic|prisma|supabase|postgres|sqlite|mysql|mongodb|migration|schema|seed|database|\bdb\b|query)' ...` | Database/data/migration discovery | Passed; schemas/file constants found, no ORM/SQL migration stack |
| `find . -maxdepth 4 ... -iname '*migration*' -o -iname '*schema*' ...` | Filesystem database/migration probe | Passed; contract schemas and audit schema only; cache paths excluded from decision |
| `rg --files -g 'pyproject.toml' -g 'uv.lock' ...` | Package/config inventory | Passed |
| `rg --files docs docs_site README.md ...` | Documentation inventory | Passed |
| `rg -n 'pct_change\(' finbot/services/simulation ...` | Missing-data behavior probe | Passed; remaining simulation production calls made explicit |
| Targeted red pytest command for new missing-price warning tests | Prove regressions fail before production code change | Failed as expected with pandas `FutureWarning` at five sites |
| Targeted green pytest command for same tests | Verify production changes | Passed; `5 passed in 3.16s` |

## Baseline And Verification Notes

Strong verification had previously been run on the branch before the v5 evidence upgrade:

- `PATH=/tmp/codex-uv:$PATH make check`: passed
- `DYNACONF_ENV=development /tmp/codex-uv/uv run --all-extras --python 3.13 pytest tests/ -q -s`: passed, `1931 passed, 10 skipped, 7 deselected, 90 warnings`
- `/tmp/codex-uv/uv run --all-extras --python 3.13 zensical build --clean --strict`: passed
- frontend `corepack pnpm typecheck`: passed
- frontend `corepack pnpm build`: passed
- workflow YAML check: passed
- Python 3.11 import smoke and `tests/unit/test_imports.py`: passed

Fresh final verification after the v5 report and additional simulation changes is recorded in the "Final Verification" section.

Local caveat:

- Default pytest capture in this shell can fail with `FileNotFoundError` from `_pytest/capture.py` when stopping global capture. The full suite is run with `-s` in this environment; CI/default pytest commands were not changed because this appears local to the shell/runtime.

## Pass Completion Table

| # | Pass | Status |
| --- | --- | --- |
| 1 | General code quality, docs, and maintenance | Fixed local issues; no broad refactor |
| 2 | Test coverage and regression confidence | Added/updated regression tests |
| 3 | Security, privacy, and secrets hygiene | Fixed env/accessor hygiene; no secrets exposed |
| 4 | CI, automation, and developer workflow | Fixed workflow/script drift |
| 5 | Dependency and package hygiene | Fixed Python metadata/optional marker; lockfile refreshed |
| 6 | Documentation and onboarding | Updated setup/config/verification docs |
| 7 | Architecture and maintainability | No architecture rewrite; map and recommendations documented |
| 8 | Performance and scalability | Fixed low-risk missing-data/vectorized simulation issue |
| 9 | Database, data, and migration health | No-op with evidence; no DB/ORM/migration stack |
| 10 | Release readiness | Fixed metadata/readiness docs; no release actions |
| 11 | Public repo presentation | Fixed factual public-facing docs; no marketing/process additions |

## Pass Evidence

### 1. General Code Quality, Docs, And Maintenance

Scope decision: applies broadly because the repo has active Python services, helper scripts, docs, CI, package metadata, and frontend/backend surfaces.

Surfaces inspected:

- `finbot/services/simulation/fund_simulator.py`
- `finbot/services/simulation/stock_index_simulator.py`
- `finbot/services/simulation/adj_finders.py`
- `finbot/services/simulation/bond_index_simulator.py`
- `finbot/services/simulation/bond_ladder/bond_ladder_simulator.py`
- `finbot/services/simulation/sim_specific_funds.py`
- `finbot/services/simulation/monte_carlo/monte_carlo_simulator.py`
- `finbot/services/simulation/monte_carlo/multi_asset_monte_carlo.py`
- `scripts/test_nautilus_install.py`
- `scripts/test_nautilus_backtest.py`
- `scripts/generate_backtesting_baseline.py`
- `scripts/benchmark/e6_compare_backtrader_vs_nautilus.py`
- `Makefile`, `.github/workflows/ci.yml`, `pyproject.toml`
- `README.md`, `docs_site/`, `notebooks/README.md`, `AGENTS.md`

Searches/probes run:

- TODO/FIXME/HACK/XXX search across source/docs/config
- broad exception search across `finbot`, `web/backend`, and `scripts`
- `pct_change(` search across simulation code
- changed-file diffs for config/API/simulation/tests/scripts/docs

Candidate findings considered:

- `pct_change()` default missing-data fill in simulation paths: fixed.
- RapidAPI headers reusing standard Alpha Vantage key: fixed.
- stale Nautilus helper script constructor usage and imprecise script typing: fixed.
- Makefile commands swallowing type/security/docstring failures: fixed.
- broad TODO/WIP markers in archived docs and unverified utility modules: deferred; larger owner prioritization, not a coherent maintenance diff.
- broad exception handling in backend routers and fallback helpers: reviewed as existing API-boundary pattern; no safe mechanical rewrite.

Change-gate decisions:

- Implemented changes are local, covered by existing tooling/tests, and align with existing uv/Ruff/pytest patterns.
- Deferred TODO/broad exception cleanups would be larger behavior or policy changes and were documented instead.

Verification:

- Targeted red/green tests for missing-price behavior ran and passed after the fix.
- Full final verification is recorded below.

### 2. Test Coverage And Regression Confidence

Scope decision: applies because the repo has a broad pytest suite, frontend e2e suite, unit/integration/performance/property directories, and touched behavior in simulation/API-key code.

Surfaces inspected:

- `tests/unit/test_fund_simulator_e2e.py`
- `tests/unit/test_index_simulators.py`
- `tests/unit/test_adj_finders.py`
- `tests/unit/test_simulation_wrappers_and_registry.py`
- `tests/unit/test_new_strategies.py`
- `tests/unit/test_alpha_vantage_utils.py`
- `tests/unit/test_imports.py`
- `tests/integration/`, `tests/performance/`, `tests/property/`, `tests/validation/`

Searches/probes run:

- `rg -n 'monte_carlo|bond_index|bond_ladder|sim_ntsx|adj_finders' tests finbot/services/simulation`
- `rg -n 'pct_change\(' finbot/services/simulation tests/...`
- targeted pytest red run for five new missing-price warning tests
- targeted pytest green rerun for the same tests

Tests added or updated:

- Fund simulator missing prices do not synthesize flat returns.
- Stock index simulator missing prices do not forward-fill.
- Bond index simulator missing prices do not forward-fill.
- Adjustment finder missing prices do not trigger pandas fill warnings.
- NTSX composite missing component prices do not trigger pandas fill warnings.
- Single-asset Monte Carlo missing prices do not trigger pandas fill warnings.
- Multi-asset Monte Carlo missing prices do not trigger pandas fill warnings.
- Alpha Vantage RapidAPI uses the RapidAPI-specific accessor and does not call the standard key accessor.

Candidate findings considered:

- Missing regression coverage for fixed pandas behavior: fixed.
- Broad new coverage gates: deferred; repo already has coverage config and this would change policy.
- Frontend Playwright expansion: deferred; CI already owns mocked Chromium suite and no frontend behavior changed.

Change-gate decisions:

- Tests were added near existing pytest unit tests, using monkeypatch and deterministic synthetic data already common in the repo.
- No new test framework, external services, or credentialed integration test was added.

Verification:

- Red run failed at expected pandas `FutureWarning` sites before production changes.
- Green targeted rerun passed.
- Full suite final result is recorded below.

### 3. Security, Privacy, And Secrets Hygiene

Scope decision: applies because the repo uses multiple provider credentials, GitHub Actions secrets, FastAPI CORS config, frontend environment variables, logs, and public docs.

Surfaces inspected:

- `finbot/config/.env.example`
- `finbot/config/api_key_manager.py`
- `finbot/config/settings_accessors.py`
- `finbot/constants/api_constants.py`
- `finbot/utils/data_collection_utils/alpha_vantage/_alpha_vantage_utils.py`
- `finbot/libs/api_manager/_apis/alpha_vantage_rapidapi.py`
- `web/backend/config.py`
- `web/backend/main.py`
- `web/frontend/src/app/layout.tsx`
- `.github/workflows/*.yml`
- `README.md`, `docs_site/user-guide/configuration.md`, `docs_site/api/cli.md`, `AGENTS.md`

Searches/probes run:

- secret/auth/env term path scan over source/docs/tests/config excluding lockfiles and this report
- explicit env-var scan for data-provider keys and CORS/client env usage
- frontend `NEXT_PUBLIC_`/`process.env` scan
- targeted manual inspection of backend CORS settings and frontend env use

Candidate findings considered:

- Standard Alpha Vantage key used for RapidAPI header: fixed with `ALPHA_VANTAGE_RAPIDAPI_KEY`.
- RapidAPI key missing from `finbot/config/.env.example`: fixed.
- likely secret scan produced docs/placeholders/workflow secret references, not hardcoded production credentials.
- `web/backend` CORS defaults allow local frontend origins only; no change.
- `finbot/libs/api_manager/_apis/alpha_vantage_rapidapi.py` uses non-raising `settings.get(...)` at import time: intentionally unchanged to avoid import failures for optional credentials.

Change-gate decisions:

- Credential separation was a clear local correctness/security hygiene issue with tests and docs coverage.
- No secret rotation, cloud changes, auth redesign, or production policy change was attempted.

Verification:

- `tests/unit/test_alpha_vantage_utils.py` updated.
- Bandit medium/high gate is part of final verification.
- Secret values are not printed in this report.

### 4. CI, Automation, And Developer Workflow

Scope decision: applies because the repo has a Makefile, uv scripts, pre-commit, GitHub Actions, frontend package scripts, Docker helpers, release and docs workflows.

Surfaces inspected:

- `Makefile`
- `.github/workflows/ci.yml`
- `.github/workflows/ci-heavy.yml`
- `.github/workflows/docs.yml`
- `.github/workflows/release.yml`
- `.github/workflows/docker-security-monitor.yml`
- `.pre-commit-config.yaml`
- `web/frontend/package.json`
- `web/frontend/pnpm-lock.yaml`
- `Dockerfile`, `docker-compose.yml`, `web/Dockerfile.backend`, `web/Dockerfile.frontend`

Searches/probes run:

- package/config inventory via `rg --files -g ...`
- CI YAML manual inspection
- Makefile command inspection
- frontend package script inspection

Candidate findings considered:

- `make type`, `make docstring`, and `make security` swallowed failures: fixed to fail fast.
- CI mypy checked only `finbot/` while local command checked `finbot/ scripts/`: fixed.
- advisory CI docstring/security jobs remain `continue-on-error`: deferred as repo policy.
- Docker build/security scan not run: deferred to release/CI path due heavier container work.
- Playwright e2e not run locally: deferred because repo docs keep mocked Chromium e2e CI-only unless needed.

Change-gate decisions:

- Makefile/CI changes align existing commands rather than adding new tooling.
- No deploy/release/publish/migration command was run.

Verification:

- `make check`, YAML check, frontend typecheck/build, and final verification are recorded below.

### 5. Dependency And Package Hygiene

Scope decision: applies because the repo has Python package metadata/lockfile, frontend package/lockfile, runtime constraints, dependency groups, extras, Docker/CI runtime setup, and public classifiers.

Surfaces inspected:

- `pyproject.toml`
- `uv.lock`
- `web/frontend/package.json`
- `web/frontend/pnpm-lock.yaml`
- `.github/workflows/ci.yml`
- `README.md`, `docs_site/user-guide/installation.md`, `AGENTS.md`

Searches/probes run:

- package/config inventory
- Python 3.11 and Nautilus metadata comparison
- `uv lock --python 3.13`
- Python 3.11 import smoke and import tests

Dependency/config changes:

| Package/config | Change | Reason | Risk | Verification |
| --- | --- | --- | --- | --- |
| `pyproject.toml` `requires-python` | `>=3.12,<3.15` to `>=3.11,<3.15` | Match repo instructions/docs and validated non-Nautilus support | Low | Python 3.11 import tests passed |
| `pyproject.toml` classifiers | Added Python 3.11 | Match supported runtime metadata | Low | Static review and smoke tests |
| `pyproject.toml` `nautilus` extra | Added `python_version >= '3.12'` marker | `nautilus-trader` does not support Python 3.11 | Low | Python 3.11 and 3.13 uv runs |
| `uv.lock` | Refreshed | Required by metadata/marker change | Medium review size | `uv sync --locked --all-extras --python 3.13` passed |
| `.github/workflows/ci.yml` | Type-checks `scripts/` too | Align local/CI checked scope | Low | mypy and YAML check passed |

Candidate findings considered:

- Broad package upgrades/audit fixes: deferred; unsafe for unattended repo-health pass.
- Removing dependencies by static search only: deferred; high false-positive risk in docs/scripts/notebooks.
- pnpm dependency changes: no-op; no frontend dependency issue found and frontend code did not change.

Change-gate decisions:

- Python metadata changes are small, documented, and verified across supported interpreter surfaces.
- No major-version upgrade or package-manager migration was performed.

Verification:

- uv lock/sync, Python 3.11 smoke, mypy, tests, and build checks recorded below.

### 6. Documentation And Onboarding

Scope decision: applies because the repo has root docs, a docs site, notebook docs, frontend/backend docs, release/security/disclaimer docs, and command/env examples.

Surfaces inspected:

- `README.md`
- `docs_site/user-guide/installation.md`
- `docs_site/user-guide/configuration.md`
- `docs_site/user-guide/getting-started.md`
- `docs_site/api/cli.md`
- `docs_site/contributing.md`
- `notebooks/README.md`
- `AGENTS.md`
- `finbot/config/.env.example`

Documentation inventory:

- Root public docs: `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `DISCLAIMER.md`, `CHANGELOG.md`, `LICENSE`
- Docs site source: `docs_site/`, built by Zensical using `mkdocs.yml`
- Engineering docs: `docs/adr/`, `docs/guides/`, `docs/planning/`, `docs/research/`, `docs/security/`
- Notebook docs: `notebooks/README.md`
- Web docs: `web/README.md`, `web/frontend/README.md`

Searches/probes run:

- documentation inventory via `rg --files docs docs_site README.md ...`
- env-var command scan across README/docs/config/workflows
- docs build as verification

Changes:

- Documented Python 3.11 support and Nautilus Python 3.12+ extra constraint.
- Updated env var lists for `ALPHA_VANTAGE_RAPIDAPI_KEY`, Alpaca, Twelve Data, and existing data-provider keys.
- Clarified verification commands and Makefile behavior.
- Added `ALPHA_VANTAGE_RAPIDAPI_KEY` to `finbot/config/.env.example`.

Candidate findings considered:

- Docs site system replacement or new docs process: not applicable; existing Zensical setup works.
- Public branding/assets/screenshots: owner decision; not added.
- Full link-checking: deferred; strict docs build was used as the repo-native docs check.

Change-gate decisions:

- Docs changes correct actual commands/config; no aspirational process or unsupported claims added.

Verification:

- Zensical strict build final result recorded below.

### 7. Architecture And Maintainability

Scope decision: applies as an audit/map and small local maintainability pass; broad architecture changes are not safe or needed in this run.

Architecture map as found:

- `finbot/config/`: Dynaconf/project settings, lazy API key management, typed accessors.
- `finbot/constants/`: path, API, security, database/file constants and tracked collection manifests.
- `finbot/libs/`: API manager, audit logging, async logging, utility infrastructure.
- `finbot/core/contracts/`: engine-agnostic contracts, versioning, serialization, schemas, risk/portfolio/realtime/factor analytics contracts.
- `finbot/services/`: execution, backtesting, simulations, optimization, health economics, data quality, risk/portfolio/factor analytics, realtime data.
- `finbot/utils/`: data collection, finance, pandas, datetime, data science, plotting, request, and threading utilities.
- `scripts/`: daily update, release/test helpers, benchmark/baseline helpers.
- `web/backend/`: FastAPI app, routers, schemas, serializers.
- `web/frontend/`: Next.js App Router frontend, shared components, stores, API/types, Playwright tests.
- `tests/`: unit, integration, property, performance, validation tests.

Surfaces inspected:

- root docs/ADRs describing architecture and runtime surfaces
- largest Python files from line-count probe
- config/API key boundaries
- simulation package boundaries
- FastAPI app/config/routers/schemas
- frontend package and env surface
- Nautilus/backtrader adapter helper scripts

Candidate findings considered:

- package splitting or service-layer restructuring: deferred; broad architecture decision.
- Nautilus adapter large file: noted as a hotspot but not refactored; high behavior surface.
- backend `backtesting.py` router large file: noted as a hotspot but not refactored; page decomposition already has planning history.
- duplicated pandas missing-data assumptions across simulation modules: fixed locally.
- script API drift/type imprecision: fixed.

Change-gate decisions:

- Local missing-data and helper-script fixes reduce friction without changing package boundaries.
- No new architecture pattern, module move, public API rename, or framework was introduced.

Verification:

- mypy, tests, and docs/build checks cover the changed boundaries.

### 8. Performance And Scalability

Scope decision: applies to vectorized simulation paths, data pipelines, backend routes, frontend build, and benchmark helpers, but only clear low-risk fixes were appropriate.

Surfaces inspected:

- `finbot/services/simulation/*`
- `finbot/services/simulation/monte_carlo/*`
- `finbot/services/simulation/bond_ladder/bond_ladder_simulator.py`
- `scripts/benchmark/e6_compare_backtrader_vs_nautilus.py`
- `benchmarks/`
- `web/backend/routers/*`
- `web/frontend/package.json`

Searches/probes run:

- `pct_change(` scan across simulation code
- largest Python file line-count probe
- TODO probe, including known performance TODOs in BLS and datetime utilities

Candidate findings considered:

- implicit pandas forward-fill causing repeated hidden missing-data work/future warning in vectorized simulations: fixed with explicit `fill_method=None`.
- `finbot/utils/datetime_utils/get_missing_us_business_dates.py` TODO for efficiency: deferred; no current failing check and not touched by workflow.
- BLS utility TODO pulling all data: deferred; provider/API behavior and caching policy need focused data-collection pass.
- profiling/caching/worker additions: not repo-native for this pass.

Change-gate decisions:

- Explicit missing-data handling preserves vectorized computation and prevents future pandas behavior drift.
- No speculative micro-optimization or infrastructure cache was added.

Verification:

- Red/green missing-price tests and full test suite final result.

### 9. Database, Data, And Migration Health

Scope decision: database migrations are mostly not applicable. The repo has data files, schemas, file-backed parquet conventions, and contract versioning, but no live DB/ORM/SQL migration system was found.

Surfaces inspected:

- `finbot/constants/db_constants.py`
- `finbot/constants/path_constants.py`
- `finbot/core/contracts/schemas.py`
- `finbot/core/contracts/versioning.py`
- `finbot/core/contracts/serialization.py`
- `finbot/libs/audit/audit_schema.py`
- `web/backend/schemas/*.py`
- `finbot/data/`
- `finbot/constants/tracked_collections/*.csv`
- docs for data quality, contract schema versioning, checkpoint/audit trails

Searches/probes run:

- DB/ORM/migration keyword path scan
- filesystem search for migration/schema/seed/sql/database/db filenames excluding cache/build dirs
- manual inspection of file-backed constants and schema/versioning surfaces

Candidate findings considered:

- no Alembic/Django/Prisma/SQLAlchemy/Supabase/Postgres migration stack found: no-op.
- cache files matching `cache.db`: excluded as local tool caches.
- contract schema migration helpers: existing repo pattern, no change needed.
- production data mutation/migration: not performed.

Data safety notes:

- No database connections opened.
- No migrations created or run.
- No production data, local parquet data, or remote provider data modified.
- No seed reset/backfill/truncate operation attempted.

Verification:

- Static inventory/no-op evidence plus final tests/builds.

### 10. Release Readiness

Scope decision: applies as package/app/container/docs readiness review. Publishing, version bumping, tags, deploys, and release policy choices are out of scope.

Surfaces inspected:

- `pyproject.toml` package metadata/classifiers/scripts/URLs
- `uv.lock`
- `README.md`
- `LICENSE`, `DISCLAIMER.md`, `SECURITY.md`, `CHANGELOG.md`, `CHANGELOG_GENERATED.md`
- `.github/workflows/release.yml`, `.github/workflows/publish-testpypi.yml`
- `.github/workflows/docker-security-monitor.yml`
- `Dockerfile`, `docker-compose.yml`, `web/Dockerfile.backend`, `web/Dockerfile.frontend`
- `docs/guides/release-process.md`, `docs/guides/RELEASE-QUICK-REFERENCE.md`, TestPyPI docs

Release-readiness checklist:

| Area | Status | Evidence |
| --- | --- | --- |
| Package metadata | Fixed | Python 3.11 metadata and Nautilus marker aligned |
| Lockfile | Fixed | `uv.lock` refreshed intentionally |
| License | Ready/unchanged | MIT license exists; no license choice made |
| README install/test docs | Fixed | Python/env/verification docs updated |
| CI quality commands | Fixed | mypy scope aligned and Makefile fail-fast |
| Docs build | Verified | Zensical strict build final result |
| Frontend build/typecheck | Verified | final frontend typecheck/build result |
| Docker image/security scan | Deferred | heavier release path, not run unattended |
| Version bump/tag/release | Not applicable | no release action authorized |
| Publishing/TestPyPI | Not run | no publish action authorized |

Candidate findings considered:

- release automation changes: deferred; policy/owner decision.
- Docker scan before release candidate: recommended follow-up.
- version bump/changelog update: not done; no release requested.

Verification:

- CI-equivalent local checks and docs/frontend builds recorded below.

### 11. Public Repo Presentation

Scope decision: applies because the repo has public package metadata, GitHub URLs, docs, license/disclaimer/security files, and public-facing README/docs site content. The pass is factual presentation, not marketing.

Surfaces inspected:

- `README.md`
- `pyproject.toml` project metadata/URLs/classifiers
- `LICENSE`, `DISCLAIMER.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`
- `docs_site/index.md`, install/config/getting-started/API pages
- `docs/security/`, `docs/guides/`, `docs/adr/`
- `.github/ISSUE_TEMPLATE`, `.github/PULL_REQUEST_TEMPLATE.md`, `.github/CODEOWNERS`

Searches/probes run:

- docs inventory
- package/config inventory
- env/secret/public placeholder scan
- strict docs build

Candidate findings considered:

- stale Python support and env var docs: fixed.
- public-facing RapidAPI docs missing: fixed.
- badges/screenshots/benchmarks/brand assets: not added; owner decision.
- support guarantees/production readiness claims: not added.
- license choice: unchanged existing MIT.

Change-gate decisions:

- Public docs were corrected to match current code and verified commands.
- No public posture, marketing claim, governance process, or GitHub setting was invented.

Verification:

- docs build and package/static checks recorded below.

## Changes Applied

Code/config/test changes:

- Added `ALPHA_VANTAGE_RAPIDAPI_KEY` to the lazy API key manager and settings accessors.
- Updated RapidAPI request headers to use `get_alpha_vantage_rapidapi_key()`.
- Added the RapidAPI placeholder to `finbot/config/.env.example`.
- Made simulation `pct_change()` calls explicit with `fill_method=None` across fund, stock index, bond index, bond ladder, adjustment finder, NTSX composite, and Monte Carlo paths.
- Updated Nautilus helper scripts for the current `NautilusAdapter(price_histories=...)` API.
- Tightened script typing in baseline/benchmark helpers so `mypy finbot/ scripts/` passes.
- Changed Makefile `type`, `docstring`, and `security` targets to fail on errors.
- Aligned `.github/workflows/ci.yml` mypy scope with the verified local command.
- Aligned Python metadata with documented support and guarded the Nautilus optional extra to Python 3.12+.
- Refreshed `uv.lock`.

Documentation changes:

- Updated root README, docs site install/config/getting-started/API/contributing pages, notebooks README, and `AGENTS.md`.
- Documented Python 3.11 support, Nautilus 3.12+ constraint, env vars, verification commands, Makefile behavior, and provider key handling.
- Replaced the earlier v4 maintenance report with this v5 deep-evidence report.
- Updated `docs/planning/roadmap.md` to record this maintenance pass and carry recurring scheduled CI/data-update failures as explicit follow-ups.

Cleanup changes:

- Removed ignored local cache/build artifacts: `.cache/`, `.hypothesis/`, `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/`, `site/`, `interrogate_badge.svg`, Python `__pycache__/` directories, `web/frontend/.next/`, `web/frontend/tsconfig.tsbuildinfo`, and `web/frontend/next-env.d.ts`.
- Left `.venv/`, `web/frontend/node_modules/`, and ignored `finbot/data/` files in place as local dependency/data caches rather than junk.

Tests added or updated:

- `tests/unit/test_alpha_vantage_utils.py`
- `tests/unit/test_fund_simulator_e2e.py`
- `tests/unit/test_index_simulators.py`
- `tests/unit/test_adj_finders.py`
- `tests/unit/test_simulation_wrappers_and_registry.py`
- `tests/unit/test_new_strategies.py`

## Deferred Or Rejected Candidate Findings

- Broad TODO/WIP cleanup across archived planning docs, unverified utility modules, and provider helpers: deferred as a larger owner-prioritized cleanup.
- Broad exception handling in backend routers: unchanged because it is an established API error-boundary pattern; a focused API error-model pass would be safer.
- Large-file decomposition for Nautilus adapter/backtesting router: deferred; high blast radius and not needed for this maintenance diff.
- Dependency upgrades/removals/audit-fix rewrites: deferred; too broad and risky for unattended maintenance.
- Docker image build/security scan: deferred to release/CI because it is heavier and not needed to verify these changes.
- Playwright e2e: deferred to CI unless frontend behavior changes; frontend typecheck/build are still run.
- License, release, version, changelog, badge, public branding, and GitHub settings changes: owner decisions.
- Database migrations/indexes/constraints: not applicable; no database migration stack found.
- Recurring scheduled workflow failures on `main`: recorded as roadmap follow-ups rather than expanding this branch into credential, quota, Docker, or release validation work.

## Completion Maintenance Pass

Additional completion checks after the primary audit:

| Check | Result |
| --- | --- |
| `git status --short --branch` | Passed; dirty maintenance branch with scoped audit changes and untracked report |
| `git branch --show-current` | Passed; `codex/maintenance-audit-2026-07-05` |
| `git branch -vv --all` and `git ls-remote --heads origin` | Passed; local `main` and maintenance branch start from `origin/main`; remote branches before push were only `main` and `gh-pages` |
| `git rev-parse --abbrev-ref --symbolic-full-name @{u}` | Failed as expected; maintenance branch had no upstream before push |
| `gh --version` | Could not run; GitHub CLI is not installed in this shell |
| GitHub API open-PR query | Passed; `0` open PRs |
| GitHub API branch query | Passed; `2` remote branches before this branch was pushed: `main`, `gh-pages` |
| GitHub API Actions query | Passed; recent `main` status showed recurring `Scheduled Data Update` failures, one recent OpenSSF Scorecard success, a scheduled `CI Heavy` failure on 2026-06-29, and a push `CI` failure from 2026-06-28 |
| `python -c ...` API parsing attempts | Could not run because bare `python` is not on PATH; reran with `python3` |
| `python3 -c ...` API parsing attempts | Passed after simplifying quoting |
| `readlink CLAUDE.md` / `readlink GEMINI.md` | Passed; both remain relative symlinks to `AGENTS.md` |
| `git status --short --ignored` | Passed; confirmed only `.venv/`, `web/frontend/node_modules/`, and ignored data caches remained after generated-artifact cleanup |

Post-push GitHub status for commit `714f2c8`:

- `main` was fast-forwarded to the maintenance commit and pushed.
- The temporary `codex/maintenance-audit-2026-07-05` branch was deleted locally and remotely after merge.
- Open PR query after cleanup returned `0` open PRs.
- Remote branches after cleanup were `main` and `gh-pages`.
- `Deploy Documentation` run `28754119907` completed successfully.
- `CI` run `28754119917` completed with overall failure because `Docker Security Scan (cli)` and `Docker Security Scan (api)` failed at the Trivy image-scan step.
- All other observed CI jobs in run `28754119917` passed: lint/format, type check, security scan, docstring coverage, backtest parity gate, performance regression, frontend quality, and Python 3.11/3.12/3.13 tests.
- Public job-log download for the failed Docker jobs returned HTTP 403 without GitHub authentication, so the exact CVE list was not available from this shell; the workflow did upload Trivy results and security reports.

## Security And Privacy Notes

- No hardcoded production secrets were identified by the static path scan; reviewed matches were placeholders, docs, workflow secret references, or env var names.
- RapidAPI and standard Alpha Vantage credentials are now separated in request-time helpers.
- `finbot/libs/api_manager/_apis/alpha_vantage_rapidapi.py` intentionally keeps import-time non-raising settings access for optional credentials.
- Frontend env usage remains limited to `NEXT_PUBLIC_API_URL`.
- Backend CORS defaults are local frontend origins in `web/backend/config.py`.
- No secrets were printed, rotated, uploaded, or added.
- No author/contributor attribution was added in this pass; commit metadata and project text should continue to list only human contributors or allowed bot accounts.

## Final Verification

Fresh final verification after the completion cleanup and report update:

| Command | Result |
| --- | --- |
| `DYNACONF_ENV=development /tmp/codex-uv/uv run --all-extras --python 3.13 pytest ...targeted missing-price tests... -q -s` | Passed; `5 passed in 3.16s` |
| `PATH=/tmp/codex-uv:$PATH make check` | Passed; Ruff check passed, Ruff format left `580` files unchanged, mypy passed on `422` source files, Interrogate passed at `79.6%` against `73.0%`, Bandit found no medium/high issues and `23` low issues |
| `DYNACONF_ENV=development /tmp/codex-uv/uv run --all-extras --python 3.13 pytest tests/ -q -s` | Passed; `1936 passed, 10 skipped, 7 deselected, 92 warnings in 42.25s` |
| `/tmp/codex-uv/uv run --all-extras --python 3.13 zensical build --clean --strict` | Passed; `No issues found` |
| `PATH=/tmp/codex-node20/bin:$PATH NEXT_TELEMETRY_DISABLED=1 corepack pnpm typecheck` | Passed; `tsc --noEmit` completed |
| `PATH=/tmp/codex-node20/bin:$PATH NEXT_TELEMETRY_DISABLED=1 corepack pnpm build` | Passed; Next.js 16.2.6 production build compiled successfully and generated 17 app routes |
| `PATH=/tmp/codex-uv:$PATH uv run pre-commit run check-yaml --files .github/workflows/ci.yml` | Passed |
| `git diff --check` | Passed |
| `/tmp/codex-uv/uv run --all-extras --python 3.11 python -c "import finbot; print('import ok')"` | Passed; `import ok` |
| `DYNACONF_ENV=development /tmp/codex-uv/uv run --all-extras --python 3.11 pytest tests/unit/test_imports.py -q -s` | Passed; `43 passed, 2 warnings in 9.70s` |
| `/tmp/codex-uv/uv sync --locked --all-extras --python 3.13` | Passed; restored the contributor/all-extras Python 3.13 environment after Python 3.11 smoke tests |
| Attribution-pattern scan | Passed for changed project text; one existing guide match only warns against improper `Co-Authored-By` trailers |
| Secret-pattern scan | Passed; no matching token/key material found |

## Final Diff Summary

Pre-commit diff after final verification and generated-artifact cleanup:

- Branch: `codex/maintenance-audit-2026-07-05`
- Tracked diff before adding this untracked report: `36 files changed, 670 insertions(+), 51 deletions(-)`
- New report: `docs/maintenance-audit.md`
- Status before staging: modified CI/docs/config/source/tests/lockfile files plus untracked report
- Ignored files intentionally left in place: `.venv/`, `web/frontend/node_modules/`, and local ignored data caches

## Risks, Assumptions, And Intentionally Unchanged Areas

- Behavior is preserved except for intentional missing-data handling: implicit pandas forward-fill is no longer used in simulation return calculations.
- Missing prices now remain missing unless a function explicitly interpolates or fills them as part of its own logic.
- Python 3.11 support is for non-Nautilus surfaces; the `nautilus` extra is Python 3.12+.
- Mypy remains targeted to Python 3.12 semantics because all-extras environments include NautilusTrader stubs using Python 3.12 syntax.
- No release, deploy, publication, cloud/resource change, secret rotation, production migration, production data operation, or broad dependency upgrade was performed.

## Remaining Recommendations

- Investigate the local pytest capture `FileNotFoundError` separately; keep using `pytest -s` in this shell until resolved.
- Consider separate CI lanes for Python 3.11 non-Nautilus and Python 3.12+/3.13 all-extras coverage.
- Triage remaining test warnings, especially pandas frequency alias deprecations and framework/client deprecations.
- Review Bandit low-severity findings in a focused security cleanup if maintainers want to reduce advisory noise.
- Run Docker build/security scans before a release candidate.
- Consider focused follow-up passes for large hotspots: `finbot/adapters/nautilus/nautilus_adapter.py`, `web/backend/routers/backtesting.py`, provider data-fetch TODOs, and old archived planning docs.
