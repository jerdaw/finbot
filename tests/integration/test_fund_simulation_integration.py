"""Integration tests for fund simulation workflows.

Tests end-to-end fund simulation including data loading, simulation execution,
and result validation.
"""

from __future__ import annotations

import pandas as pd
import pytest

from finbot.services.simulation.fund_simulator import fund_simulator


class TestFundSimulationIntegration:
    """Integration tests for complete fund simulation workflows."""

    def test_basic_fund_simulation(self, sample_spy_data):
        """Test basic fund simulation with SPY data."""
        # Simulate unleveraged fund (1x)
        result = fund_simulator(
            price_df=sample_spy_data,
            leverage_mult=1.0,
            annual_er_pct=0.1 / 100,  # 0.1% expense ratio
        )

        # Validate result
        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert "Close" in result.columns
        assert "Change" in result.columns
        assert len(result) == len(sample_spy_data)

        # Check that changes are calculated
        assert result["Change"].notna().any()

    def test_leveraged_fund_simulation_2x(self, sample_spy_data):
        """Test 2x leveraged fund simulation."""
        result = fund_simulator(
            price_df=sample_spy_data,
            leverage_mult=2.0,
            annual_er_pct=0.5 / 100,
            percent_daily_spread_cost=0.01 / 100,
        )

        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(sample_spy_data)

        # 2x leverage should amplify returns
        underlying_return = (sample_spy_data["Close"].iloc[-1] / sample_spy_data["Close"].iloc[0] - 1) * 100
        fund_return = (result["Close"].iloc[-1] / result["Close"].iloc[0] - 1) * 100

        # Fund return should be roughly 2x (accounting for costs)
        # Not exact due to daily rebalancing and compounding
        assert abs(fund_return) > abs(underlying_return) * 0.5  # At least somewhat amplified

    def test_leveraged_fund_simulation_3x(self, sample_spy_data):
        """Test 3x leveraged fund simulation."""
        result = fund_simulator(
            price_df=sample_spy_data,
            leverage_mult=3.0,
            annual_er_pct=0.95 / 100,
            percent_daily_spread_cost=0.015 / 100,
            fund_swap_pct=1.0,
        )

        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(sample_spy_data)

        # 3x leverage should have higher volatility, though not necessarily higher returns due to fees and decay
        underlying_changes = sample_spy_data["Close"].pct_change().dropna()
        fund_changes = result["Change"].dropna()

        # Volatility should be amplified (check standard deviation is higher)
        underlying_vol = underlying_changes.std()
        fund_vol = fund_changes.std()
        assert fund_vol > underlying_vol * 2.0, (
            f"Expected 3x fund volatility {fund_vol} > 2x underlying {underlying_vol * 2.0}"
        )

    def test_simulation_with_custom_libor(self, sample_spy_data, sample_libor_data):
        """Test simulation with custom LIBOR data."""
        result = fund_simulator(
            price_df=sample_spy_data,
            leverage_mult=3.0,
            annual_er_pct=0.95 / 100,
            libor_yield_df=sample_libor_data,
        )

        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(sample_spy_data)
        assert "Close" in result.columns

    def test_simulation_preserves_index(self, sample_spy_data):
        """Test that simulation preserves datetime index."""
        result = fund_simulator(
            price_df=sample_spy_data,
            leverage_mult=2.0,
        )

        assert isinstance(result.index, pd.DatetimeIndex)
        assert result.index.equals(sample_spy_data.index)

    def test_simulation_with_multiplicative_constant(self, sample_spy_data):
        """Test simulation with curve-fitting constants."""
        result = fund_simulator(
            price_df=sample_spy_data,
            leverage_mult=2.0,
            multiplicative_constant=1.05,
            additive_constant=0.0001,
        )

        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(sample_spy_data)

    def test_simulation_error_handling_missing_close(self):
        """Test error handling when Close column is missing."""
        # Create DataFrame without Close column
        dates = pd.date_range(start="2023-01-01", periods=10, freq="D")
        bad_df = pd.DataFrame({"Open": range(10), "High": range(10)}, index=dates)

        with pytest.raises(ValueError, match="Close"):
            fund_simulator(price_df=bad_df, leverage_mult=1.0)

    def test_simulation_error_handling_non_datetime_index(self):
        """Test error handling when index is not datetime."""
        bad_df = pd.DataFrame({"Close": range(10)}, index=range(10))

        with pytest.raises(ValueError, match="datetime"):
            fund_simulator(price_df=bad_df, leverage_mult=1.0)

    def test_multiple_funds_same_data(self, sample_spy_data):
        """Test simulating multiple leverage levels from same underlying."""
        leverage_levels = [1.0, 2.0, 3.0]
        results = {}

        for lev in leverage_levels:
            results[lev] = fund_simulator(
                price_df=sample_spy_data,
                leverage_mult=lev,
                annual_er_pct=0.5 / 100,
            )

        # All should have same length
        assert all(len(r) == len(sample_spy_data) for r in results.values())

        # Higher leverage should have more volatility in returns
        vol_1x = results[1.0]["Change"].std()
        vol_2x = results[2.0]["Change"].std()
        vol_3x = results[3.0]["Change"].std()

        assert vol_2x > vol_1x, "2x should have higher volatility than 1x"
        assert vol_3x > vol_2x, "3x should have higher volatility than 2x"


@pytest.mark.slow
class TestFundSimulationPerformance:
    """Performance tests for fund simulation (marked as slow)."""

    def test_simulation_large_dataset(self):
        """Test simulation performance with large dataset."""
        # Generate 10 years of data
        import numpy as np

        dates = pd.date_range(start="2014-01-01", periods=2520, freq="B")  # 10 years
        np.random.seed(42)
        returns = np.random.normal(0.0005, 0.01, 2520)
        prices = 400 * (1 + returns).cumprod()

        large_df = pd.DataFrame({"Close": prices, "Adj Close": prices}, index=dates)

        # Simulate - should complete in reasonable time
        import time

        start = time.time()
        result = fund_simulator(price_df=large_df, leverage_mult=3.0)
        duration = time.time() - start

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2520
        assert duration < 1.0, f"Simulation took {duration:.2f}s, expected <1s"
