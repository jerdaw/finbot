"""Unit tests for fund simulator."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def sample_underlying_data():
    """Create sample underlying price data."""
    dates = pd.date_range("2020-01-01", periods=252, freq="B")
    data = pd.DataFrame(
        {
            "Close": np.linspace(100, 150, 252),  # Steady growth
        },
        index=dates,
    )
    return data


@pytest.fixture
def sample_libor_data():
    """Create sample LIBOR data."""
    dates = pd.date_range("2020-01-01", periods=252, freq="B")
    data = pd.Series([0.05] * 252, index=dates)  # 5% annual rate
    return data


class TestFundSimulator:
    """Tests for fund_simulator function."""

    def test_fund_simulator_import(self):
        """Test that fund_simulator can be imported."""
        from finbot.services.simulation.fund_simulator import fund_simulator

        assert callable(fund_simulator)

    def test_fund_simulator_is_function(self):
        """Test that fund_simulator is a callable function."""
        from finbot.services.simulation.fund_simulator import fund_simulator

        assert callable(fund_simulator)


class TestComputeSimChanges:
    """Tests for _compute_sim_changes helper function (already tested in test_simulation_math.py)."""

    def test_compute_sim_changes_import(self):
        """Test that _compute_sim_changes can be imported."""
        from finbot.services.simulation.fund_simulator import _compute_sim_changes

        assert callable(_compute_sim_changes)


class TestApproximateOvernightLibor:
    """Tests for approximate_overnight_libor function."""

    def test_approximate_overnight_libor_import(self):
        """Test that approximate_overnight_libor can be imported."""
        from finbot.services.simulation.approximate_overnight_libor import approximate_overnight_libor

        assert callable(approximate_overnight_libor)

    def test_approximate_overnight_libor_is_function(self):
        """Test that approximate_overnight_libor is callable."""
        from finbot.services.simulation.approximate_overnight_libor import approximate_overnight_libor

        assert callable(approximate_overnight_libor)


class TestSimSpecificFunds:
    """Tests for specific fund simulation functions."""

    def test_sim_spy_import(self):
        """Test that sim_spy can be imported."""
        from finbot.services.simulation.sim_specific_funds import sim_spy

        assert callable(sim_spy)

    def test_sim_upro_import(self):
        """Test that sim_upro can be imported."""
        from finbot.services.simulation.sim_specific_funds import sim_upro

        assert callable(sim_upro)

    def test_sim_tqqq_import(self):
        """Test that sim_tqqq can be imported."""
        from finbot.services.simulation.sim_specific_funds import sim_tqqq

        assert callable(sim_tqqq)

    def test_sim_tlt_import(self):
        """Test that sim_tlt can be imported."""
        from finbot.services.simulation.sim_specific_funds import sim_tlt

        assert callable(sim_tlt)

    def test_sim_tmf_import(self):
        """Test that sim_tmf can be imported."""
        from finbot.services.simulation.sim_specific_funds import sim_tmf

        assert callable(sim_tmf)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
