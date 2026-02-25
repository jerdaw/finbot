"""Stress testing module for risk analytics.

Applies parametric market stress scenarios to a portfolio and
computes trough values, drawdowns, and recovery price paths.

Four built-in historical scenarios are provided:
- ``2008_financial_crisis``: -56% over 17 months, 48-month recovery
- ``covid_crash_2020``: -34% over 23 days, 126-day recovery
- ``dot_com_bubble``: -49% over 630 days, 1260-day recovery
- ``black_monday_1987``: -23% single-day, 504-day recovery
"""

from __future__ import annotations

import numpy as np

from finbot.core.contracts.risk_analytics import StressScenario, StressTestResult

# ---------------------------------------------------------------------------
# Built-in historical scenarios
# ---------------------------------------------------------------------------

SCENARIOS: dict[str, StressScenario] = {
    "2008_financial_crisis": StressScenario(
        name="2008 Financial Crisis",
        shock_return=-0.565,
        shock_duration_days=357,
        recovery_days=756,
        description="S&P 500 peak-to-trough Oct 2007 - Mar 2009",
    ),
    "covid_crash_2020": StressScenario(
        name="COVID-19 Crash 2020",
        shock_return=-0.340,
        shock_duration_days=23,
        recovery_days=126,
        description="S&P 500 peak-to-trough Feb 19 - Mar 23, 2020",
    ),
    "dot_com_bubble": StressScenario(
        name="Dot-com Bubble Burst",
        shock_return=-0.491,
        shock_duration_days=630,
        recovery_days=1260,
        description="NASDAQ peak-to-trough Mar 2000 - Oct 2002",
    ),
    "black_monday_1987": StressScenario(
        name="Black Monday 1987",
        shock_return=-0.226,
        shock_duration_days=1,
        recovery_days=504,
        description="DJIA single-day crash, October 19, 1987",
    ),
}


def run_stress_test(
    returns: np.ndarray,
    scenario: str | StressScenario,
    initial_value: float = 100.0,
) -> StressTestResult:
    """Apply a stress scenario to a portfolio.

    The shock phase linearly interpolates from ``initial_value`` to
    ``initial_value * (1 + shock_return)`` over ``shock_duration_days``
    steps.  The recovery phase then linearly interpolates back to
    ``initial_value`` over ``recovery_days`` steps.

    The price path has length ``shock_duration_days + recovery_days + 1``
    (including the starting value at index 0).

    Args:
        returns: Historical return series (used only for metadata; not
            applied to the path — the path is driven entirely by the
            scenario parameters).
        scenario: A ``StressScenario`` object **or** a string key into
            the ``SCENARIOS`` dict.
        initial_value: Starting portfolio value in any currency unit.
            Defaults to 100.0.

    Returns:
        ``StressTestResult`` with full price path and summary metrics.

    Raises:
        KeyError: If ``scenario`` is a string not found in ``SCENARIOS``.
    """
    if isinstance(scenario, str):
        scenario = SCENARIOS[scenario]

    trough_value = initial_value * (1.0 + scenario.shock_return)
    trough_return = scenario.shock_return

    # Build shock phase: linear interpolation from initial to trough
    shock_values = np.linspace(initial_value, trough_value, scenario.shock_duration_days + 1)

    # Build recovery phase: linear interpolation from trough to initial
    # Exclude the trough point (already in shock_values) but include the final point
    if scenario.recovery_days > 0:
        recovery_values = np.linspace(trough_value, initial_value, scenario.recovery_days + 1)[1:]
    else:
        recovery_values = np.array([], dtype=float)

    full_path = np.concatenate([shock_values, recovery_values])
    price_path: tuple[float, ...] = tuple(float(v) for v in full_path)

    min_value = float(np.min(full_path))
    max_drawdown_pct = (initial_value - min_value) / initial_value * 100.0

    recovery_value = float(full_path[-1])

    return StressTestResult(
        scenario_name=scenario.name,
        initial_value=initial_value,
        trough_value=trough_value,
        trough_return=trough_return,
        recovery_value=recovery_value,
        max_drawdown_pct=max_drawdown_pct,
        shock_duration_days=scenario.shock_duration_days,
        recovery_days=scenario.recovery_days,
        price_path=price_path,
        scenario=scenario,
    )


def run_all_scenarios(
    returns: np.ndarray,
    initial_value: float = 100.0,
) -> dict[str, StressTestResult]:
    """Run all four built-in stress scenarios.

    Args:
        returns: Historical return series (passed through to each
            ``run_stress_test`` call).
        initial_value: Starting portfolio value.  Defaults to 100.0.

    Returns:
        Dict mapping scenario key to ``StressTestResult``.
    """
    return {key: run_stress_test(returns, key, initial_value=initial_value) for key in SCENARIOS}
