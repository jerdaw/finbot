# Finbot Roadmap

**Created:** 2026-02-10
**Last Updated:** 2026-02-25
**Status:** Priority 0-7 complete. Priority 8 Clusters A-C complete (Risk Analytics, Portfolio Analytics, Real-Time Data) (2026-02-25).

Improvements, fixes, and enhancements identified from comprehensive project evaluations. Organized by priority tier. Previous items (Priority 0-4) have been implemented. New Priority 5 items focus on making the project suitable for Ontario medical school admissions (OMSAS/CanMEDS frameworks).

See Completed Items table below and git history for details on implemented features.

**Current Plan Record:** None active. Last plan: `docs/planning/archive/IMPLEMENTATION_PLAN_12_P8_REALTIME_DATA_CLUSTER_C.md` (completed 2026-02-25)

---

## Priority 0: Bugs and Architectural Hazards ✓

All 6 items complete. Fixed logger duplication, import-time side effects, dangerous error handling, dual config system, ruff version mismatch, and added Dependabot.

## Priority 1: Critical Gaps ✓

All 3 items complete. Expanded test coverage (18 → 262 tests, 34.57% coverage), created 5 example notebooks with findings, and produced 3 research summaries.

**Remaining (Deferred — Not Blocking):**
- [x] Add tests for `bond_ladder_simulator` end-to-end — P7.23 complete (23 tests, synthetic yield data)
- [x] Add tests for `backtest_batch`: parallel execution, result aggregation — P7.23 complete (11 tests)
- [x] Add tests for `rebalance_optimizer` — P7.23 complete (5 tests)
- [ ] Add tests for `approximate_overnight_libor` (requires FRED data)
- [ ] Add tests for data collection utilities: `get_history`, `get_fred_data` (requires mock API responses)

*Completed deferred items:* integration tests (P7.2), coverage 60%+ target (P7.2 → 61.63%), blog posts (P7.5–7.7).

## Priority 2: High-Impact Improvements ✓

All 6 items complete. Added CLI interface (4 commands), fixed code smells, refactored fund simulations to data-driven config, improved git history (CHANGELOG.md), completed incomplete components, added Makefile.

**Remaining (Deferred — Not Blocking):**
- [ ] Apply data-driven config pattern to `sim_specific_bond_indexes.py` (only 3 functions, not worth refactoring)

*Completed deferred items:* conventional commits (P5.36 — commitlint hook + guide added).

## Priority 3: Moderate Improvements ✓

All 7 items complete. Improved documentation (160 module docstrings, MkDocs site, ADRs), strengthened type safety (146 → 0 mypy errors), added performance benchmarks, improved CI/CD pipeline, improved pre-commit hooks, modernized pyproject.toml metadata, consolidated package layout.

**Remaining (Deferred — Not Blocking):**
- [x] Enable stricter mypy settings (`disallow_untyped_defs`, etc.) — P7.1 audit complete; phased roadmap in `docs/planning/mypy-phase1-audit-report.md`

*Completed deferred items:* py.typed marker (P5.2.11), SHA pinning for CI (2026-02-17), scheduled CI (P7.3).

## Priority 4: Polish and Extensibility ✓

All 6 items complete. Added containerization, Streamlit web dashboard (6 pages), health economics extension (QALY simulator, CEA, treatment optimizer), additional strategies (DualMomentum, RiskParity, multi-asset Monte Carlo, inflation-adjusted returns), migrated from Poetry to uv, added data quality/observability.

**Remaining (Deferred — Not Blocking):**
- [ ] Add options overlay strategy (covered calls, protective puts) — requires options pricing model, Greeks calculations, and options chain data
- [ ] Investigate epidemiological backtesting — not feasible with Backtrader (finance-specific); would need purpose-built SIR/SEIR simulator

---

## Priority 5: Admissions-Focused Improvements (OMSAS/CanMEDS)

New improvements identified 2026-02-12 to strengthen the project for Ontario medical school admissions. Focus on demonstrating leadership, collaboration, professionalism, scholarship, and impact aligned with CanMEDS competency framework.

### 5.1 Governance & Professionalism (Immediate Wins - All Size S, ~2 hours total)

**Why these matter for admissions:** Professional governance artifacts demonstrate maturity, accountability, and leadership. GitHub Community Standards compliance signals project legitimacy.

1. **Add LICENSE file to repository root** (S: 10 min)
   - **CanMEDS:** Professional (legal compliance, governance)
   - **What:** Create standard MIT LICENSE file at repo root with name and year 2024
   - **Evidence:** LICENSE file visible on GitHub, auto-detected license badge
   - **Status:** ✅ Complete (2026-02-12)

2. **Fix version mismatch** (S: 5 min)
   - **CanMEDS:** Professional (attention to detail, credibility)
   - **What:** Update pyproject.toml version to "1.0.0" to match CHANGELOG
   - **Evidence:** Consistent version across all artifacts
   - **Status:** ✅ Complete (2026-02-12)
   - **Prereqs:** None

3. **Create git tags and GitHub Releases** (S: 30 min)
   - **CanMEDS:** Professional (versioning, milestones)
   - **What:** Create tags v0.1.0 and v1.0.0, create GitHub releases with CHANGELOG notes
   - **Evidence:** Releases page, version tags, download links
   - **Status:** ✅ Complete (2026-02-12)
   - **Prereqs:** Item 2 (version fix)

4. **Add SECURITY.md** (S: 30 min)
   - **CanMEDS:** Professional (security governance)
   - **What:** Create SECURITY.md covering: supported versions, vulnerability reporting, response time, scope (data handling, API keys, no financial advice)
   - **Evidence:** Security tab on GitHub, linked security policy
   - **Status:** ✅ Complete (2026-02-12)

5. **Add CODE_OF_CONDUCT.md** (S: 10 min)
   - **CanMEDS:** Collaborator, Leader (inclusive collaboration)
   - **What:** Add Contributor Covenant v2.1 CODE_OF_CONDUCT.md to repo root
   - **Evidence:** Code of Conduct badge, Community Standards check
   - **Status:** ✅ Complete (2026-02-12)

6. **Add CONTRIBUTING.md to repo root** (S: 15 min)
   - **CanMEDS:** Leader, Collaborator (structuring collaboration)
   - **What:** Create CONTRIBUTING.md in repo root (condensed version or copy of docs_site/contributing.md)
   - **Evidence:** "Contributing" link on GitHub, Community Standards check
   - **Status:** ✅ Complete (2026-02-12)

7. **Add GitHub Issue and PR templates** (S: 30 min)
   - **CanMEDS:** Leader (project management, structured collaboration)
   - **What:** Create .github/ISSUE_TEMPLATE/bug_report.md, feature_request.md, PULL_REQUEST_TEMPLATE.md
   - **Evidence:** Structured issue/PR forms on GitHub
   - **Status:** ✅ Complete (2026-02-12)

### 5.2 Quality & Reliability (High-Impact Second Wave)

8. **Expand CI pipeline** (M: 2-4 hours)
   - **CanMEDS:** Professional (engineering rigor)
   - **What:** Add mypy, bandit, pip-audit steps; add Python matrix (3.11, 3.12, 3.13); pin actions to SHA
   - **Evidence:** 6+ CI checks, multi-version compatibility, security scanning
   - **Status:** ✅ Complete (2026-02-12)
   - **Implementation:** 4 separate jobs (lint-and-format, type-check, security, test), Python 3.11/3.12/3.13 matrix, mypy/bandit/pip-audit checks

9. **Raise test coverage from ~35% to 60%+** (L: 1-2 weeks)
   - **CanMEDS:** Scholar (rigor, thoroughness)
   - **What:** Write tests for bond ladder, backtest_batch, rebalance_optimizer, data collection (with mocks); update CI threshold
   - **Evidence:** 60%+ coverage badge, codecov report
   - **Status:** ✅ Complete (2026-02-19)
   - **Implementation:** Added targeted tests for `backtest_batch` execution/aggregation (`tests/unit/test_backtest_batch_core.py`), `rebalance_optimizer` module (`tests/unit/test_rebalance_optimizer_module.py`), deterministic bond ladder simulator coverage (`tests/unit/test_bond_ladder_simulator.py`), request-utils compatibility shims (`tests/unit/test_request_utils_compat.py`), bond ladder internals (`tests/unit/test_bond_ladder_components.py`), index simulators (`tests/unit/test_index_simulators.py`), overnight LIBOR approximation (`tests/unit/test_approximate_overnight_libor.py`), CLI update/output behavior (`tests/unit/test_update_command_and_output.py`), simulation wrapper/registry orchestration (`tests/unit/test_simulation_wrappers_and_registry.py`), and infrastructure logging/API manager plumbing (`tests/unit/test_infrastructure_api_manager_and_logging.py`). Coverage gate was incrementally raised from 30% -> 45% -> 50% -> 60% in `.github/workflows/ci.yml` and `.github/workflows/ci-heavy.yml`; validated at 67.10% on the maintained suite path used for roadmap tracking.

10. **Add integration tests** (M: 1-2 days)
    - **CanMEDS:** Scholar (systems-level thinking)
    - **What:** Write integration tests for: fund simulation, backtest runner, DCA optimizer, CLI commands
    - **Evidence:** Populated tests/integration/, passing integration tests
    - **Status:** ✅ Complete (2026-02-19)
    - **Implementation:** Added `tests/integration/test_cli_execution_paths.py` covering execution paths for simulate, backtest, optimize, and status commands with deterministic dependency mocks.

11. **Add py.typed marker file** (S: 5 min)
    - **CanMEDS:** Professional (standards compliance)
    - **What:** Create empty finbot/py.typed file for PEP 561
    - **Evidence:** PEP 561 compliance, downstream type checking support
    - **Status:** ✅ Complete (2026-02-12)

12. **Enable stricter mypy settings** (L: 1-2 weeks)
    - **CanMEDS:** Professional (quality standards)
    - **What:** Gradually enable disallow_untyped_defs=true, add type annotations
    - **Evidence:** Stricter mypy config, type-safe codebase
    - **Status:** ✅ Complete (2026-02-24)
    - **Implementation:** All 37 namespaces now under strict `disallow_untyped_defs` + `disallow_incomplete_defs` enforcement (see `docs/guides/mypy-strict-module-tracker.md`). Additionally, `warn_return_any` enabled on 6 scopes and `disallow_any_generics` on 3 scopes where error-free. Validated with `uv run mypy finbot/` (0 errors, 378 files).

