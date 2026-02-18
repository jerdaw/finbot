"""Statistical hypothesis testing for backtesting result comparison.

Provides rigorous statistical tools to answer:
  - "Is strategy A significantly better than strategy B?"
  - "Does the strategy significantly beat a benchmark?"
  - "What is the confidence interval around this strategy's CAGR?"

All tests use scipy.stats (already a project dependency).  No new packages
are required.

Typical usage::

    from finbot.services.backtesting.hypothesis_testing import (
        paired_t_test,
        bootstrap_confidence_interval,
        compare_strategies,
    )

    # Compare two strategies across walk-forward windows
    result = paired_t_test(strategy_a_results, strategy_b_results, metric="cagr")
    print(result.notes)

    # Bootstrap CI for a single strategy
    ci = bootstrap_confidence_interval(strategy_results, metric="sharpe")
    print(f"95% CI: [{ci.lower:.3f}, {ci.upper:.3f}]")
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
import pandas as pd
import scipy.stats as stats

from finbot.core.contracts import BacktestRunResult
from finbot.core.contracts.walkforward import WalkForwardResult


@dataclass(frozen=True, slots=True)
class HypothesisTestResult:
    """Result of a single hypothesis test.

    Attributes:
        test_name: Short identifier, e.g. "paired_t_test".
        statistic: Test statistic value (t, U, etc.).
        p_value: Two-tailed p-value.
        significant: Whether p_value < alpha.
        alpha: Significance level used (default 0.05).
        n_samples: Number of observations used.
        notes: Plain-English interpretation of the result.
    """

    test_name: str
    statistic: float
    p_value: float
    significant: bool
    alpha: float
    n_samples: int
    notes: str


@dataclass(frozen=True, slots=True)
class BootstrapCI:
    """Bootstrap confidence interval for a single metric.

    Attributes:
        metric: Metric name.
        estimate: Point estimate (mean of bootstrap samples).
        lower: Lower bound of the confidence interval.
        upper: Upper bound of the confidence interval.
        confidence_level: e.g. 0.95 for 95% CI.
        n_bootstrap: Number of bootstrap iterations used.
    """

    metric: str
    estimate: float
    lower: float
    upper: float
    confidence_level: float
    n_bootstrap: int


def _extract_metric(results: Sequence[BacktestRunResult], metric: str) -> list[float]:
    """Extract per-result metric values, raising descriptive errors."""
    if len(results) < 2:
        raise ValueError(f"Need at least 2 results for hypothesis testing, got {len(results)}.")
    values: list[float] = []
    for i, r in enumerate(results):
        if metric not in r.metrics:
            raise KeyError(f"Metric '{metric}' not found in result {i}. Available metrics: {sorted(r.metrics.keys())}")
        values.append(float(r.metrics[metric]))
    return values


def paired_t_test(
    results_a: Sequence[BacktestRunResult],
    results_b: Sequence[BacktestRunResult],
    metric: str = "cagr",
    *,
    alpha: float = 0.05,
) -> HypothesisTestResult:
    """Paired t-test comparing metric values across matched windows.

    Best suited for comparing two strategies run over **identical** walk-forward
    windows.  Assumes the differences are approximately normally distributed.

    H₀: E[metric_A - metric_B] = 0
    H₁: E[metric_A - metric_B] ≠ 0

    Args:
        results_a: Backtest results for strategy A (one per window).
        results_b: Backtest results for strategy B (one per window).
        metric: Canonical metric key to compare.
        alpha: Significance level (default 0.05).

    Returns:
        HypothesisTestResult with statistic, p-value, and interpretation.

    Raises:
        ValueError: If lengths differ or n < 2.
        KeyError: If metric not found in any result.
    """
    if len(results_a) != len(results_b):
        raise ValueError(f"paired_t_test requires equal-length sequences. Got {len(results_a)} vs {len(results_b)}.")
    vals_a = _extract_metric(results_a, metric)
    vals_b = _extract_metric(results_b, metric)

    t_stat, p_val = stats.ttest_rel(vals_a, vals_b)
    significant = float(p_val) < alpha
    direction = "A > B" if float(np.mean(vals_a)) > float(np.mean(vals_b)) else "B > A"
    decision = "reject H₀" if significant else "fail to reject H₀"
    notes = (
        f"Paired t-test on {metric.upper()} (n={len(vals_a)}): "
        f"t={t_stat:.3f}, p={p_val:.4f} vs alpha={alpha}. "
        f"{decision.capitalize()}. "
        f"{'Significant difference detected' if significant else 'No significant difference'} "
        f"({direction}, mean_A={np.mean(vals_a):.4f}, mean_B={np.mean(vals_b):.4f})."
    )
    return HypothesisTestResult(
        test_name="paired_t_test",
        statistic=float(t_stat),
        p_value=float(p_val),
        significant=significant,
        alpha=alpha,
        n_samples=len(vals_a),
        notes=notes,
    )


def mannwhitney_test(
    results_a: Sequence[BacktestRunResult],
    results_b: Sequence[BacktestRunResult],
    metric: str = "cagr",
    *,
    alpha: float = 0.05,
) -> HypothesisTestResult:
    """Mann-Whitney U test (non-parametric two-sample comparison).

    Does not assume normality.  Best when sample sizes are small or the
    return distribution is skewed.

    H₀: P(A > B) = 0.5
    H₁: P(A > B) ≠ 0.5

    Args:
        results_a: Backtest results for strategy A.
        results_b: Backtest results for strategy B.
        metric: Canonical metric key.
        alpha: Significance level.

    Returns:
        HypothesisTestResult.

    Raises:
        ValueError: If n < 2.
        KeyError: If metric not found.
    """
    vals_a = _extract_metric(results_a, metric)
    vals_b = _extract_metric(results_b, metric)

    u_stat, p_val = stats.mannwhitneyu(vals_a, vals_b, alternative="two-sided")
    significant = float(p_val) < alpha
    decision = "reject H₀" if significant else "fail to reject H₀"
    notes = (
        f"Mann-Whitney U on {metric.upper()} (n_A={len(vals_a)}, n_B={len(vals_b)}): "
        f"U={u_stat:.1f}, p={p_val:.4f} vs alpha={alpha}. "
        f"{decision.capitalize()}. "
        f"{'Significant stochastic dominance detected' if significant else 'No significant difference'}."
    )
    return HypothesisTestResult(
        test_name="mannwhitney_test",
        statistic=float(u_stat),
        p_value=float(p_val),
        significant=significant,
        alpha=alpha,
        n_samples=len(vals_a),
        notes=notes,
    )


def permutation_test(
    results_a: Sequence[BacktestRunResult],
    results_b: Sequence[BacktestRunResult],
    metric: str = "cagr",
    *,
    n_permutations: int = 1000,
    alpha: float = 0.05,
    random_seed: int = 42,
) -> HypothesisTestResult:
    """Permutation test for strategy comparison.

    Builds a null distribution by randomly swapping labels and recomputing
    the mean difference.  Makes no distributional assumptions.

    Args:
        results_a: Backtest results for strategy A.
        results_b: Backtest results for strategy B.
        metric: Canonical metric key.
        n_permutations: Number of permutation iterations.
        alpha: Significance level.
        random_seed: Random seed for reproducibility.

    Returns:
        HypothesisTestResult.

    Raises:
        ValueError: If n < 2.
        KeyError: If metric not found.
    """
    vals_a = np.array(_extract_metric(results_a, metric))
    vals_b = np.array(_extract_metric(results_b, metric))

    observed_diff = float(np.mean(vals_a) - np.mean(vals_b))
    combined = np.concatenate([vals_a, vals_b])
    n_a = len(vals_a)

    rng = np.random.default_rng(random_seed)
    null_diffs: list[float] = []
    for _ in range(n_permutations):
        perm = rng.permutation(combined)
        null_diffs.append(float(np.mean(perm[:n_a]) - np.mean(perm[n_a:])))

    null_arr = np.array(null_diffs)
    p_val = float(np.mean(np.abs(null_arr) >= abs(observed_diff)))
    significant = p_val < alpha
    decision = "reject H₀" if significant else "fail to reject H₀"
    notes = (
        f"Permutation test on {metric.upper()} (n_perm={n_permutations}): "
        f"observed_diff={observed_diff:.4f}, p={p_val:.4f} vs alpha={alpha}. "
        f"{decision.capitalize()}. "
        f"{'Significant difference detected' if significant else 'No significant difference'}."
    )
    return HypothesisTestResult(
        test_name="permutation_test",
        statistic=observed_diff,
        p_value=p_val,
        significant=significant,
        alpha=alpha,
        n_samples=len(vals_a),
        notes=notes,
    )


def bootstrap_confidence_interval(
    results: Sequence[BacktestRunResult],
    metric: str = "cagr",
    *,
    confidence_level: float = 0.95,
    n_bootstrap: int = 10_000,
    random_seed: int = 42,
) -> BootstrapCI:
    """Bootstrap percentile confidence interval for a single metric.

    Resamples with replacement to estimate sampling uncertainty.

    Args:
        results: Backtest results (one per walk-forward window, or strategy runs).
        metric: Canonical metric key.
        confidence_level: e.g. 0.95 for 95% CI.
        n_bootstrap: Number of bootstrap samples.
        random_seed: Random seed for reproducibility.

    Returns:
        BootstrapCI with lower/upper bounds.

    Raises:
        ValueError: If n < 2.
        KeyError: If metric not found.
    """
    vals = np.array(_extract_metric(results, metric))
    estimate = float(np.mean(vals))

    rng = np.random.default_rng(random_seed)
    boot_means = np.array([np.mean(rng.choice(vals, size=len(vals), replace=True)) for _ in range(n_bootstrap)])

    tail = (1.0 - confidence_level) / 2.0
    lower = float(np.percentile(boot_means, tail * 100))
    upper = float(np.percentile(boot_means, (1.0 - tail) * 100))

    return BootstrapCI(
        metric=metric,
        estimate=estimate,
        lower=lower,
        upper=upper,
        confidence_level=confidence_level,
        n_bootstrap=n_bootstrap,
    )


def compare_strategies(
    strategies: dict[str, Sequence[BacktestRunResult]],
    metric: str = "cagr",
    *,
    alpha: float = 0.05,
) -> pd.DataFrame:
    """Pairwise strategy comparison using paired t-tests.

    For N strategies, performs N*(N-1)/2 pairwise paired t-tests and returns
    a summary DataFrame.

    Note: Strategy result sequences must have the same length (same windows).

    Args:
        strategies: Dict mapping strategy name → sequence of BacktestRunResults.
        metric: Canonical metric key.
        alpha: Significance level.

    Returns:
        DataFrame with columns: strategy_a, strategy_b, mean_a, mean_b,
        statistic, p_value, significant, winner.

    Raises:
        ValueError: If fewer than 2 strategies provided.
    """
    names = list(strategies.keys())
    if len(names) < 2:
        raise ValueError(f"compare_strategies requires ≥2 strategies, got {len(names)}.")

    rows = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            name_a, name_b = names[i], names[j]
            res = paired_t_test(strategies[name_a], strategies[name_b], metric, alpha=alpha)
            vals_a = _extract_metric(strategies[name_a], metric)
            vals_b = _extract_metric(strategies[name_b], metric)
            mean_a = float(np.mean(vals_a))
            mean_b = float(np.mean(vals_b))
            winner = name_a if mean_a >= mean_b else name_b
            if not res.significant:
                winner = "no_significant_winner"
            rows.append(
                {
                    "strategy_a": name_a,
                    "strategy_b": name_b,
                    "mean_a": mean_a,
                    "mean_b": mean_b,
                    "statistic": res.statistic,
                    "p_value": res.p_value,
                    "significant": res.significant,
                    "winner": winner,
                }
            )

    return pd.DataFrame(rows)


def summarize_walk_forward_significance(
    result: WalkForwardResult,
    benchmark_metric_value: float,
    metric: str = "cagr",
    *,
    alpha: float = 0.05,
) -> HypothesisTestResult:
    """One-sample t-test: does the strategy significantly beat a benchmark?

    Tests H₀: μ(per_window_metric) = benchmark_metric_value.

    Example: does mean CAGR across walk-forward windows differ from 0.07 (7% S&P 500)?

    Args:
        result: Walk-forward result object.
        benchmark_metric_value: Benchmark value to test against (e.g. 0.07 for 7% CAGR).
        metric: Canonical metric key.
        alpha: Significance level.

    Returns:
        HypothesisTestResult.

    Raises:
        KeyError: If metric not found in any result.
    """
    if not result.test_results:
        raise ValueError("WalkForwardResult has no test_results.")
    vals = _extract_metric(list(result.test_results), metric)
    t_stat, p_val = stats.ttest_1samp(vals, popmean=benchmark_metric_value)
    significant = float(p_val) < alpha
    decision = "reject H₀" if significant else "fail to reject H₀"
    mean_val = float(np.mean(vals))
    notes = (
        f"One-sample t-test: H₀ μ({metric})={benchmark_metric_value:.4f} "
        f"(n={len(vals)}): t={t_stat:.3f}, p={p_val:.4f} vs alpha={alpha}. "
        f"{decision.capitalize()}. "
        f"Observed mean={mean_val:.4f}. "
        f"{'Strategy significantly differs from benchmark' if significant else 'No significant difference from benchmark'}."
    )
    return HypothesisTestResult(
        test_name="one_sample_t_test",
        statistic=float(t_stat),
        p_value=float(p_val),
        significant=significant,
        alpha=alpha,
        n_samples=len(vals),
        notes=notes,
    )
