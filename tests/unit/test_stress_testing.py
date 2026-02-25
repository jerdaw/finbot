"""Tests for stress testing module."""

from __future__ import annotations

import numpy as np
import pytest

from finbot.core.contracts.risk_analytics import StressScenario, StressTestResult
from finbot.services.risk_analytics.stress import SCENARIOS, run_all_scenarios, run_stress_test

DUMMY_RETURNS = np.random.default_rng(seed=1).normal(0.001, 0.01, 252)


class TestBuiltinScenarios:
    """Tests for the four pre-defined SCENARIOS constants."""

    def test_all_four_scenarios_present(self) -> None:
        """All four scenario keys are present."""
        expected = {"2008_financial_crisis", "covid_crash_2020", "dot_com_bubble", "black_monday_1987"}
        assert set(SCENARIOS.keys()) == expected

    def test_all_scenarios_are_stress_scenario(self) -> None:
        """Each value is a StressScenario instance."""
        for key, scenario in SCENARIOS.items():
            assert isinstance(scenario, StressScenario), f"{key} is not a StressScenario"

    def test_all_shock_returns_negative(self) -> None:
        """All built-in scenarios have negative shock_return."""
        for key, scenario in SCENARIOS.items():
            assert scenario.shock_return < 0, f"{key} has non-negative shock_return"


class TestStressScenarioValidation:
    """Tests for StressScenario __post_init__ validation."""

    def test_positive_shock_return_raises(self) -> None:
        """Positive shock_return raises ValueError."""
        with pytest.raises(ValueError, match="shock_return"):
            StressScenario(name="Bad", shock_return=0.1, shock_duration_days=10, recovery_days=30)

    def test_zero_shock_allowed(self) -> None:
        """Zero shock_return is allowed."""
        s = StressScenario(name="Zero", shock_return=0.0, shock_duration_days=1, recovery_days=1)
        assert s.shock_return == 0.0


class TestRunStressTest:
    """Tests for run_stress_test function."""

    def test_returns_stress_test_result(self) -> None:
        """run_stress_test returns StressTestResult."""
        result = run_stress_test(DUMMY_RETURNS, "2008_financial_crisis")
        assert isinstance(result, StressTestResult)

    def test_trough_less_than_initial(self) -> None:
        """trough_value < initial_value for any negative shock."""
        result = run_stress_test(DUMMY_RETURNS, "covid_crash_2020")
        assert result.trough_value < result.initial_value

    def test_trough_return_matches_shock(self) -> None:
        """trough_return matches the scenario's shock_return."""
        result = run_stress_test(DUMMY_RETURNS, "2008_financial_crisis")
        expected = SCENARIOS["2008_financial_crisis"].shock_return
        assert abs(result.trough_return - expected) < 1e-10

    def test_price_path_length(self) -> None:
        """Price path length equals shock_duration + recovery_days + 1."""
        scenario = SCENARIOS["covid_crash_2020"]
        result = run_stress_test(DUMMY_RETURNS, "covid_crash_2020")
        expected_length = scenario.shock_duration_days + scenario.recovery_days + 1
        assert len(result.price_path) == expected_length

    def test_price_path_starts_at_initial(self) -> None:
        """Price path starts at initial_value."""
        result = run_stress_test(DUMMY_RETURNS, "black_monday_1987", initial_value=200.0)
        assert abs(result.price_path[0] - 200.0) < 1e-9

    def test_price_path_ends_at_initial(self) -> None:
        """Price path ends at initial_value (full recovery)."""
        result = run_stress_test(DUMMY_RETURNS, "black_monday_1987", initial_value=200.0)
        assert abs(result.price_path[-1] - 200.0) < 1e-9

    def test_max_drawdown_positive(self) -> None:
        """max_drawdown_pct is positive for negative shock scenarios."""
        result = run_stress_test(DUMMY_RETURNS, "dot_com_bubble")
        assert result.max_drawdown_pct > 0

    def test_custom_initial_value(self) -> None:
        """Custom initial_value is honoured."""
        result = run_stress_test(DUMMY_RETURNS, "covid_crash_2020", initial_value=50_000.0)
        assert result.initial_value == 50_000.0


class TestRunAllScenarios:
    """Tests for run_all_scenarios function."""

    def test_returns_all_four_keys(self) -> None:
        """Returns dict with all four scenario keys."""
        results = run_all_scenarios(DUMMY_RETURNS)
        assert set(results.keys()) == set(SCENARIOS.keys())

    def test_all_results_are_stress_test_result(self) -> None:
        """All values are StressTestResult instances."""
        results = run_all_scenarios(DUMMY_RETURNS)
        for key, result in results.items():
            assert isinstance(result, StressTestResult), f"{key} is not a StressTestResult"


class TestCustomScenario:
    """Tests for user-defined StressScenario objects."""

    def test_custom_scenario_works(self) -> None:
        """A custom StressScenario is applied correctly."""
        custom = StressScenario(
            name="Custom Test",
            shock_return=-0.15,
            shock_duration_days=20,
            recovery_days=60,
            description="Custom 15% drawdown",
        )
        result = run_stress_test(DUMMY_RETURNS, custom, initial_value=1000.0)
        assert abs(result.trough_return - (-0.15)) < 1e-10
        assert result.scenario_name == "Custom Test"
