# Finbot Roadmap

**Created:** 2026-02-10
**Last Updated:** 2026-02-19
**Status:** Priority 0-5 baseline complete/progressing; Priority 6 adapter-first backtesting/live-readiness in progress (E0-E5 complete, E6-T1 complete, E6 decision gate in progress)

Improvements, fixes, and enhancements identified from comprehensive project evaluations. Organized by priority tier. Previous items (Priority 0-4) have been implemented. New Priority 5 items focus on making the project suitable for Ontario medical school admissions (OMSAS/CanMEDS frameworks).

See Completed Items table below and git history for details on implemented features.

---

## Priority 0: Bugs and Architectural Hazards ✓

All 6 items complete. Fixed logger duplication, import-time side effects, dangerous error handling, dual config system, ruff version mismatch, and added Dependabot.

## Priority 1: Critical Gaps ✓

All 3 items complete. Expanded test coverage (18 → 262 tests, 34.57% coverage), created 5 example notebooks with findings, and produced 3 research summaries.

**Remaining (Deferred — Not Blocking):**
- [ ] Add tests for `bond_ladder_simulator` end-to-end (requires yield data from FRED)
- [ ] Add tests for `backtest_batch`: parallel execution, result aggregation
- [ ] Add tests for `rebalance_optimizer`
- [ ] Add tests for `approximate_overnight_libor` (requires FRED data)
- [ ] Add tests for data collection utilities: `get_history`, `get_fred_data` (requires mock API responses)
- [ ] Populate `tests/integration/` with at least one end-to-end pipeline test (requires data files)
- [ ] Increase coverage target from 30% to 60% as more tests are added
- [ ] Consider publishing research findings as a blog post or short paper for external visibility

## Priority 2: High-Impact Improvements ✓

All 6 items complete. Added CLI interface (4 commands), fixed code smells, refactored fund simulations to data-driven config, improved git history (CHANGELOG.md), completed incomplete components, added Makefile.

**Remaining (Deferred — Not Blocking):**
- [ ] Apply data-driven config pattern to `sim_specific_bond_indexes.py` (only 3 functions, not worth refactoring)
- [ ] Adopt conventional commit format going forward

## Priority 3: Moderate Improvements ✓

All 7 items complete. Improved documentation (160 module docstrings, MkDocs site, ADRs), strengthened type safety (146 → 0 mypy errors), added performance benchmarks, improved CI/CD pipeline, improved pre-commit hooks, modernized pyproject.toml metadata, consolidated package layout.

**Remaining (Deferred — Not Blocking):**
- [ ] Enable stricter mypy settings (`disallow_untyped_defs`, etc.)
- [ ] Add `py.typed` marker file for PEP 561 compliance
- [ ] Pin CI action versions to SHA hashes
- [ ] Add scheduled CI for daily update pipeline (requires API keys in CI)

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
   - **Status:** ⬜ Not started

10. **Add integration tests** (M: 1-2 days)
    - **CanMEDS:** Scholar (systems-level thinking)
    - **What:** Write integration tests for: fund simulation, backtest runner, DCA optimizer, CLI commands
    - **Evidence:** Populated tests/integration/, passing integration tests
    - **Status:** ⬜ Not started

11. **Add py.typed marker file** (S: 5 min)
    - **CanMEDS:** Professional (standards compliance)
    - **What:** Create empty finbot/py.typed file for PEP 561
    - **Evidence:** PEP 561 compliance, downstream type checking support
    - **Status:** ✅ Complete (2026-02-12)

12. **Enable stricter mypy settings** (L: 1-2 weeks)
    - **CanMEDS:** Professional (quality standards)
    - **What:** Gradually enable disallow_untyped_defs=true, add type annotations
    - **Evidence:** Stricter mypy config, type-safe codebase
    - **Status:** ⬜ Not started

### 5.3 Documentation & Communication

