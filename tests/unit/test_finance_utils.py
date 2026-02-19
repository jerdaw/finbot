"""Unit tests for finance utility functions."""

from __future__ import annotations

import pandas as pd
import pytest


class TestGetCGR:
    """Tests for get_cgr (compound growth rate) calculation."""

    def test_basic_cgr_calculation(self):
        """Test basic CGR with known values."""
        from finbot.utils.finance_utils.get_cgr import get_cgr

        # 10% annual growth over 5 years: 1.10^5 = 1.61051
        result = get_cgr(start_val=100, end_val=161.051, periods=5)
        assert round(result, 4) == 0.1000

    def test_cgr_one_period(self):
        """Test CGR with one period (simple growth)."""
        from finbot.utils.finance_utils.get_cgr import get_cgr

        result = get_cgr(start_val=100, end_val=110, periods=1)
        assert result == pytest.approx(0.10)

    def test_cgr_negative_growth(self):
        """Test CGR with negative growth."""
        from finbot.utils.finance_utils.get_cgr import get_cgr

        # 50% loss in 1 year
        result = get_cgr(start_val=100, end_val=50, periods=1)
        assert result == -0.5

    def test_cgr_multiple_periods(self):
        """Test CGR over multiple periods."""
        from finbot.utils.finance_utils.get_cgr import get_cgr

        # 20% total growth over 2 years: sqrt(1.2) - 1 ≈ 0.0954
        result = get_cgr(start_val=100, end_val=120, periods=2)
        assert round(result, 4) == 0.0954


class TestGetPctChange:
    """Tests for percentage change calculation."""

    def test_basic_pct_change(self):
        """Test basic percentage change."""
        from finbot.utils.finance_utils.get_pct_change import get_pct_change

        result = get_pct_change(start_val=100, end_val=110)
        assert result == 0.10

    def test_pct_change_negative(self):
        """Test percentage change with negative movement."""
        from finbot.utils.finance_utils.get_pct_change import get_pct_change

        result = get_pct_change(start_val=100, end_val=90)
        assert result == -0.10

    def test_pct_change_mult_by_100(self):
        """Test percentage change multiplied by 100."""
        from finbot.utils.finance_utils.get_pct_change import get_pct_change

        result = get_pct_change(start_val=100, end_val=110, mult_by_100=True)
        assert result == 10.0  # Returns 10 instead of 0.10

    def test_pct_change_allow_negative_false(self):
        """Test percentage change with allow_negative=False (absolute value)."""
        from finbot.utils.finance_utils.get_pct_change import get_pct_change

        # Negative change should become positive
        result = get_pct_change(start_val=100, end_val=90, allow_negative=False)
        assert result == 0.10  # Returns absolute value

    def test_pct_change_division_by_zero_returns_inf(self):
        """Test division by zero returns infinity when div_by_zero_error=False."""
        from finbot.utils.finance_utils.get_pct_change import get_pct_change

        result = get_pct_change(start_val=0, end_val=100, div_by_zero_error=False)
        assert result == float("inf")

    def test_pct_change_division_by_zero_raises_error(self):
        """Test division by zero raises error when div_by_zero_error=True."""
        from finbot.utils.finance_utils.get_pct_change import get_pct_change

        with pytest.raises(ZeroDivisionError, match="start_val cannot be zero"):
            get_pct_change(start_val=0, end_val=100, div_by_zero_error=True)