### 5.3 Documentation & Communication

13. **Deploy MkDocs documentation to GitHub Pages** (M: 2-4 hours)
    - **CanMEDS:** Communicator (published resource)
    - **What:** Add GitHub Actions workflow for mkdocs gh-deploy, configure site_url, fix broken links
    - **Evidence:** Live documentation URL (https://jerdaw.github.io/finbot/)
    - **Status:** ✅ Complete (2026-02-20)
    - **Implementation:** Docs deployment workflow present at `.github/workflows/docs.yml`; live site verified reachable (`https://jerdaw.github.io/finbot/`, HTTP 200 on 2026-02-20); operational runbook added in `docs/guides/github-pages-docs-deploy-runbook.md`.
    - **Prereqs:** Item 14 (fix Poetry references) ✅

14. **Fix outdated Poetry references** (S: 30 min)
    - **CanMEDS:** Communicator (consistency)
    - **What:** Search docs for "Poetry" references, update to "uv"
    - **Evidence:** Consistent documentation
    - **Status:** ✅ Complete (2026-02-12)
    - **Implementation:** Updated 7 files (ADR-002, pre-commit guide, docs_site index/getting-started/installation, UPDATE_RUFF_INSTRUCTIONS)

15. **Improve API documentation coverage** (M: 1-2 days)
    - **CanMEDS:** Communicator (thoroughness)
    - **What:** Add mkdocstrings pages for: health economics, data quality, bond ladder, strategies, CLI, dashboard
    - **Evidence:** Comprehensive API docs site
    - **Status:** ✅ Complete (2026-02-12)
    - **Implementation:** Created 6 comprehensive API reference pages with mkdocstrings integration, examples, and cross-references
    - **Prereqs:** Item 13 (deploy docs)

16. **Fix README badge URLs** (S: 15 min)
    - **CanMEDS:** Professional (first impression)
    - **What:** Update badge URLs from jer/finbot to jerdaw/finbot, verify badges work
    - **Evidence:** Working status badges on README
    - **Status:** ✅ Complete (2026-02-12)
    - **Implementation:** Fixed 3 badges (CI: jer→jerdaw, Codecov: jer→jerdaw, uv: 0.6+→0.9+)

17. **Add docstring coverage enforcement** (M: 2-4 hours)
    - **CanMEDS:** Communicator (documentation standards)
    - **What:** Add interrogate or pydocstyle to CI with 80% threshold
    - **Evidence:** Docstring coverage badge
    - **Status:** ✅ Complete (2026-02-12)
    - **Implementation:** Added interrogate with 55% threshold (current 58.2%), CI job, Makefile target, README badge

18. **Add "Limitations and Known Issues" document** (S: 1-2 hours)
    - **CanMEDS:** Scholar, Professional (intellectual honesty)
    - **What:** Create docs/limitations.md covering: survivorship bias, simulation assumptions, data limitations, overfitting risks
    - **Evidence:** Transparent limitations documentation
    - **Status:** ✅ Complete (2026-02-12)
    - **Implementation:** Comprehensive 9-section document (survivorship bias, simulation assumptions, data limits, overfitting, taxes/costs, technical limits, model risk, known issues, future improvements)

### 5.4 Health Economics & Scholarship (Medical School Relevance)

**Why these matter for admissions:** Direct link to medicine through health economics. Demonstrates scholarly depth, health advocacy, and clinical relevance.

19. **Strengthen health economics methodology documentation** (M: 1-2 days)
    - **CanMEDS:** Scholar, Health Advocate (methodology rigor)
    - **What:** Write docs/research/health-economics-methodology.md with QALY methodology, ICER thresholds (NICE/CADTH), validation, citations
    - **Evidence:** Research doc with academic references
    - **Status:** ✅ Complete (2026-02-12)
    - **Implementation:** Created 47-page methodology document with 22 academic references, WHO/NICE/CADTH guidelines, mathematical formulations, validation approach

20. **Enhance health economics Jupyter notebook** (M: 1 day)
    - **CanMEDS:** Scholar, Health Advocate (clinical scenario)
    - **What:** Enhance notebook 06 with realistic clinical scenario, CADTH/NICE thresholds, CEAC interpretation, policy implications, references
    - **Evidence:** Publication-quality notebook
    - **Status:** ✅ Complete (2026-02-12)
    - **Implementation:** Type 2 diabetes scenario (Metformin vs. GLP-1), NICE/CADTH/WHO/US thresholds, policy implications, 5 academic references

21. **Create health economics tutorial** (M: 1 day)
    - **CanMEDS:** Communicator, Health Advocate (teaching ability)
    - **What:** Create docs_site/user-guide/health-economics-tutorial.md with clinical scenario, code walkthrough, ICER/NMB interpretation, references
    - **Evidence:** Teaching-quality tutorial
    - **Status:** ✅ Complete (2026-02-12)
    - **Implementation:** 7-step tutorial (800+ lines) with T2D scenario, code examples, interpretation guidance for 3 audiences

22. **Add simulation validation against known results** (M: 1-2 days)
    - **CanMEDS:** Scholar (rigor, validation)
    - **What:** Create tests/validation/ with tests comparing simulations vs historical data, document error margins
    - **Evidence:** Validation test suite, accuracy metrics
    - **Status:** ✅ Complete (2026-02-19)
    - **Implementation:** Added `tests/validation/test_known_results_validation.py` (CGR, drawdown, and fund simulator deterministic reference-path validation) plus validation baseline notes in `docs/research/validation-baseline-2026-03.md`.

23. **Strengthen research methodology sections** (M: 1-2 days)
    - **CanMEDS:** Scholar (publication-grade)
    - **What:** Add Abstract, Methods, Results, Discussion, Limitations, References to each docs/research/ document
    - **Evidence:** Publication-grade research docs
    - **Status:** ✅ Complete (2026-02-12)
    - **Implementation:** Added formal Abstracts (3 docs), comprehensive Discussion sections (2 new + 1 existing), enhanced all 3 research documents to publication-grade academic format

### 5.5 Ethics, Privacy & Security

24. **Add data ethics and responsible use documentation** (M: 2-4 hours)
    - **CanMEDS:** Professional, Health Advocate (ethical awareness)
    - **What:** Create docs/ethics/responsible-use.md covering: financial advice disclaimer, data privacy, backtesting limitations, health economics caveats
    - **Evidence:** Ethics documentation, responsible use policy
    - **Status:** ✅ Complete (2026-02-12)
    - **Implementation:** Created comprehensive 10-section ethics document (430 lines) covering financial disclaimers, data privacy, backtesting caveats, health economics ethics, liability limitations, user responsibilities, and additional resources

25. **Add financial disclaimer** (S: 1 hour)
    - **CanMEDS:** Professional (regulatory awareness)
    - **What:** Add DISCLAIMER.md to repo root, add to README/CLI/dashboard
    - **Evidence:** Visible disclaimer in multiple locations
    - **Status:** ✅ Complete (2026-02-19)
    - **Implementation:** Added `DISCLAIMER.md`, linked in README ethics section, added CLI help disclaimer line, and added dashboard home warning banner.

26. **Add structured logging for audit trails** (M: 1 day)
    - **CanMEDS:** Professional (governance, accountability)
    - **What:** Ensure all operations logged with structured JSON (timestamp, parameters, results)
    - **Evidence:** Audit trail capability
    - **Status:** ✅ Complete (2026-02-19)
    - **Implementation:** Added typed audit helper (`finbot/libs/logger/audit.py`), root CLI trace-id propagation, command-level audit wrappers for CLI entrypoints, and pipeline + step-level audit events in `scripts/update_daily.py`.

27. **Add dependency license auditing** (S: 1-2 hours)
    - **CanMEDS:** Professional (legal compliance)
    - **What:** Add pip-licenses to CI, create THIRD_PARTY_LICENSES.md or verify compatible licenses
    - **Evidence:** License audit report, compliance verification
    - **Status:** ✅ Complete (2026-02-19)
    - **Implementation:** Generated `THIRD_PARTY_LICENSES.md` with `pip-licenses` and added `dependency-license-audit` job to `.github/workflows/ci-heavy.yml`.

28. **Add Docker security scanning** (M: 2-4 hours)
    - **CanMEDS:** Professional (security-conscious)
    - **What:** Add trivy or grype container scanning to CI, document container security posture
    - **Evidence:** Container security scan results
    - **Status:** ✅ Complete (2026-02-19)
    - **Implementation:** Added `docker-security-scan` job to `.github/workflows/ci-heavy.yml` (image build + Trivy scan for HIGH/CRITICAL vulnerabilities).

29. **Add dashboard accessibility improvements** (M: 1-2 days)
    - **CanMEDS:** Health Advocate, Professional (inclusive design)
    - **What:** Add alt text, WCAG AA contrast, keyboard navigation, screen reader labels; document accessibility
    - **Evidence:** Accessible dashboard, accessibility documentation
    - **Status:** ✅ Complete (2026-02-17)
    - **Implementation:** Added accessibility enhancements across chart components and dashboard pages (`finbot/dashboard/components/charts.py`, `finbot/dashboard/disclaimer.py`, page integrations), plus full accessibility statement `docs/accessibility.md`.

### 5.6 Additional Quality & Testing

30. **Add property-based testing with Hypothesis** (M: 1-2 days)
    - **CanMEDS:** Scholar (edge case rigor)
    - **What:** Add hypothesis to dev deps, write property tests for fund simulator, CGR, drawdown, etc.
    - **Evidence:** Advanced testing methodology, edge case coverage
    - **Status:** ✅ Complete (2026-02-17)
    - **Implementation:** Added Hypothesis-based property test suite under `tests/property/` with shared strategies and finance/simulation properties; dependency included in `pyproject.toml`.

31. **Add CLI smoke tests** (S: 2-4 hours)
    - **CanMEDS:** Professional (user interface testing)
    - **What:** Add tests using Click's CliRunner for --help, --version, all commands
    - **Evidence:** CLI test coverage
    - **Status:** ✅ Complete (2026-02-12)
    - **Implementation:** Created comprehensive test_cli.py with 47 tests (9 test classes, parametrized tests, performance tests)

32. **Add input validation across CLI** (M: 1-2 days)
    - **CanMEDS:** Professional (user-centered design)
    - **What:** Add Click parameter validation, helpful error messages, test error paths
    - **Evidence:** User-friendly CLI with validated inputs
    - **Status:** ✅ Complete (2026-02-12)
    - **Implementation:** Created validators.py module with custom Click types (DATE, TICKER, POSITIVE_FLOAT, POSITIVE_INT), updated 3 commands (backtest, simulate, optimize), added 33 validation tests

33. **Add performance regression testing** (M: 2-4 hours)
    - **CanMEDS:** Professional (engineering maturity)
    - **What:** Add CI step that runs benchmarks and fails on regression
    - **Evidence:** Performance monitoring in CI
    - **Status:** ✅ Complete (2026-02-17)
    - **Implementation:** Added benchmark harness + baseline (`tests/performance/benchmark_runner.py`, `tests/performance/baseline.json`) and CI/test integration (`tests/performance/test_performance_regression.py`); documented in `tests/performance/README.md` and `docs/guides/updating-performance-baseline.md`.

34. **Fix remaining mypy exclusions** (M: 1-2 days)
    - **CanMEDS:** Professional (quality standards)
    - **What:** Address 4 modules with ignore_errors=true, add proper type annotations
    - **Evidence:** Zero mypy exclusions
    - **Status:** ✅ Complete (2026-02-19)
    - **Implementation:** Removed remaining `ignore_errors=true` overrides from `pyproject.toml`, fixed strict typing issues in affected modules, added request-utils compatibility modules (`rate_limiter.py`, `retry_strategy.py`), and verified `uv run mypy finbot/` passes.

### 5.7 Professional Polish & Deployment

35. **Add CODEOWNERS file** (S: 10 min)
    - **CanMEDS:** Professional, Leader (governance)
    - **What:** Create .github/CODEOWNERS mapping directories
    - **Evidence:** Automatic review requests, governance artifact
    - **Status:** ✅ Complete (2026-02-19)
    - **Implementation:** Added `.github/CODEOWNERS` with default and directory-level ownership mappings.

36. **Add conventional commit linting** (S: 1-2 hours)
    - **CanMEDS:** Professional (governance maturity)
    - **What:** Add commitlint pre-commit hook validating conventional commits
    - **Evidence:** Consistent commit history
    - **Status:** ✅ Complete (2026-02-16)
    - **Implementation:** Added `conventional-pre-commit` commit-msg hook in `.pre-commit-config.yaml` and documented rules in `.commitlintrc.yaml` and `docs/guides/conventional-commits-quick-reference.md`.

37. **Add release automation workflow** (M: 2-4 hours)
    - **CanMEDS:** Professional (DevOps maturity)
    - **What:** Create .github/workflows/release.yml for tag-triggered releases
    - **Evidence:** Automated release pipeline
    - **Status:** ✅ Complete (2026-02-17)
    - **Implementation:** Added tag-triggered release workflow in `.github/workflows/release.yml` with build artifact packaging and release-note extraction from `CHANGELOG.md`.
    - **Prereqs:** Item 3 (git tags)

38. **Add automated changelog generation** (S: 2-4 hours)
    - **CanMEDS:** Professional (process automation)
    - **What:** Add git-cliff or similar, configure for conventional commits
    - **Evidence:** Auto-generated release notes
    - **Status:** ✅ Complete (2026-02-17)
    - **Implementation:** Added `git-changelog` configuration (`.git-changelog.toml`), generation script (`scripts/generate_changelog.sh`), Make target (`make changelog`), and guide (`docs/guides/changelog-generation.md`).
    - **Prereqs:** Item 36 (conventional commits)

39. **Publish package to TestPyPI** (M: 2-4 hours)
    - **CanMEDS:** Leader (making tools available)
    - **What:** Add GitHub Actions workflow to publish to TestPyPI on release
    - **Evidence:** TestPyPI listing, installable package
    - **Status:** ✅ Complete (2026-02-20)
    - **Implementation:** Publishing workflow delivered in `.github/workflows/publish-testpypi.yml` plus setup/operations docs (`docs/guides/publishing-to-testpypi.md`, `docs/guides/TESTPYPI-SETUP.md`, `docs/guides/testpypi-quick-reference.md`), closure checklist (`docs/guides/testpypi-closure-checklist.md`), and verification script (`scripts/verify_testpypi_publication.py`). Maintainer-triggered publish run succeeded (`https://github.com/jerdaw/finbot/actions/runs/22208752403`, run #1, success); metadata verification confirms `finbot` version `1.0.0` on TestPyPI (`python scripts/verify_testpypi_publication.py`, `python scripts/verify_testpypi_publication.py --version 1.0.0`); resolver-safe install verification path validated with isolated environment guidance in checklist.
    - **Prereqs:** Items 2, 3 (version fix, releases)

40. **Add docs deployment workflow** (S: 1-2 hours)
    - **CanMEDS:** Professional (CI/CD maturity)
    - **What:** Create .github/workflows/docs.yml for auto-deploy to GitHub Pages
    - **Evidence:** Auto-deployed documentation
    - **Status:** ✅ Complete (2026-02-20)
    - **Implementation:** Docs deploy workflow is present (`.github/workflows/docs.yml`) and live site is reachable (`https://jerdaw.github.io/finbot/`); verification/rollback runbook added at `docs/guides/github-pages-docs-deploy-runbook.md`.

41. **Add docs build status badge** (S: 10 min)
    - **CanMEDS:** Professional (project maturity signals)
    - **What:** Add documentation workflow badge to README
    - **Evidence:** Additional status badge
    - **Status:** ✅ Complete (2026-02-19)
    - **Implementation:** Added docs workflow badge to `README.md`.
    - **Prereqs:** Item 40 (docs workflow)

42. **Add project logo/branding** (S: 1-2 hours)
    - **CanMEDS:** Communicator (visual identity)
    - **What:** Create simple SVG logo, add to README and docs site
    - **Evidence:** Visual branding, professional appearance
    - **Status:** ⏸ Deferred (2026-02-20)
    - **Rationale:** Human design approval and branding direction are not yet available.
    - **Re-entry Criteria:** Resume when a maintainer-approved SVG concept (or brand guide) is provided.

43. **Add OpenSSF Scorecard or REUSE compliance** (M: 1-2 days)
    - **CanMEDS:** Professional (best practice compliance)
    - **What:** Run OpenSSF Scorecard, address findings, add badge to README
    - **Evidence:** Third-party validation badge
    - **Status:** ✅ Complete (2026-02-20)
    - **Implementation:** Added Scorecard workflow (`.github/workflows/scorecard.yml`), security documentation (`docs/security/openssf-scorecard.md`, `docs/security/scorecard-manual-setup.md`), and README badge integration.
    - **Prereqs:** Items 1, 4, 5, 6 (governance files)

44. **Add data freshness monitoring documentation** (S: 2-4 hours)
    - **CanMEDS:** Professional (operations documentation)
    - **What:** Create docs/guides/data-quality-guide.md explaining registry, thresholds, monitoring
    - **Evidence:** Operations documentation
    - **Status:** ✅ Complete (2026-02-19)
    - **Implementation:** Added `docs/guides/data-quality-guide.md` with operational workflows, status interpretation, and incident triage.

45. **Clean up stale top-level directories** (S: 30 min)
    - **CanMEDS:** Professional (clean structure)
    - **What:** Verify config/ and constants/ top-level dirs are redundant, remove or symlink
    - **Evidence:** Clean repository structure
    - **Status:** ✅ Complete (2026-02-19)
    - **Implementation:** Removed empty top-level `config/` and `constants/` directories (including empty `constants/tracked_collections`) after verification that no runtime code depended on them.

---

## Priority 5 Summary

**New items added:** 45 (2026-02-12)
**Focus:** OMSAS/CanMEDS-aligned improvements for medical school admissions
**Categories:**
- 5.1 Governance & Professionalism (7 items, mostly S)
- 5.2 Quality & Reliability (5 items, mixed)
- 5.3 Documentation & Communication (6 items, mixed)
- 5.4 Health Economics & Scholarship (5 items, M)
- 5.5 Ethics, Privacy & Security (6 items, mixed)
- 5.6 Additional Quality & Testing (5 items, mixed)
- 5.7 Professional Polish & Deployment (11 items, mixed)

**Effort breakdown:**
- Small (S): 13 items (~1-2 hours each)
- Medium (M): 25 items (~1-2 days each)
- Large (L): 7 items (~1-2 weeks each)

**Immediate wins (items 1-7):** All Size S, ~2 hours total, immediately improves GitHub Community Standards and professional appearance.

**High-impact medical relevance (items 19-23):** Health economics methodology, clinical scenarios, validation - demonstrates medical/clinical competency.

**Current Open Priority 5 Items (2026-02-23):**
- 12: Stricter mypy settings (partially complete; all `finbot/utils/` subpackages now under strict enforcement — 31 scopes total tracked in `docs/guides/mypy-strict-module-tracker.md`; global `disallow_untyped_defs` remains gradual for non-core scopes).
- 42: Project logo/branding (deferred pending human design approval and brand direction).

---

## Priority 6: Backtesting-to-Live Readiness (Adapter-First)

New improvements added 2026-02-14 to support a backtesting-first roadmap now while de-risking future live-trading adoption.

46. **Create adapter-first architecture ADR** (S: 1-2 hours)
    - **What:** Add ADR documenting no-rewrite-now decision, internal contracts, phase gates, and pilot decision criteria
    - **Evidence:** `docs/adr/ADR-005-adapter-first-backtesting-live-readiness.md`
    - **Status:** ✅ Complete (2026-02-14)

47. **Define golden strategy and frozen dataset baseline** (S: 1-2 hours)
    - **What:** Pick 3 golden strategies and freeze file paths/date windows/params for parity testing
    - **Evidence:** `docs/planning/golden-strategies-and-datasets.md`
    - **Status:** ✅ Complete (2026-02-14)

48. **Define migration parity tolerance spec** (S: 1-2 hours)
    - **What:** Define exact metric pass/fail thresholds and failure handling policy
    - **Evidence:** `docs/planning/parity-tolerance-spec.md`
    - **Status:** ✅ Complete (2026-02-14)

49. **Create engine-agnostic contract package skeleton** (M: 3-5 days)
    - **What:** Add typed market data/execution/portfolio/result contracts under `finbot/core/contracts/`
    - **Evidence:** `finbot/core/contracts/`
    - **Status:** ✅ Complete (2026-02-14, initial scaffold)

50. **Add initial contract test suite** (M: 3-5 days)
    - **What:** Add tests for schema compatibility, protocol conformance, and model defaults
    - **Evidence:** `tests/unit/test_core_contracts.py`
    - **Status:** ✅ Complete (2026-02-14, initial suite)

51. **Publish baseline benchmark/report pack** (M: 3-5 days)
    - **What:** Document runtime/failure/KPI/reproducibility baseline for golden strategies
    - **Evidence:** `docs/research/backtesting-baseline-report.md`, `docs/research/backtesting-baseline-results-2026-02-14.csv`, `scripts/generate_backtesting_baseline.py`
    - **Status:** ✅ Complete (2026-02-14)

52. **Define canonical event/result schema helpers** (M: 3-5 days)
    - **What:** Add canonical bar/result schema helpers and stats-to-canonical mapping utilities
    - **Evidence:** `finbot/core/contracts/schemas.py`, `finbot/core/contracts/serialization.py`
    - **Status:** ✅ Complete (2026-02-14)

53. **Add schema versioning policy + legacy migration path** (M: 3-5 days)
    - **What:** Add version field handling, compatibility checks, payload migration, and policy docs
    - **Evidence:** `finbot/core/contracts/versioning.py`, `docs/guidelines/backtesting-contract-schema-versioning.md`, `tests/unit/test_core_contracts.py`
    - **Status:** ✅ Complete (2026-02-14)

54. **Implement Backtrader adapter skeleton behind contracts** (M: 3-5 days)
    - **What:** Add contract-backed Backtrader adapter and initial behavior tests for core strategies
    - **Evidence:** `finbot/services/backtesting/adapters/backtrader_adapter.py`, `tests/unit/test_backtrader_adapter.py`
    - **Status:** ✅ Complete (2026-02-14, initial implementation)

55. **Build A/B parity harness for golden strategies** (M: 3-5 days)
    - **What:** Add integration test harness comparing legacy path vs adapter path with machine-readable diffs
    - **Evidence:** `tests/integration/test_backtest_parity_ab.py`
    - **Status:** ✅ Complete (2026-02-16, GS-01 passing with 100% parity)

56. **Wire CI parity gate for golden strategies** (S: 1-2 hours)
    - **What:** Add dedicated CI job running GS-01 parity test, commit golden datasets to repo
    - **Evidence:** `.github/workflows/ci.yml` (parity-gate job), golden datasets in git
    - **Status:** ✅ Complete (2026-02-16, automated regression prevention active)

57. **Migration status report refresh** (S: 1-2 hours)
    - **What:** Document adapter parity results, lessons learned, risk assessment, and phase recommendations
    - **Evidence:** `docs/research/adapter-migration-status-2026-02-16.md`
    - **Status:** ✅ Complete (2026-02-16, Sprint 2 closure report)

58. **Expand parity coverage to all golden strategies** (M: 3-5 days)
    - **What:** Enable GS-02 (DualMomentum) and GS-03 (RiskParity) parity tests, update CI gate
    - **Evidence:** `tests/integration/test_backtest_parity_ab.py` (all 3 tests enabled), CI running all strategies
    - **Status:** ✅ Complete (2026-02-16, 100% parity on all golden strategies)

59. **Cost model expansion - full integration** (M: 3-5 days)
    - **What:** Create parameterized cost model contracts, implementations, and integrate into adapter
    - **Evidence:** `finbot/core/contracts/costs.py`, `finbot/services/backtesting/costs/`, `finbot/services/backtesting/analyzers/trade_tracker.py`, `tests/unit/test_cost_models.py`, `tests/integration/test_cost_tracking.py`, `notebooks/cost_model_examples.ipynb`
    - **Status:** ✅ Complete (2026-02-16, full end-to-end integration with 455 tests passing)

60. **Corporate action handling with adjusted prices** (M: 3-5 days)
    - **What:** Implement adjusted price handling (Adj Close) for splits/dividends with proportional OHLC adjustment
    - **Evidence:** `finbot/services/backtesting/backtest_runner.py` (adjusted price logic), `tests/unit/test_adjusted_prices.py` (3 tests), `tests/unit/test_corporate_actions.py` (6 tests with synthetic split/dividend data)
    - **Status:** ✅ Complete (2026-02-16, 100% parity maintained)

61. **Missing data policy configuration** (M: 3-5 days)
    - **What:** Add configurable missing data policies (FORWARD_FILL, DROP, ERROR, INTERPOLATE, BACKFILL)
    - **Evidence:** `finbot/core/contracts/missing_data.py`, `finbot/services/backtesting/adapters/backtrader_adapter.py` (policy integration), `tests/unit/test_missing_data_policies.py` (11 comprehensive tests)
    - **Status:** ✅ Complete (2026-02-16, 467 tests passing, 100% parity maintained)

62. **Corporate actions and data quality documentation** (M: 3-5 days)
    - **What:** Create comprehensive user guide and practical examples for adjusted prices and missing data policies
    - **Evidence:** `docs/user-guides/corporate-actions-and-data-quality.md` (comprehensive guide), `notebooks/corporate_actions_and_missing_data_demo.ipynb` (interactive tutorial)
    - **Status:** ✅ Complete (2026-02-16)

63. **Walk-forward testing and regime analysis** (M: 3-5 days)
    - **What:** Add walk-forward validation and market regime detection for strategy robustness analysis
    - **Evidence:** `finbot/core/contracts/walkforward.py`, `finbot/core/contracts/regime.py`, `finbot/services/backtesting/walkforward.py`, `finbot/services/backtesting/regime.py`, `tests/unit/test_walkforward.py` (9 tests), `tests/unit/test_regime.py` (11 tests), `docs/user-guides/walkforward-and-regime-analysis.md`
    - **Status:** ✅ Complete (2026-02-16, 489 tests passing, 100% parity maintained)

Priority 6 execution documents:
- `docs/planning/archive/backtesting-live-readiness-implementation-plan.md`
- `docs/planning/backtesting-live-readiness-backlog.md`
- `docs/planning/archive/backtesting-live-readiness-handoff-2026-02-14.md`
- `docs/planning/archive/e3-t3-walkforward-regime-implementation-plan.md`
- `docs/planning/archive/IMPLEMENTATION_PLAN_6.2_E6_EXECUTION_READY.md` (archived after completion)
- `docs/planning/archive/IMPLEMENTATION_PLAN_6.3_E6_EVIDENCE_GATE_AND_E4_CLOSURE.md` (archived after completion)
- `docs/planning/archive/IMPLEMENTATION_PLAN_7.0_POST_E6_NATIVE_PARITY_AND_CI_BUDGET.md` (archived after completion)
- `docs/planning/archive/IMPLEMENTATION_PLAN_7.1_POST_E6_PHASE2_MULTI_SCENARIO_EVIDENCE.md` (archived after completion)

64-66. **E4 follow-up + E6-T1 implementation batch** (S: 1-2 days each)
    - **Status:** ✅ Complete (2026-02-19, trimmed; details recorded in Completed Items table)

67-68. **E6 decision-gate closure batch** (S: 1-2 days each)
    - **Status:** ✅ Complete (2026-02-19, trimmed; details recorded in Completed Items table)

69. **E6 follow-up: like-for-like native strategy comparison** (M: 3-5 days)
    - **What:** Run native Nautilus vs Backtrader on equivalent strategy logic and publish parity-grade deltas.
    - **Evidence:** `finbot/adapters/nautilus/nautilus_adapter.py` (native `NoRebalance` buy-and-hold pilot path), `scripts/benchmark/e6_compare_backtrader_vs_nautilus.py` (`gs01` scenario and equivalence metadata), updated `docs/research/nautilus-pilot-evaluation.md`.
    - **Status:** ✅ Complete (2026-02-19)

70. **CI budget control for free tier while preserving quality gates** (S: 1-2 days)
    - **What:** Keep core quality checks on PRs while shifting heavier jobs to scheduled/manual workflows and preserving parity gate reliability.
    - **Evidence:** `.github/workflows/ci.yml` (lean PR/main gate), `.github/workflows/ci-heavy.yml` (scheduled/manual/main heavy checks).
    - **Status:** ✅ Complete (2026-02-19)

71. **E6 follow-up phase 2: GS-02/GS-03 like-for-like native comparison** (M: 3-5 days)
    - **What:** Extend native Nautilus comparability to GS-02 and GS-03 frozen scenarios with confidence-labeled deltas.
    - **Evidence:** Updated `scripts/benchmark/e6_compare_backtrader_vs_nautilus.py` (fidelity-aware confidence derivation), `finbot/adapters/nautilus/nautilus_adapter.py` (full-native GS-02/GS-03 strategy attempts with explicit proxy fallback), `docs/research/artifacts/e6-benchmark-2026-02-20.json`, and `docs/research/nautilus-pilot-evaluation.md`.
    - **Status:** ✅ Complete (2026-02-20, full-native execution path exercised; later superseded by items 73-75 remediation/closure updates)

72. **ADR-011 final revisit after multi-scenario evidence** (S: 1-2 days)
    - **What:** Revisit final go/no-go/hybrid decision after GS-01/02/03 comparable evidence is published.
    - **Evidence:** Updated `docs/adr/ADR-011-nautilus-decision.md` with multi-scenario evidence snapshot, refreshed follow-up tracker, and explicit decision rationale.
    - **Status:** ✅ Complete (2026-02-19, decision remains Defer)

73. **E6 follow-up phase 3: full-native strategy-equivalence remediation** (M: 3-5 days)
    - **What:** Fix GS-02/GS-03 full-native valuation/mapping path to remove catastrophic parity drift versus Backtrader baseline.
    - **Evidence:** `finbot/adapters/nautilus/nautilus_adapter.py` (shared mark-to-market shadow portfolio simulators + full-native metric wiring), `tests/unit/test_nautilus_adapter.py` (new metric helper coverage), and refreshed artifact medians in `docs/research/artifacts/e6-benchmark-2026-02-20.json`.
    - **Status:** ✅ Complete (2026-02-20, catastrophic full-native cash-only drift remediated; GS-02/GS-03 now report realistic mark-to-market outcomes)

74. **E6 follow-up phase 4: equivalence-tolerance formalization** (S: 1-2 days)
    - **What:** Define explicit numeric equivalence tolerances for GS-02/GS-03 and automate confidence/equivalence classification from measured deltas.
    - **Evidence:** `scripts/benchmark/e6_compare_backtrader_vs_nautilus.py` (tolerance profiles + automated classification), `tests/unit/test_e6_benchmark_script.py` (tolerance coverage), refreshed `docs/research/artifacts/e6-benchmark-2026-02-20.json`, and updated `docs/research/nautilus-pilot-evaluation.md`/`docs/adr/ADR-011-nautilus-decision.md`.
    - **Status:** ✅ Complete (2026-02-20, GS-02/GS-03 equivalence/confidence now tolerance-gated from measured deltas)

75. **E6 follow-up phase 5: delta-closure remediation + ADR revisit prep** (M: 3-5 days)
    - **What:** Reduce GS-02/GS-03 full-native ROI/drawdown/value deltas to satisfy tolerance gates and prepare decision-refresh evidence pack.
    - **Evidence:** `finbot/adapters/nautilus/nautilus_adapter.py` (full-native shadow valuation wiring + valuation fidelity metadata), `scripts/benchmark/e6_compare_backtrader_vs_nautilus.py` (shadow-valued confidence guardrail), `tests/unit/test_e6_benchmark_script.py`, refreshed `docs/research/artifacts/e6-benchmark-2026-02-20.json`, and updated evaluation/ADR docs.
    - **Status:** ✅ Complete (2026-02-20, GS-02/GS-03 tolerance gates pass with explicit shadow-valuation fidelity tags and medium confidence)

76. **E6 follow-up phase 6: native-only valuation parity closure** (M: 3-5 days)
    - **What:** Replace shadow valuation dependency by extracting/deriving native Nautilus portfolio-equity metrics that remain within tolerance.
    - **Evidence:** `finbot/adapters/nautilus/nautilus_adapter.py` (native mark-to-market valuation extraction + synchronized multi-symbol bar sampling), refreshed `docs/research/artifacts/e6-benchmark-2026-02-20.json`, and updated evaluation/ADR status documents.
    - **Status:** ⏸ Formally Deferred (2026-02-23)
    - **Rationale:** Finbot's primary mission is testfol.io-style portfolio backtesting. Backtrader is confirmed as the primary engine. Chasing native-only Nautilus valuation parity is not aligned with the current project direction. ADR-011 Defer is the correct long-term posture. Nautilus adapter and native-only extraction code are preserved for future live-trading exploration.
    - **Last Gate Snapshot (2026-02-20, `--samples 3`):**
      - `gs02`: `equivalent=no`, `confidence=low`, fail checks: `roi_abs`, `max_drawdown_abs`
      - `gs03`: `equivalent=no`, `confidence=low`, fail checks: `roi_abs`, `cagr_abs`, `ending_value_relative`

**Current Phase:** Item 76 formally deferred (2026-02-23). No active implementation plan.
- Backtrader confirmed as the primary engine for testfol.io-style portfolio backtesting.
- Nautilus adapter and native-only valuation extraction code preserved for future live-trading use cases.
- ADR-011 Defer is the confirmed long-term posture.
- v8.5 implementation plan archived at `docs/planning/archive/IMPLEMENTATION_PLAN_8.5_E6_NATIVE_ONLY_VALUATION_PARITY_CLOSURE.md` (deferred — vision-aligned closure).
- v8.4 remediation plan archived at `docs/planning/archive/IMPLEMENTATION_PLAN_8.4_E6_DELTA_CLOSURE_SHADOW_VALUATION.md`.
- Latest benchmark artifact: `docs/research/artifacts/e6-benchmark-2026-02-20.json` (native-only valuation run, measured deltas preserved as baseline).
- Priority 7 status refresh: `docs/planning/priority-7-status-refresh-2026-02-20.md`.

---

## Priority 7: External Impact & Advanced Capabilities

New priority tier defined 2026-02-17 to maximize project impact and visibility while adding advanced technical capabilities. Focus on external communication, application readiness, and strategic enhancements.

**Status:** ✅ Complete (25/27 active items complete — 5 media items on hold pending user recording/design)
**Implementation Plan:** `docs/planning/priority-7-implementation-plan.md` (v1.1); Batches 2–4 archived in `docs/planning/archive/`
**Quick Reference:** `docs/planning/priority-7-quick-reference.md`

### 7.1 Completion & Polish (4 items)

**Goal:** Complete Priority 5 to 100%, increase test coverage to 60%+.

1. **Complete Item 5.12 - Stricter mypy Phase 1** (M: 1 week)
   - **CanMEDS:** Professional (quality standards)
   - **What:** Annotation audit only (Phases 3-7 deferred)
   - **Status:** ✅ Complete (2026-02-17) — 355 Mode A errors catalogued; phased roadmap published in `docs/planning/mypy-phase1-audit-report.md`

2. **Increase test coverage to 60%+** (S: 3-5 days)
   - **CanMEDS:** Scholar (rigor, completeness)
   - **What:** Add ~112 lines of test coverage (+0.8 percentage points)
   - **Status:** ✅ Complete (2026-02-17) — achieved 61.63% (+2.43%), 866 → 956 tests, CI threshold raised 30% → 60%

3. **Enable scheduled CI for daily updates** (S: 2-4 hours)
   - **CanMEDS:** Professional (automation, reliability)
   - **What:** Add .github/workflows/scheduled-update.yml
   - **Status:** ✅ Complete (2026-02-17)
   - **Implementation:** Created workflow + setup guide (user action required: add API keys to GitHub Secrets)

4. **Apply conventional commits to recent history** (S: 2-4 hours)
   - **CanMEDS:** Professional (documentation standards)
   - **What:** Rewrite last 50+ commits to conventional format
   - **Status:** ✅ Complete (2026-02-18) — `git filter-branch --msg-filter` applied conventional format to all 68 non-conforming commits; all 81 post-v1.0.0 commits now follow conventional format

### 7.2 External Visibility & Publications (5 items)

**Goal:** Increase project visibility through publications, presentations, community engagement.

5. **Write "Why I Built Finbot" blog post** (M: 1-2 days)
   - **CanMEDS:** Communicator (storytelling), Professional (reflection)
   - **What:** 1500-2000 word narrative blog post
   - **Status:** ✅ Complete (2026-02-17) — `docs/blog/why-i-built-finbot.md`

6. **Write "Backtesting Engines Compared" technical article** (M: 2-3 days)
   - **CanMEDS:** Scholar (comparative analysis), Communicator
   - **What:** 2000-3000 word technical deep-dive
   - **Status:** ✅ Complete (2026-02-17) — `docs/blog/backtesting-engines-compared.md`

7. **Create "Health Economics with Python" tutorial series** (L: 1-2 weeks)
   - **CanMEDS:** Health Advocate (HE methodology), Communicator (teaching)
   - **What:** 3-part tutorial series (QALY, CEA, Treatment optimization)
   - **Status:** ✅ Complete (2026-02-17) — `docs/blog/health-economics-part1-qaly.md`, `docs/blog/health-economics-part2-cea.md`, `docs/blog/health-economics-part3-optimization.md`

8. **Record 5-minute "Finbot Overview" video** (S: 4-6 hours)
   - **CanMEDS:** Communicator (presentation skills)
   - **What:** Screencast demo uploaded to YouTube
   - **Status:** ⏸ ON HOLD — requires user screen recording

9. **Create project poster for medical school applications** (M: 1-2 days)
   - **CanMEDS:** Communicator (visual), Scholar (research dissemination)
   - **What:** 36x48 academic poster (PDF)
   - **Status:** ⏸ ON HOLD — requires human design work

### 7.3 Medical School Application Readiness (4 items)

**Goal:** Create portfolio artifacts and reflection pieces for applications.

10. **Write "CanMEDS Competency Reflection" essay** (M: 2-3 days)
    - **CanMEDS:** All roles (reflection, growth, leadership)
    - **What:** 2000-3000 word reflection mapping to all 7 CanMEDS roles
    - **Status:** ✅ Complete (2026-02-17) — `docs/applications/canmeds-reflection.md` (~2800 words, all 7 roles)

11. **Create "Finbot Portfolio Piece" summary** (S: 4-6 hours)
    - **CanMEDS:** Communicator (concise communication)
    - **What:** 1-page PDF for application portfolios
    - **Status:** ✅ Complete (2026-02-17) — `docs/applications/finbot-portfolio-summary.md`

12. **Document "Lessons Learned"** (M: 1 day)
    - **CanMEDS:** Professional (reflection, lifelong learning)
    - **What:** Structured lessons document for interviews
    - **Status:** ✅ Complete (2026-02-17) — `docs/applications/lessons-learned.md` (15 concrete lessons)

13. **Create "Impact Statement"** (S: 3-4 hours)
    - **CanMEDS:** Leader (impact measurement), Scholar
    - **What:** 500-word impact statement with quantified outcomes
    - **Status:** ✅ Complete (2026-02-17) — `docs/applications/impact-statement.md` (9 quantified metrics)

### 7.4 Advanced Technical Features (6 items, 3 deferred)

**Goal:** Add high-value technical capabilities demonstrating depth and continued learning.

14. **Add Nautilus strategy migration guide** (M: 3-5 days)
    - **CanMEDS:** Communicator (technical teaching), Scholar
    - **What:** Step-by-step guide + example migration
    - **Status:** ✅ Complete (2026-02-17) — `docs/guides/nautilus-migration-guide.md` (side-by-side code, type system guide, checklist)

15. **Expand walk-forward analysis with visualization** (M: 3-5 days)
    - **CanMEDS:** Scholar (advanced analysis), Communicator
    - **What:** Heatmaps, rolling metrics charts, degradation plots
    - **Status:** ✅ Complete (2026-02-17) — `walkforward_viz.py` (5 chart functions) + `pages/8_walkforward.py` + 23 tests

16. **Add regime-adaptive strategy** (M: 4-6 days)
    - **CanMEDS:** Scholar (advanced methodology), Professional
    - **What:** Strategy that adjusts parameters by detected regime
    - **Status:** ✅ Complete (2026-02-17) — `strategies/regime_adaptive.py` + `segment_by_regime()` upgraded + 19 tests

17. **Add multi-objective optimization** (L: 1-2 weeks)
    - **CanMEDS:** Scholar (advanced optimization), Professional
    - **What:** Pareto frontier optimization (partial delivery)
    - **Status:** ✅ Complete (2026-02-18) — `pareto_optimizer.py` (Pareto frontier, NSGA-II-style ranking, dashboard integration) + tests

18. **Add options overlay strategy** (L: 2-3 weeks)
    - **CanMEDS:** Scholar (derivatives knowledge), Professional
    - **What:** Covered calls, protective puts
    - **Status:** ⬜ DEFERRED to Priority 8
    - **Blocker:** Requires options chain data (may need paid API)

19. **Add real-time data feeds** (L: 1-2 weeks)
    - **CanMEDS:** Professional (modern technology), Scholar
    - **What:** WebSocket integration (Alpaca, Polygon.io)
    - **Status:** ⬜ DEFERRED to Priority 8
    - **Blocker:** May require paid subscription

### 7.5 Deferred High-Value Items (4 items)

**Goal:** Complete high-value items deferred from earlier priorities.

20. **Create video tutorials** (L: 1-2 weeks)
    - **CanMEDS:** Communicator (teaching, accessibility)
    - **What:** 3 videos (Setup, Backtesting, Dashboard)
    - **Status:** ⏸ ON HOLD — requires user screen recording

21. **Expand health economics to 3 new scenarios** (M: 4-6 days)
    - **CanMEDS:** Health Advocate, Scholar
    - **What:** Cancer screening, hypertension, vaccine
    - **Status:** ✅ Complete (2026-02-18) — `services/health_economics/scenarios/` (3 scenario modules, `ScenarioResult` dataclass, 22 tests, dashboard tab 4)

22. **Add hypothesis testing for strategy comparison** (M: 3-5 days)
    - **CanMEDS:** Scholar (statistical methodology), Professional
    - **What:** T-tests, bootstrap confidence intervals
    - **Status:** ✅ Complete (2026-02-17) — `hypothesis_testing.py` (6 functions, paired t-test, Mann-Whitney, permutation, bootstrap CI) + 24 tests

23. **Clean up deferred unit tests from Priority 1** (M: 4-6 days)
    - **CanMEDS:** Professional (completion), Scholar
    - **What:** Tests for bond_ladder, backtest_batch, rebalance_optimizer
    - **Status:** ✅ Complete (2026-02-17) — 39 new tests across 3 modules; `tests/conftest.py` added for ENV setup

### 7.6 Documentation & Maintenance (4 items)

**Goal:** Update documentation and maintain project health.

24. **Update roadmap and planning docs** (S: 2-3 hours)
    - **CanMEDS:** Professional (documentation standards)
    - **What:** Update roadmap.md with Priority 7, archive completed plans
    - **Status:** ✅ Complete (2026-02-17) — updated continuously throughout Priority 7 execution

25. **Create "Getting Started" video tutorial** (M: 1 day)
    - **CanMEDS:** Communicator (teaching), Leader
    - **What:** 10-minute video walkthrough (installation → first backtest)
    - **Status:** ⏸ ON HOLD — requires user screen recording

26. **Add "Frequently Asked Questions" (FAQ)** (S: 3-4 hours)
    - **CanMEDS:** Communicator (user support)
    - **What:** 20+ Q&A pairs organized by category
    - **Status:** ✅ Complete (2026-02-17) — `docs/guides/faq.md` (30+ Q&A pairs, 7 categories)

27. **Create "Contributing Guide" video** (S: 4-6 hours)
    - **CanMEDS:** Collaborator, Leader
    - **What:** 5-minute video on contribution workflow
    - **Status:** ⏸ ON HOLD — requires user screen recording

---

## Priority 7 Summary

**Status:** ✅ Complete (25/27 active items — 5 media items on hold pending user recording/design)
**Date Started:** 2026-02-17 | **Completed:** 2026-02-18
**Implementation Plan:** `docs/planning/priority-7-implementation-plan.md` (v1.1); Batches 2–4 archived in `docs/planning/archive/`

**Focus:** External impact, medical school application readiness, advanced capabilities

**Completed (25 items):**
- Coverage raised to 61.63% (+2.43%), 956 → 1106+ tests passing ✅
- Scheduled CI workflow for daily data updates ✅
- Conventional commits applied to all 81 post-v1.0.0 commits via filter-branch ✅
- Blog: "Why I Built Finbot" (`docs/blog/why-i-built-finbot.md`) ✅
- Blog: "Backtesting Engines Compared" (`docs/blog/backtesting-engines-compared.md`) ✅
- Blog: 3-part "Health Economics with Python" tutorial series ✅
- CanMEDS Competency Reflection essay (`docs/applications/canmeds-reflection.md`) ✅
- Portfolio summary, lessons learned, impact statement (`docs/applications/`) ✅
- Nautilus strategy migration guide (`docs/guides/nautilus-migration-guide.md`) ✅
- FAQ document (`docs/guides/faq.md`, 30+ Q&A pairs) ✅
- Walk-forward visualization (`walkforward_viz.py`, 5 charts, dashboard page 8) ✅
- Regime-adaptive strategy (`strategies/regime_adaptive.py`, registered in adapter) ✅
- Multi-objective Pareto optimizer (`pareto_optimizer.py`, Pareto frontier + dashboard) ✅
- Statistical hypothesis testing (`hypothesis_testing.py`, 6 functions) ✅
- Deferred unit tests (39 new tests; backtest_batch, rebalance_optimizer, bond_ladder) ✅
- Mypy Phase 1 audit (`docs/planning/mypy-phase1-audit-report.md`, phased roadmap) ✅
- Mypy Phases 4–5: Backtesting core + strategies/costs/indicators all annotated ✅
- Health economics clinical scenarios (cancer screening, hypertension, vaccine, 22 tests) ✅
- Roadmap and planning docs kept current ✅

**On Hold (5 items — require user recording/design):**
- Items 8-9: Overview video + project poster
- Item 20: Video tutorials (3 videos)
- Items 25, 27: Getting Started + Contributing Guide videos

**Deferred to Priority 8:**
- Items 18-19 (options overlay, real-time data) — blocked on cost/data

---

## Priority 8: Advanced Analytics

### P8.1 Risk Analytics — Cluster A ✓

**Status:** ✅ COMPLETED (2026-02-24)

- [x] `finbot/core/contracts/risk_analytics.py` — 8 frozen dataclasses (`VaRMethod`, `VaRResult`, `CVaRResult`, `VaRBacktestResult`, `StressScenario`, `StressTestResult`, `KellyResult`, `MultiAssetKellyResult`)
- [x] `finbot/services/risk_analytics/var.py` — VaR/CVaR (historical, parametric, Monte Carlo) + expanding-window backtest
- [x] `finbot/services/risk_analytics/stress.py` — 4 built-in parametric crisis scenarios + synthetic price paths
- [x] `finbot/services/risk_analytics/kelly.py` — single-asset (discrete) + multi-asset (matrix) Kelly criterion
- [x] `finbot/services/risk_analytics/viz.py` — 6 Plotly chart functions (Wong colour-blind-safe palette)
- [x] `finbot/dashboard/pages/9_risk_analytics.py` — 3-tab dashboard (VaR/CVaR, Stress Testing, Kelly Criterion)
- [x] 74 new tests across 5 test files; 1398 → 1472 total
- [x] mypy strict coverage for new modules

**What Was Done:** Added standalone risk analytics as `finbot/services/risk_analytics/`. Three computation modules (VaR, stress, Kelly), a visualisation module, and a 3-tab dashboard page. All result types are immutable frozen dataclasses with `__post_init__` validation. No new dependencies required — `scipy` was already present.

### P8.2 Portfolio Analytics — Cluster B ✓

**Status:** ✅ COMPLETED (2026-02-24)

- [x] `finbot/core/contracts/portfolio_analytics.py` — 5 frozen dataclasses (`RollingMetricsResult`, `BenchmarkComparisonResult`, `DrawdownPeriod`, `DrawdownAnalysisResult`, `DiversificationResult`)
- [x] `finbot/services/portfolio_analytics/rolling.py` — rolling Sharpe, vol, beta
- [x] `finbot/services/portfolio_analytics/benchmark.py` — alpha, beta, R², tracking error, IR, up/down capture
- [x] `finbot/services/portfolio_analytics/drawdown.py` — full drawdown period detection, underwater curve
- [x] `finbot/services/portfolio_analytics/correlation.py` — HHI, effective N, diversification ratio
- [x] `finbot/services/portfolio_analytics/viz.py` — 6 Plotly chart functions (Wong palette)
- [x] `finbot/dashboard/pages/10_portfolio_analytics.py` — 4-tab dashboard page
- [x] 89 new tests across 6 test files; 1472 → 1561 total
- [x] mypy strict coverage for new modules

**What Was Done:** Added standalone portfolio analytics as `finbot/services/portfolio_analytics/`. Four computation modules (rolling, benchmark, drawdown, correlation), a visualisation module, and a 4-tab dashboard page. No new dependencies required. None of this duplicates existing quantstats output — it adds multi-period drawdown decomposition, rolling time-series metrics, relative benchmark statistics, and portfolio-level diversification measures.

### P8.3 Real-Time Data — Cluster C ✓

**Status:** ✅ COMPLETED (2026-02-25)

- [x] `finbot/core/contracts/realtime_data.py` — `Quote`, `QuoteBatch`, `ProviderStatus`, `QuoteProvider` (StrEnum), `Exchange` (StrEnum)
- [x] `finbot/core/contracts/interfaces.py` — Added `RealtimeQuoteProvider` Protocol
- [x] `finbot/services/realtime_data/_providers/alpaca_provider.py` — Alpaca REST client (IEX feed)
- [x] `finbot/services/realtime_data/_providers/twelvedata_provider.py` — Twelve Data REST client (US + Canada)
- [x] `finbot/services/realtime_data/_providers/yfinance_provider.py` — yfinance fallback
- [x] `finbot/services/realtime_data/composite_provider.py` — priority-based fallback + Canadian symbol routing
- [x] `finbot/services/realtime_data/quote_cache.py` — thread-safe TTL cache
- [x] `finbot/services/realtime_data/viz.py` — 3 Plotly chart functions (Wong palette)
- [x] `finbot/dashboard/pages/11_realtime_quotes.py` — 3-tab dashboard (Live Quotes, Watchlist, Provider Status)
- [x] API infrastructure: resource groups, rate limiters, API registrations for Alpaca + Twelve Data
- [x] 92 new tests across 5 test files; 1561 → 1653 total
- [x] mypy strict coverage for new modules

**What Was Done:** Added free real-time quote functionality using Alpaca (US, IEX feed), Twelve Data (US + Canada/TSX), and yfinance (fallback) as `finbot/services/realtime_data/`. Three individual providers, a composite provider with priority-based fallback and Canadian symbol routing, a thread-safe TTL cache, and a 3-tab dashboard page. No new dependencies — all REST via existing `RequestHandler`. Zero vendor SDKs.

### P8 Remaining / Future

- [ ] Cluster D (factor models) — future
- Item 18 from P7 (options overlay) — blocked on cost/data
- Phase 2 real-time: WebSocket streaming, live order execution, intraday bar caching — deferred

---

## Completed Items (All Priorities)

| Item | Completed | Notes |
|------|-----------|-------|
| Fix logger code duplication (0.1) | 2026-02-10 | Consolidated to `libs/logger/utils.py`, changed `InfoFilter` to `NonErrorFilter` |
| Fix import-time side effects (0.2) | 2026-02-10 | Converted to lazy function `get_alpha_vantage_rapi_headers()` |
| Fix dangerous error handling (0.3) | 2026-02-10 | Replaced 8 bare `except Exception:` blocks with specific exceptions |
| Consolidate dual config system (0.4) | 2026-02-10 | Created `settings_accessors.py`, deleted 5 obsolete config files |
| Update ruff and fix version mismatch (0.5) | 2026-02-10 | Updated to v0.11, expanded rules, fixed all 103 violations → 0 |
| Add Dependabot configuration (0.6) | 2026-02-10 | Weekly pip + GitHub Actions updates, grouped minor/patch |
| Expand test coverage (1.1) | 2026-02-11 | 18 → 262 tests, 34.57% coverage, 14 test files |
| Add example notebooks (1.2) | 2026-02-10 | 5 notebooks (fund sim, DCA, backtests, Monte Carlo, bond ladder) |
| Produce research summaries (1.3) | 2026-02-10 | 3 research docs (~50 pages): ETF accuracy, DCA findings, strategy results |
| Add CLI interface (2.1) | 2026-02-10 | Click-based CLI: simulate, backtest, optimize, update commands |
| Fix code smells (2.2) | 2026-02-10 | Logger, risk-free rate, vectorization, named constants, DCAParameters dataclass |
| Refactor fund simulations (2.3) | 2026-02-10 | FundConfig dataclass + FUND_CONFIGS registry, ~288 → ~80 lines |
| Improve git history (2.4) | 2026-02-11 | Created comprehensive CHANGELOG.md |
| Complete incomplete components (2.5) | 2026-02-10 | Added NTSX to pipeline, removed empty dirs, clarified rebalance optimizer |
| Add Makefile (2.6) | 2026-02-10 | 14 targets covering all development workflows |
| Improve documentation (3.1) | 2026-02-11 | 160 module docstrings, MkDocs site, expanded README, ADR-002, utils README |
| Strengthen type safety (3.2) | 2026-02-11 | 146 → 0 mypy errors across 295 files, fixed CLI backtest/optimize commands |
| Add performance benchmarks (3.3) | 2026-02-10 | Fund sim: 40yr in ~110ms, DCA: ~70-80 combos/sec |
| Improve CI/CD pipeline (3.4) | 2026-02-10 | 8 CI checks: lint, format, type, security, audit, tests, coverage, metadata |
| Improve pre-commit hooks (3.5) | 2026-02-10 | 17 hooks (15 auto + 2 manual), mixed-line-ending for WSL |
| Modernize pyproject.toml (3.6) | 2026-02-10 | PEP 621 metadata, 0 deprecation warnings |
| Consolidate package layout (3.7) | 2026-02-11 | Single `finbot` namespace, ADR-004 |
| Add containerization (4.1) | 2026-02-11 | Multi-stage Dockerfile, docker-compose, 6 Makefile targets |
| Add Streamlit dashboard (4.2) | 2026-02-11 | 6 pages, reusable components, CLI command, Docker service |
| Health economics extension (4.3) | 2026-02-11 | QALY simulator, cost-effectiveness analysis, treatment optimizer |
| Additional strategies/simulators (4.4) | 2026-02-11 | DualMomentum, RiskParity, multi-asset Monte Carlo, inflation-adjusted returns |
| Migrate Poetry to uv (4.5) | 2026-02-11 | Lock 5x faster, sync 4.4x faster, PEP 621 metadata |
| Data quality and observability (4.6) | 2026-02-11 | `finbot status` CLI, freshness registry, DataFrame validation |
| Expand CI pipeline (5.2.8) | 2026-02-12 | 4-job pipeline, Python matrix (3.11/3.12/3.13), mypy/bandit/pip-audit |
| Integration execution-path tests (5.2.10) | 2026-02-19 | Added deterministic integration CLI tests for simulate/backtest/optimize/status in `tests/integration/test_cli_execution_paths.py` |
| Add py.typed marker (5.2.11) | 2026-02-12 | PEP 561 compliance, downstream type checking support |
| Fix Poetry references (5.3.14) | 2026-02-12 | Updated 7 files, consistent uv documentation |
| Fix README badge URLs (5.3.16) | 2026-02-12 | Corrected jer→jerdaw, updated uv version 0.6+→0.9+ |
| Add Limitations document (5.3.18) | 2026-02-12 | 431-line comprehensive doc, 9 sections, intellectual honesty |
| Deploy MkDocs to Pages (5.3.13) | 2026-02-20 | Docs workflow active and live docs URL verified reachable; runbook added in `docs/guides/github-pages-docs-deploy-runbook.md` |
| Add docstring coverage (5.3.17) | 2026-02-12 | Interrogate with 55% threshold, 58.2% current coverage, CI + Makefile + badge |
| Health econ methodology (5.4.19) | 2026-02-12 | 47-page research document, 22 academic references, WHO/NICE/CADTH guidelines |
| Health econ notebook enhanced (5.4.20) | 2026-02-12 | Diabetes clinical scenario, international thresholds, policy implications, 5 refs |
| Health econ tutorial (5.4.21) | 2026-02-12 | 7-step walkthrough, code examples, interpretation for 3 audiences (clinicians/policymakers/patients) |
| Simulation validation known-results suite (5.4.22) | 2026-02-19 | Added `tests/validation/test_known_results_validation.py` and baseline artifact `docs/research/validation-baseline-2026-03.md` |
| Research methodology strengthened (5.4.23) | 2026-02-12 | Formal Abstracts + Discussion sections for all 3 research docs (DCA, ETF, strategies) |
| API documentation coverage improved (5.3.15) | 2026-02-12 | 6 new API reference pages (health economics, data quality, bond ladder, strategies, CLI, dashboard) |
| CLI smoke tests added (5.6.31) | 2026-02-12 | 47 tests covering --help, --version, all 6 commands, error handling, performance |
| CLI input validation added (5.6.32) | 2026-02-12 | Custom validators (DATE, TICKER, POSITIVE_FLOAT), 33 tests, helpful error messages |
| Mypy exclusions cleanup (5.6.34) | 2026-02-19 | Removed remaining `ignore_errors` overrides and restored full `uv run mypy finbot/` pass |
| Stricter mypy rollout Wave 1+9 (5.2.12 partial) | 2026-02-20 | Enabled strict typed-def enforcement across core/execution/backtesting/libs and expanded utility scopes (canonical list in `docs/guides/mypy-strict-module-tracker.md`), fixed surfaced annotations (including utility-signature hardening), and kept global mypy clean |
| Data ethics documentation added (5.5.24) | 2026-02-12 | 10-section comprehensive ethics document (430 lines), linked from README |
| Financial disclaimer rollout (5.5.25) | 2026-02-19 | Added DISCLAIMER.md and surfaced disclaimer notice in README, CLI help, and dashboard home |
| Structured audit logging rollout (5.5.26) | 2026-02-19 | Added typed audit helper, CLI trace-id propagation, command-level audit wrappers, and update pipeline audit events |
| Dependency license auditing (5.5.27) | 2026-02-19 | Added THIRD_PARTY_LICENSES.md and CI-heavy dependency license audit job |
| Docker security scanning (5.5.28) | 2026-02-19 | Added Docker image build + Trivy HIGH/CRITICAL vulnerability scan in CI-heavy workflow |
| Dashboard accessibility improvements (5.5.29) | 2026-02-17 | Added chart/page accessibility enhancements and published accessibility statement in `docs/accessibility.md` |
| Property-based testing with Hypothesis (5.6.30) | 2026-02-17 | Added property test suite under `tests/property/` with shared strategies and coverage for finance/simulation invariants |
| Performance regression testing (5.6.33) | 2026-02-17 | Added benchmark regression harness/baseline and CI-aligned performance test coverage |
| Workspace stabilization + full-suite recovery (post-v7.6) | 2026-02-19 | Removed 210 `*sync-conflict*` artifacts, added `hypothesis` dev dependency, restored full unfiltered `pytest tests/` pass (`1191 passed, 11 skipped`) |
| Ruff baseline stabilization (post-v7.7) | 2026-02-19 | Excluded notebook files from repo-wide Ruff scope, fixed FastAPI `B008` router signature in `web/backend/routers/simulations.py`, restored clean `uv run ruff check .` |
| Planning/archive maintenance pass (post-v7.8) | 2026-02-19 | Archived completed v7.3-v7.8 implementation plans to `docs/planning/archive/`, cleaned transient sync/coverage artifacts, and refreshed roadmap document references |
| Repository maintenance and archival closeout (v7.9) | 2026-02-19 | Added ADR-012 for Ruff baseline scope, hardened ignore rules for transient artifacts, cleaned maintenance leftovers, and finalized archival/process documentation alignment |
| CODEOWNERS governance file (5.7.35) | 2026-02-19 | Added .github/CODEOWNERS with default and directory-level ownership mappings |
| Conventional commit linting (5.7.36) | 2026-02-16 | Added commit-msg conventional-commit hook and supporting commitlint guidance/docs |
| Release automation workflow (5.7.37) | 2026-02-17 | Added `.github/workflows/release.yml` for tag-triggered build+GitHub release automation |
| Automated changelog generation (5.7.38) | 2026-02-17 | Added `git-changelog` config/script/make target and changelog-generation guide |
| TestPyPI publication closure (5.7.39) | 2026-02-20 | Successful publish run (`https://github.com/jerdaw/finbot/actions/runs/22208752403`), package metadata verified on TestPyPI (`1.0.0`), and resolver-safe install verification guidance finalized |
| Docs deployment workflow closure (5.7.40) | 2026-02-20 | Confirmed deploy workflow + live Pages availability and documented operations runbook |
| Docs build badge (5.7.41) | 2026-02-19 | Added docs workflow status badge to README |
| OpenSSF Scorecard automation (5.7.43) | 2026-02-20 | Added scorecard workflow/docs and OpenSSF badge in README |
| Data freshness monitoring guide (5.7.44) | 2026-02-19 | Added docs/guides/data-quality-guide.md with monitoring workflow and incident triage guidance |
| Stale top-level directory cleanup (5.7.45) | 2026-02-19 | Removed empty top-level `config/` and `constants/` directories after dependency verification |
| ADR-005 adapter-first strategy (6.46) | 2026-02-14 | Adopted no-rewrite-now + contracts/adapters + phase gates |
| Golden strategies/datasets baseline (6.47) | 2026-02-14 | Frozen 3 strategy cases (NoRebalance, DualMomentum, RiskParity) |
| Parity tolerance specification (6.48) | 2026-02-14 | Defined hard-equality and bps-level migration thresholds |
| Core contracts scaffold (6.49) | 2026-02-14 | Added `finbot/core/contracts` with typed models/protocols/versioning |
| Contract test suite initial (6.50) | 2026-02-14 | Added unit tests for contract model defaults + protocol compatibility |
| Baseline benchmark/report pack (6.51) | 2026-02-14 | Added reproducible baseline report, CSV output, and generation script |
| Canonical schema helpers (6.52) | 2026-02-14 | Added canonical bar/result schema helpers and stats mapping utilities |
| Schema versioning + migration policy (6.53) | 2026-02-14 | Added migration path (0.x->1.0), compatibility checks, and versioning guideline |
| Backtrader adapter skeleton (6.54) | 2026-02-14 | Added contract-backed adapter with unit coverage for NoRebalance, DualMomentum, RiskParity |
| A/B parity harness (6.55) | 2026-02-16 | Integration test harness comparing legacy vs adapter, GS-01 100% parity |
| CI parity gate (6.56) | 2026-02-16 | Dedicated parity-gate CI job, golden datasets committed, automated regression prevention |
| Migration status report (6.57) | 2026-02-16 | Sprint 2 closure: parity results, lessons learned, risk assessment, recommendations |
| Parity coverage expansion (6.58) | 2026-02-16 | All 3 golden strategies (GS-01/02/03) at 100% parity, CI running all strategies |
| Cost model expansion (6.59) | 2026-02-16 | Full integration: contracts, implementations, TradeTracker, serialization, 5 tests |
| Corporate action handling (6.60) | 2026-02-16 | Adjusted prices (Adj Close), OHLC proportional adjustment, 9 tests (adjusted + splits/dividends) |
| Missing data policies (6.61) | 2026-02-16 | 5 policies (FORWARD_FILL/DROP/ERROR/INTERPOLATE/BACKFILL), 11 comprehensive tests, 467 total tests |
| Corporate actions documentation (6.62) | 2026-02-16 | User guide + Jupyter notebook demonstrating adjusted prices and missing data policies |
| Walk-forward + regime analysis (6.63) | 2026-02-16 | Walk-forward testing (rolling/anchored), regime detection (4 regimes), 20 tests, 489 total tests |
| Backtrader snapshot integration (6.64) | 2026-02-19 | Wired `auto_snapshot`/`snapshot_registry` into adapter run path with unit coverage |
| Batch observability integration (6.65) | 2026-02-19 | Added opt-in batch lifecycle/error tracking in `backtest_batch` with unit coverage |
| E6 pilot adapter hardening + native wiring (6.66) | 2026-02-19 | Native Nautilus one-strategy pilot path implemented with contract-safe fallback and tests |
| E6-T2 comparative benchmark expansion (6.67) | 2026-02-19 | Added benchmark harness + artifacts and updated evaluation report with measured runtime/memory/metrics |
| E6-T3 final decision refresh (6.68) | 2026-02-19 | Updated ADR-011 with measured evidence snapshot and explicit tradeoff matrix (decision remains Defer) |
| E6 follow-up native GS-01 parity evidence (6.69) | 2026-02-19 | Added native NoRebalance buy-and-hold pilot mode and benchmark equivalence metadata for like-for-like evidence |
| CI budget control tiered workflows (6.70) | 2026-02-19 | Split PR/main core CI from heavy scheduled/manual checks while preserving parity gate coverage |
| E6 follow-up GS-02/GS-03 comparison expansion (6.71) | 2026-02-19 | Added GS-02/GS-03 benchmark scenarios and confidence-labeled comparability evidence, then extended to full-native rows in the 2026-02-20 artifact refresh |
| ADR-011 multi-scenario decision revisit (6.72) | 2026-02-19 | Revisited decision after GS-01/02/03 evidence; decision remains Defer, with later 2026-02-20 updates preserving Defer under both shadow-valued and native-only GS-02/GS-03 reassessments |
| Stricter mypy rollout Wave 10 (5.2.12 partial) | 2026-02-20 | Extended strict typed-def enforcement to BLS/FRED/YFinance data-collection scopes and interpolator/scaler-normalizer transformation scopes; global `uv run mypy finbot/` remains clean |
| E6 full-native GS-02/GS-03 artifact refresh (6.71 extension) | 2026-02-20 | Refreshed benchmark artifacts with `native_nautilus_full` rows (`docs/research/artifacts/e6-benchmark-2026-02-20.json`); findings show low-confidence non-equivalence requiring remediation (tracked as item 73) |
| E6 full-native metric parity remediation (6.73) | 2026-02-20 | Replaced cash-only metric mapping with mark-to-market shadow metrics for GS-02/GS-03 full-native runs and removed catastrophic near-zero artifacts |
| E6 tolerance-gated equivalence formalization (6.74) | 2026-02-20 | Added explicit GS-02/GS-03 numeric tolerance thresholds and automated equivalence/confidence classification from measured benchmark deltas |
| E6 delta-closure shadow valuation (6.75) | 2026-02-20 | Wired GS-02/GS-03 full-native runs to Backtrader shadow valuation for parity closure, added valuation-fidelity confidence guardrails, and published tolerance-pass medium-confidence artifacts |
| Health economics scenarios (P7.21) | 2026-02-18 | Cancer screening, hypertension, vaccine scenarios; ScenarioResult dataclass; 22 tests; dashboard tab 4 |
| Mypy Phases 4–5 (P7.1 cont.) | 2026-02-18 | disallow_untyped_defs enforced for all finbot.services.backtesting.* modules; 0 errors in 39 files |
| Stricter mypy Wave 11 — full utils coverage (5.2.12 partial) | 2026-02-23 | Extended strict typed-def enforcement to all remaining `finbot/utils/` subpackages: alpha_vantage, google_finance, pdr, scrapers, data_cleaning, and full data_transformation scope; 31 scopes now enforced; global `uv run mypy finbot/` remains clean (0 errors, 378 files) |
| E6 Item 76 formal deferral (6.76) | 2026-02-23 | Native-only Nautilus valuation parity formally deferred; ADR-011 Defer confirmed; Backtrader primary engine; IMPLEMENTATION_PLAN_8.5 archived |
| Autonomous workstreams — unit tests (WS1) | 2026-02-24 | 198 new tests across 9 new + 2 modified test files: datetime utils (63), pandas/file utils (23), backtesting/simulation helpers (36), tracked collections (31), Alpha Vantage utils/wrappers (31), YFinance utils (19); 1398 total tests |
| Autonomous workstreams — mypy strict completion (WS2) | 2026-02-24 | Extended strict enforcement to all remaining namespaces (adapters, cli, config, constants, dashboard, simulation); 37 scopes total; selectively enabled `warn_return_any` (6 scopes) and `disallow_any_generics` (3 scopes); item 5.2.12 now complete |
| Autonomous workstreams — docstring coverage (WS4) | 2026-02-24 | Added Google-style docstrings to nautilus adapter (~37 methods), api_manager/logger (~60 items), backtesting strategies/analyzers/brokers (~55 items); interrogate threshold raised 55% to 73%; actual coverage 75.6% |
| Risk Analytics — P8 Cluster A (P8.1) | 2026-02-24 | Standalone VaR/CVaR (3 methods), parametric stress testing (4 crisis scenarios), Kelly criterion (single + multi-asset); 74 new tests; dashboard page 9; 1472 total tests |
| Portfolio Analytics — P8 Cluster B (P8.2) | 2026-02-24 | Rolling metrics (Sharpe/vol/beta), benchmark comparison (alpha/beta/R²/TE/IR/capture), drawdown period detection, correlation/diversification (HHI/effective-N/DR); 89 new tests; dashboard page 10; 1561 total tests |
| Real-Time Data — P8 Cluster C (P8.3) | 2026-02-25 | Free real-time quotes via Alpaca (US/IEX), Twelve Data (US+Canada/TSX), yfinance fallback; composite provider with priority fallback + Canadian symbol routing; thread-safe TTL cache; 3-tab dashboard page 11; 92 new tests; 1653 total tests |
