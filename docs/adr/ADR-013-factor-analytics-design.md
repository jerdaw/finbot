# ADR-013: Factor Analytics Module Design

**Status:** Accepted
**Date:** 2026-02-25

## Context

Following the completion of P8 Clusters A–C (Risk Analytics, Portfolio Analytics, Real-Time Data),
Cluster D adds Fama-French-style multi-factor model analysis to finbot's standalone analytics
capabilities. The key design questions were:

1. **Data fetching vs. pure computation**: Should the module fetch Fama-French factors from the
   internet, or accept them as inputs?
2. **OLS implementation**: Use `scipy.stats.linregress`, `statsmodels`, or raw numpy?
3. **Model type detection**: Auto-detect CAPM/FF3/FF5 or require explicit specification?
4. **Contract structure**: Three separate result types or a single unified result?

## Decision

### Pure computation — no data fetching

The module accepts returns arrays/DataFrames as inputs and computes. It does not fetch factor data
from Kenneth French's data library or any external source. The dashboard handles data loading
(local parquet or CSV upload).

**Rationale:** Consistent with `benchmark.py`, `kelly.py`, and all other P8 modules. Keeps service
modules testable without network access. Users who want Fama-French factors can download the CSV
directly from the data library and upload via the dashboard.

### Raw numpy OLS (`np.linalg.lstsq`)

Instead of `statsmodels` (not a project dependency) or `scipy.stats.linregress` (single-factor
only), we use `np.linalg.lstsq` directly with the design matrix `[ones | factor_matrix]`.

Standard errors are computed via `np.linalg.pinv(X.T @ X)` (pseudoinverse fallback) to handle
near-collinear factor matrices safely — the same pattern used in `kelly.py:143`. T-statistics use
`scipy.stats.t.cdf` which is already a project dependency.

**Rationale:** No new dependencies. Handles multi-factor case uniformly. `pinv` fallback prevents
crashes when factors are highly correlated.

### Auto-detect model type from column names

`_infer_model_type()` checks whether column names contain the well-known Fama-French set:
- `{"Mkt-RF"}` → CAPM
- `{"Mkt-RF", "SMB", "HML"}` (exactly) → FF3
- `{"Mkt-RF", "SMB", "HML", "RMW", "CMA"}` (superset) → FF5
- Anything else → CUSTOM

Users can override via the `model_type` parameter.

**Rationale:** Reduces friction for users working directly with Fama-French CSV downloads (which use
these exact column names). Override preserves flexibility for non-standard factor sets.

### Three separate result contracts

`FactorRegressionResult`, `FactorAttributionResult`, and `FactorRiskResult` are distinct frozen
dataclasses rather than a single combined type.

**Rationale:**
- Attribution and risk decomposition are optional analyses that build on regression. Users who only
  want regression outputs shouldn't receive attribution/risk fields with placeholder values.
- Each result can be passed directly to the corresponding `viz.py` function.
- Pre-computed regression results can be shared across attribution and risk calls without
  re-running the OLS.
- Consistent with the design of `VaRResult` / `CVaRResult` / `KellyResult` in `risk_analytics.py`.

## Consequences

**Positive:**
- Zero new dependencies.
- OLS with `pinv` is numerically robust for correlated factor sets.
- Auto-detection makes Fama-French CSV uploads (the most common use case) zero-configuration.
- Pre-computed regression result can be passed to both attribution and risk functions, avoiding
  duplicate OLS runs.
- 96 tests covering all contracts, computation logic, and visualisations.

**Negative:**
- Users must supply factor data themselves (no built-in download). The dashboard provides a CSV
  upload widget to mitigate this.
- Attribution uses sum-of-period-returns rather than compounded returns. This is a linear
  approximation that slightly overstates contributions for long horizons or large returns.
  Documented in the dashboard.