class TestGetDrawdown:
    """Tests for drawdown calculation."""

    def test_no_drawdown(self):
        """Test series with no drawdown (monotonic increase)."""
        from finbot.utils.finance_utils.get_drawdown import get_drawdown

        series = pd.Series([100, 110, 120, 130])
        result = get_drawdown(series)
        assert result.max() == 0.0  # No drawdown

    def test_simple_drawdown(self):
        """Test simple drawdown calculation."""
        from finbot.utils.finance_utils.get_drawdown import get_drawdown

        series = pd.Series([100, 120, 90, 110])  # Peak at 120, trough at 90
        result = get_drawdown(series)
        assert round(result.min(), 4) == -0.2500  # 25% drawdown from peak

    def test_drawdown_recovery(self):
        """Test drawdown that recovers."""
        from finbot.utils.finance_utils.get_drawdown import get_drawdown

        series = pd.Series([100, 120, 90, 120])  # Drop then recover
        result = get_drawdown(series)
        assert result.iloc[-1] == 0.0  # Recovered to 0 drawdown

    def test_drawdown_with_rolling_window(self):
        """Test drawdown with rolling window (window > 1)."""
        from finbot.utils.finance_utils.get_drawdown import get_drawdown

        series = pd.Series([100, 110, 105, 115, 100, 120])
        result = get_drawdown(series, window=3)

        # Should calculate drawdown from rolling 3-period max
        assert isinstance(result, pd.Series)
        assert len(result) == len(series)

    def test_drawdown_invalid_window_raises_error(self):
        """Test that window < 1 raises ValueError."""
        from finbot.utils.finance_utils.get_drawdown import get_drawdown

        series = pd.Series([100, 110, 120])

        with pytest.raises(ValueError, match="Window must be greater than 0"):
            get_drawdown(series, window=0)

    def test_drawdown_with_dataframe(self):
        """Test drawdown calculation with DataFrame input."""
        from finbot.utils.finance_utils.get_drawdown import get_drawdown

        df = pd.DataFrame({"Price": [100, 120, 90, 110]})
        result = get_drawdown(df["Price"])

        assert isinstance(result, pd.Series)
        assert round(result.min(), 4) == -0.2500  # 25% drawdown


class TestGetPeriodsPerYear:
    """Tests for detecting frequency from price data."""

    def test_daily_frequency(self):
        """Test detection of daily frequency."""
        from finbot.utils.finance_utils.get_periods_per_year import get_periods_per_year

        # Need at least a year of data
        dates = pd.date_range("2020-01-01", periods=400, freq="B")  # Business days
        df = pd.DataFrame({"Close": range(400)}, index=dates)
        result = get_periods_per_year(df)
        # Business days per year is approximately 252, but can vary
        assert 250 <= result <= 265

    def test_monthly_frequency(self):
        """Test detection of monthly frequency."""
        from finbot.utils.finance_utils.get_periods_per_year import get_periods_per_year

        # Need at least a year of data
        dates = pd.date_range("2020-01-01", periods=24, freq="ME")
        df = pd.DataFrame({"Close": range(24)}, index=dates)
        result = get_periods_per_year(df)
        # Monthly frequency should be 12 or close to it
        assert 11 <= result <= 13

    def test_weekly_frequency(self):
        """Test detection of weekly frequency."""
        from finbot.utils.finance_utils.get_periods_per_year import get_periods_per_year

        # Need at least a year of data
        dates = pd.date_range("2020-01-01", periods=100, freq="W")
        df = pd.DataFrame({"Close": range(100)}, index=dates)
        result = get_periods_per_year(df)
        # Weekly frequency should be 52 or close to it
        assert 50 <= result <= 54


class TestMergePriceHistories:
    """Tests for merging overlapping price histories."""

    def test_merge_function_exists(self):
        """Test that merge_price_histories function exists and is callable."""
        from finbot.utils.finance_utils.merge_price_histories import merge_price_histories

        assert callable(merge_price_histories)

    def test_merge_simple_case(self):
        """Test merging with simple overlapping case."""
        from finbot.utils.finance_utils.merge_price_histories import merge_price_histories

        # Create simple overlapping series
        dates1 = pd.date_range("2020-01-01", periods=10, freq="D")
        dates2 = pd.date_range("2020-01-05", periods=10, freq="D")

        older = pd.Series(range(100, 110), index=dates1)
        newer = pd.Series(range(200, 210), index=dates2)

        # Just verify it returns a Series without error
        result = merge_price_histories(older, newer, fix_point="end")
        assert isinstance(result, pd.Series)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