13. **Deploy MkDocs documentation to GitHub Pages** (M: 2-4 hours)
    - **CanMEDS:** Communicator (published resource)
    - **What:** Add GitHub Actions workflow for mkdocs gh-deploy, configure site_url, fix broken links
    - **Evidence:** Live documentation URL (https://jerdaw.github.io/finbot/)
    - **Status:** 🔄 Partially Complete (2026-02-12) - Workflow created, user must enable GitHub Pages
    - **Implementation:** Updated site_url, created .github/workflows/docs.yml, tested build (5.27s)
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
    - **Status:** ⬜ Not started
    - **Note:** Requires historical data files

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
    - **Status:** ⬜ Not started

26. **Add structured logging for audit trails** (M: 1 day)
    - **CanMEDS:** Professional (governance, accountability)
    - **What:** Ensure all operations logged with structured JSON (timestamp, parameters, results)
    - **Evidence:** Audit trail capability
    - **Status:** ⬜ Not started

27. **Add dependency license auditing** (S: 1-2 hours)
    - **CanMEDS:** Professional (legal compliance)
    - **What:** Add pip-licenses to CI, create THIRD_PARTY_LICENSES.md or verify compatible licenses
    - **Evidence:** License audit report, compliance verification
    - **Status:** ⬜ Not started

28. **Add Docker security scanning** (M: 2-4 hours)
    - **CanMEDS:** Professional (security-conscious)
    - **What:** Add trivy or grype container scanning to CI, document container security posture
    - **Evidence:** Container security scan results
    - **Status:** ⬜ Not started

29. **Add dashboard accessibility improvements** (M: 1-2 days)
    - **CanMEDS:** Health Advocate, Professional (inclusive design)
    - **What:** Add alt text, WCAG AA contrast, keyboard navigation, screen reader labels; document accessibility
    - **Evidence:** Accessible dashboard, accessibility documentation
    - **Status:** ⬜ Not started

### 5.6 Additional Quality & Testing

30. **Add property-based testing with Hypothesis** (M: 1-2 days)
    - **CanMEDS:** Scholar (edge case rigor)
    - **What:** Add hypothesis to dev deps, write property tests for fund simulator, CGR, drawdown, etc.
    - **Evidence:** Advanced testing methodology, edge case coverage
    - **Status:** ⬜ Not started

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
    - **Status:** ⬜ Not started

34. **Fix remaining mypy exclusions** (M: 1-2 days)
    - **CanMEDS:** Professional (quality standards)
    - **What:** Address 4 modules with ignore_errors=true, add proper type annotations
    - **Evidence:** Zero mypy exclusions
    - **Status:** ⬜ Not started

### 5.7 Professional Polish & Deployment

35. **Add CODEOWNERS file** (S: 10 min)
    - **CanMEDS:** Professional, Leader (governance)
    - **What:** Create .github/CODEOWNERS mapping directories
    - **Evidence:** Automatic review requests, governance artifact
    - **Status:** ⬜ Not started

36. **Add conventional commit linting** (S: 1-2 hours)
    - **CanMEDS:** Professional (governance maturity)
    - **What:** Add commitlint pre-commit hook validating conventional commits
    - **Evidence:** Consistent commit history
    - **Status:** ⬜ Not started

37. **Add release automation workflow** (M: 2-4 hours)
    - **CanMEDS:** Professional (DevOps maturity)
    - **What:** Create .github/workflows/release.yml for tag-triggered releases
    - **Evidence:** Automated release pipeline
    - **Status:** ⬜ Not started
    - **Prereqs:** Item 3 (git tags)

38. **Add automated changelog generation** (S: 2-4 hours)
    - **CanMEDS:** Professional (process automation)
    - **What:** Add git-cliff or similar, configure for conventional commits
    - **Evidence:** Auto-generated release notes
    - **Status:** ⬜ Not started
    - **Prereqs:** Item 36 (conventional commits)

39. **Publish package to TestPyPI** (M: 2-4 hours)
    - **CanMEDS:** Leader (making tools available)
    - **What:** Add GitHub Actions workflow to publish to TestPyPI on release
    - **Evidence:** TestPyPI listing, installable package
    - **Status:** ⬜ Not started
    - **Prereqs:** Items 2, 3 (version fix, releases)

40. **Add docs deployment workflow** (S: 1-2 hours)
    - **CanMEDS:** Professional (CI/CD maturity)
    - **What:** Create .github/workflows/docs.yml for auto-deploy to GitHub Pages
    - **Evidence:** Auto-deployed documentation
    - **Status:** ⬜ Not started

41. **Add docs build status badge** (S: 10 min)
    - **CanMEDS:** Professional (project maturity signals)
    - **What:** Add documentation workflow badge to README
    - **Evidence:** Additional status badge
    - **Status:** ⬜ Not started
    - **Prereqs:** Item 40 (docs workflow)

42. **Add project logo/branding** (S: 1-2 hours)
    - **CanMEDS:** Communicator (visual identity)
    - **What:** Create simple SVG logo, add to README and docs site
    - **Evidence:** Visual branding, professional appearance
    - **Status:** ⬜ Not started
    - **Note:** Requires human approval of design

43. **Add OpenSSF Scorecard or REUSE compliance** (M: 1-2 days)
    - **CanMEDS:** Professional (best practice compliance)
    - **What:** Run OpenSSF Scorecard, address findings, add badge to README
    - **Evidence:** Third-party validation badge
    - **Status:** ⬜ Not started
    - **Prereqs:** Items 1, 4, 5, 6 (governance files)

44. **Add data freshness monitoring documentation** (S: 2-4 hours)
    - **CanMEDS:** Professional (operations documentation)
    - **What:** Create docs/guides/data-quality-guide.md explaining registry, thresholds, monitoring
    - **Evidence:** Operations documentation
    - **Status:** ⬜ Not started

45. **Clean up stale top-level directories** (S: 30 min)
    - **CanMEDS:** Professional (clean structure)
    - **What:** Verify config/ and constants/ top-level dirs are redundant, remove or symlink
    - **Evidence:** Clean repository structure
    - **Status:** ⬜ Not started
    - **Note:** Verify no references remain

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
- `docs/planning/backtesting-live-readiness-implementation-plan.md`
- `docs/planning/backtesting-live-readiness-backlog.md`
- `docs/planning/backtesting-live-readiness-handoff-2026-02-14.md`
- `docs/planning/e3-t3-walkforward-regime-implementation-plan.md`
- `docs/planning/archive/IMPLEMENTATION_PLAN_6.2_E6_EXECUTION_READY.md` (archived after completion)

64-66. **E4 follow-up + E6-T1 implementation batch** (S: 1-2 days each)
    - **Status:** ✅ Complete (2026-02-19, trimmed; details recorded in Completed Items table)

67. **E6-T2 comparative benchmark expansion** (M: 3-5 days)
    - **What:** Publish side-by-side Backtrader vs native Nautilus deltas (returns/drawdown/trades/runtime/memory) on frozen datasets.
    - **Evidence:** `docs/research/nautilus-pilot-evaluation.md` update with measured benchmark section + reproducible command log.
    - **Status:** ⬜ Not started

68. **E6-T3 final decision refresh** (S: 1-2 days)
    - **What:** Revisit ADR-011 with measured E6-T2 evidence and record Go/No-Go/Hybrid outcome.
    - **Evidence:** `docs/adr/ADR-011-nautilus-decision.md` revision with explicit tradeoff table.
    - **Status:** ⬜ Not started

**Current Phase:** Epic E6 (comparative evaluation report + decision gate)
- E4 reproducibility/observability deferred integration items have been partially closed.

---

## Completed Items (Priority 0-4)

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
| Add py.typed marker (5.2.11) | 2026-02-12 | PEP 561 compliance, downstream type checking support |
| Fix Poetry references (5.3.14) | 2026-02-12 | Updated 7 files, consistent uv documentation |
| Fix README badge URLs (5.3.16) | 2026-02-12 | Corrected jer→jerdaw, updated uv version 0.6+→0.9+ |
| Add Limitations document (5.3.18) | 2026-02-12 | 431-line comprehensive doc, 9 sections, intellectual honesty |
| Deploy MkDocs to Pages (5.3.13) | 2026-02-12 | Workflow created, awaiting user to enable Pages |
| Add docstring coverage (5.3.17) | 2026-02-12 | Interrogate with 55% threshold, 58.2% current coverage, CI + Makefile + badge |
| Health econ methodology (5.4.19) | 2026-02-12 | 47-page research document, 22 academic references, WHO/NICE/CADTH guidelines |
| Health econ notebook enhanced (5.4.20) | 2026-02-12 | Diabetes clinical scenario, international thresholds, policy implications, 5 refs |
| Health econ tutorial (5.4.21) | 2026-02-12 | 7-step walkthrough, code examples, interpretation for 3 audiences (clinicians/policymakers/patients) |
| Research methodology strengthened (5.4.23) | 2026-02-12 | Formal Abstracts + Discussion sections for all 3 research docs (DCA, ETF, strategies) |
| API documentation coverage improved (5.3.15) | 2026-02-12 | 6 new API reference pages (health economics, data quality, bond ladder, strategies, CLI, dashboard) |
| CLI smoke tests added (5.6.31) | 2026-02-12 | 47 tests covering --help, --version, all 6 commands, error handling, performance |
| CLI input validation added (5.6.32) | 2026-02-12 | Custom validators (DATE, TICKER, POSITIVE_FLOAT), 33 tests, helpful error messages |
| Data ethics documentation added (5.5.24) | 2026-02-12 | 10-section comprehensive ethics document (430 lines), linked from README |
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
