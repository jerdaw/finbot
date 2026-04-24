"""Opt-in parity checks against the public testfol.io backtester.

These tests are intentionally excluded from the default test run. They make
live requests to testfol.io, so run them manually and keep the case limit low.
"""

from __future__ import annotations

import json
import math
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Literal

import pytest

os.environ.setdefault("ENV", "development")
os.environ.setdefault("DYNACONF_ENV", "development")

TESTFOLIO_BACKTEST_URL = "https://testfol.io/api/backtest"
RUN_ENV_VAR = "FINBOT_RUN_TESTFOLIO_PARITY"
CASE_LIMIT_ENV_VAR = "FINBOT_TESTFOLIO_CASE_LIMIT"
REQUEST_DELAY_ENV_VAR = "FINBOT_TESTFOLIO_REQUEST_DELAY_SECONDS"
REQUEST_TIMEOUT_ENV_VAR = "FINBOT_TESTFOLIO_TIMEOUT_SECONDS"

INITIAL_CASH = 1_000_000.0
DEFAULT_CASE_LIMIT = 1
DEFAULT_REQUEST_DELAY_SECONDS = 2.0
DEFAULT_TIMEOUT_SECONDS = 60.0


@dataclass(frozen=True)
class ParityCase:
    """One Finbot/testfol.io parity scenario."""

    case_id: str
    tickers: tuple[str, ...]
    weights: tuple[float, ...]
    strategy: Literal["NoRebalance", "Rebalance"]
    strategy_params: dict[str, Any]
    testfolio_rebalance_freq: str
    start_date: str
    end_date: str


@dataclass(frozen=True)
class NormalizedMetrics:
    """Comparable metric subset shared by Finbot and testfol.io."""

    ending_value: float
    roi: float
    cagr: float
    max_drawdown: float
    annualized_volatility: float
    sharpe: float


@dataclass(frozen=True)
class MetricTolerance:
    """How far an external parity metric may drift before failing."""

    mode: Literal["absolute", "relative"]
    limit: float


PARITY_CASES = (
    ParityCase(
        case_id="spy_buy_hold_2020",
        tickers=("SPY",),
        weights=(1.0,),
        strategy="NoRebalance",
        strategy_params={"equity_proportions": [1.0]},
        testfolio_rebalance_freq="None",
        start_date="2020-01-01",
        end_date="2020-12-31",
    ),
    ParityCase(
        case_id="spy_tlt_60_40_yearly_2020_2021",
        tickers=("SPY", "TLT"),
        weights=(0.6, 0.4),
        strategy="Rebalance",
        strategy_params={"rebal_proportions": [0.6, 0.4], "rebal_interval": 253},
        testfolio_rebalance_freq="Yearly",
        start_date="2020-01-01",
        end_date="2021-12-31",
    ),
)

TOLERANCES = {
    # Cross-tool parity allows small drift from data revisions, rebalance timing,
    # and Backtrader's whole-share execution model.
    "ending_value": MetricTolerance("relative", 0.01),
    "roi": MetricTolerance("absolute", 0.015),
    "cagr": MetricTolerance("absolute", 0.005),
    "max_drawdown": MetricTolerance("absolute", 0.015),
    "annualized_volatility": MetricTolerance("absolute", 0.025),
    "sharpe": MetricTolerance("absolute", 0.10),
}

pytestmark = [
    pytest.mark.slow,
    pytest.mark.external,
    pytest.mark.skipif(
        os.getenv(RUN_ENV_VAR) != "1",
        reason=f"Set {RUN_ENV_VAR}=1 to run live testfol.io parity checks.",
    ),
]


def _float_from_env(name: str, default: float) -> float:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    try:
        parsed = float(raw_value)
    except ValueError as exc:
        raise AssertionError(f"{name} must be a float, got {raw_value!r}") from exc
    if parsed < 0:
        raise AssertionError(f"{name} must be non-negative, got {parsed}")
    return parsed


def _selected_cases() -> tuple[ParityCase, ...]:
    raw_limit = os.getenv(CASE_LIMIT_ENV_VAR, str(DEFAULT_CASE_LIMIT))
    try:
        case_limit = int(raw_limit)
    except ValueError as exc:
        raise AssertionError(f"{CASE_LIMIT_ENV_VAR} must be an integer, got {raw_limit!r}") from exc

    if case_limit < 1:
        raise AssertionError(f"{CASE_LIMIT_ENV_VAR} must be at least 1, got {case_limit}")
    return PARITY_CASES[: min(case_limit, len(PARITY_CASES))]


def _build_testfolio_payload(case: ParityCase) -> dict[str, Any]:
    allocation = {ticker: round(weight * 100, 10) for ticker, weight in zip(case.tickers, case.weights, strict=True)}
    return {
        "start_date": case.start_date,
        "end_date": case.end_date,
        "start_val": INITIAL_CASH,
        "adj_inflation": False,
        "cashflow": 0,
        "cashflow_freq": "Yearly",
        "cashflow_offset": 0,
        "match_first_portfolio_income_cashflows": False,
        "cashflow_legs": [],
        "one_time_cashflows": [],
        "rolling_window": 60,
        "withdrawal_surface_include": False,
        "withdrawal_surface_projection": "NONE",
        "withdrawal_surface_projection_min_years": 10,
        "withdrawal_surface_start_years": 5,
        "withdrawal_surface_end_years": 50,
        "withdrawal_surface_step_years": 1,
        "backtests": [
            {
                "invest_dividends": True,
                "rebalance_freq": case.testfolio_rebalance_freq,
                "rebalance_offset": 0,
                "allocation": allocation,
                "drag": 0,
                "absolute_dev": 0,
                "relative_dev": 0,
            }
        ],
    }


def _fetch_testfolio_backtest(payload: dict[str, Any]) -> dict[str, Any]:
    request = urllib.request.Request(
        TESTFOLIO_BACKTEST_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "User-Agent": "finbot-testfolio-parity/1.0",
        },
        method="POST",
    )
    timeout = _float_from_env(REQUEST_TIMEOUT_ENV_VAR, DEFAULT_TIMEOUT_SECONDS)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:500]
        if exc.code in {403, 408, 409, 425, 429, 500, 502, 503, 504}:
            pytest.skip(f"testfol.io backtest request unavailable/rate-limited ({exc.code}): {body}")
        pytest.fail(f"testfol.io backtest request failed with HTTP {exc.code}: {body}")
    except urllib.error.URLError as exc:
        pytest.skip(f"testfol.io backtest request unavailable: {exc.reason}")


def _finite_float(value: Any, label: str) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise AssertionError(f"{label} must be numeric, got {value!r}") from exc
    if not math.isfinite(parsed):
        raise AssertionError(f"{label} must be finite, got {value!r}")
    return parsed


def _extract_testfolio_metrics(payload: dict[str, Any], case_id: str) -> NormalizedMetrics:
    errors = payload.get("errors") or []
    if errors:
        raise AssertionError(f"testfol.io returned errors for {case_id}: {errors!r}")

    stats = payload.get("stats")
    if not isinstance(stats, list) or not stats or not isinstance(stats[0], dict):
        raise AssertionError(f"testfol.io response for {case_id} did not include stats[0]")

    first_stats = stats[0]
    return NormalizedMetrics(
        ending_value=_finite_float(first_stats.get("end_val"), "testfolio.stats[0].end_val"),
        roi=_finite_float(first_stats.get("cum_return"), "testfolio.stats[0].cum_return") / 100.0,
        cagr=_finite_float(first_stats.get("cagr"), "testfolio.stats[0].cagr") / 100.0,
        max_drawdown=_finite_float(first_stats.get("max_drawdown"), "testfolio.stats[0].max_drawdown") / 100.0,
        annualized_volatility=_finite_float(first_stats.get("std"), "testfolio.stats[0].std") / 100.0,
        sharpe=_finite_float(first_stats.get("sharpe"), "testfolio.stats[0].sharpe"),
    )


def _run_finbot_backtest(case: ParityCase) -> NormalizedMetrics:
    from web.backend.routers.backtesting import run_backtest
    from web.backend.schemas.backtesting import BacktestRequest

    response = run_backtest(
        BacktestRequest(
            tickers=list(case.tickers),
            strategy=case.strategy,
            strategy_params=case.strategy_params,
            start_date=case.start_date,
            end_date=case.end_date,
            initial_cash=INITIAL_CASH,
            risk_free_rate=0.0,
        )
    )
    stats = response.stats
    return NormalizedMetrics(
        ending_value=_finite_float(stats.get("Ending Value"), "finbot.stats['Ending Value']"),
        roi=_finite_float(stats.get("ROI"), "finbot.stats['ROI']"),
        cagr=_finite_float(stats.get("CAGR"), "finbot.stats['CAGR']"),
        max_drawdown=_finite_float(stats.get("Max Drawdown"), "finbot.stats['Max Drawdown']"),
        annualized_volatility=_finite_float(
            stats.get("Annualized Volatility"),
            "finbot.stats['Annualized Volatility']",
        ),
        sharpe=_finite_float(stats.get("Sharpe"), "finbot.stats['Sharpe']"),
    )


def _metric_diff(metric_name: str, finbot: float, testfolio: float) -> float:
    tolerance = TOLERANCES[metric_name]
    if tolerance.mode == "relative":
        denominator = max(abs(testfolio), 1e-12)
        return abs(finbot - testfolio) / denominator
    return abs(finbot - testfolio)


def _format_failure(case_id: str, metric_name: str, finbot: float, testfolio: float, diff: float) -> str:
    tolerance = TOLERANCES[metric_name]
    return (
        f"{case_id} {metric_name}: finbot={finbot:.8f}, testfolio={testfolio:.8f}, "
        f"{tolerance.mode}_diff={diff:.8f}, tolerance={tolerance.limit:.8f}"
    )


def test_finbot_backtests_match_testfolio_for_limited_golden_cases() -> None:
    """Compare Finbot against a deliberately small set of testfol.io cases."""
    failures: list[str] = []
    cases = _selected_cases()
    delay_seconds = _float_from_env(REQUEST_DELAY_ENV_VAR, DEFAULT_REQUEST_DELAY_SECONDS)

    for case_index, case in enumerate(cases):
        if case_index > 0 and delay_seconds > 0:
            time.sleep(delay_seconds)

        finbot_metrics = _run_finbot_backtest(case)
        testfolio_metrics = _extract_testfolio_metrics(
            _fetch_testfolio_backtest(_build_testfolio_payload(case)),
            case.case_id,
        )

        for metric_name in TOLERANCES:
            finbot_value = getattr(finbot_metrics, metric_name)
            testfolio_value = getattr(testfolio_metrics, metric_name)
            diff = _metric_diff(metric_name, finbot_value, testfolio_value)
            if diff > TOLERANCES[metric_name].limit:
                failures.append(_format_failure(case.case_id, metric_name, finbot_value, testfolio_value, diff))

    assert not failures, "Finbot/testfol.io parity failures:\n" + "\n".join(failures)
