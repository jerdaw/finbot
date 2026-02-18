"""Integration tests for DCA optimizer workflows.

Tests end-to-end optimization including grid search, result aggregation,
and optimal parameter identification.

NOTE: These tests are currently skipped because they were written based on
incorrect assumptions about the dca_optimizer API. The actual dca_optimizer
takes a single price_history Series, not equity_data/bond_data DataFrames.
These tests need to be rewritten to match the actual API.
"""

from __future__ import annotations

import pandas as pd
import pytest

from finbot.services.optimization.dca_optimizer import dca_optimizer

from ..integration.conftest import assert_valid_optimization_results

pytestmark = pytest.mark.skip(
    reason="DCA optimizer tests need rewrite to match actual API (price_history, not equity_data/bond_data)"
)


class TestDCAOptimizerIntegration:
    """Integration tests for complete DCA optimization workflows."""

    def test_basic_dca_optimization(self, sample_spy_data):
        """Test basic DCA optimization with small parameter grid."""
        # Use small grid for fast testing
        results = dca_optimizer(
            equity_data=sample_spy_data,
            bond_data=None,  # Equity only
            ratios=[(1.0, 0.0)],  # 100% equity
            durations=[30, 60],  # Short durations
            intervals=[7, 14],  # Weekly, biweekly
            max_workers=1,  # Single-threaded for determinism
        )

        # Validate results
        assert_valid_optimization_results(results)

        # Should have 2 durations x 2 intervals = 4 trials
        assert len(results) == 4

        # Check for expected columns (lowercase CAGR, sharpe, etc.)
        assert any("cagr" in col.lower() for col in results.columns)
        assert any("sharpe" in col.lower() for col in results.columns)

    def test_dca_optimization_multi_ratio(self, sample_multi_asset_data):
        """Test DCA optimization with multiple asset allocation ratios."""
        spy_data = sample_multi_asset_data["SPY"]
        tlt_data = sample_multi_asset_data["TLT"]

        results = dca_optimizer(
            equity_data=spy_data,
            bond_data=tlt_data,
            ratios=[(1.0, 0.0), (0.6, 0.4), (0.4, 0.6)],  # 3 ratios
            durations=[30],  # Single duration
            intervals=[7],  # Single interval
            max_workers=1,
        )

        # Should have 3 trials (one per ratio)
        assert len(results) == 3

        # Results should vary by ratio
        returns = []
        for idx in results.index:
            if "cagr" in results.columns:
                returns.append(results.loc[idx, "cagr"])
            else:
                # Find CAGR column
                cagr_cols = [c for c in results.columns if "cagr" in c.lower()]
                if cagr_cols:
                    returns.append(results.loc[idx, cagr_cols[0]])

        if len(returns) == 3:
            # Returns should differ (not all identical)
            assert len(set(returns)) > 1, "Different ratios should produce different returns"

    def test_dca_optimization_finds_best_params(self, sample_spy_data):
        """Test that optimization identifies best parameters."""
        results = dca_optimizer(
            equity_data=sample_spy_data,
            bond_data=None,
            ratios=[(1.0, 0.0)],
            durations=[30, 60, 90],  # 3 durations
            intervals=[7, 14],  # 2 intervals
            max_workers=1,
        )

        # Should have 3 x 2 = 6 trials
        assert len(results) == 6

        # Should be able to identify best trial by some metric
        # (Exact metric column name may vary by implementation)
        cagr_cols = [c for c in results.columns if "cagr" in c.lower()]
        if cagr_cols:
            best_idx = results[cagr_cols[0]].idxmax()
            assert best_idx is not None

    def test_dca_optimization_result_structure(self, sample_spy_data):
        """Test that optimization results have expected structure."""
        results = dca_optimizer(
            equity_data=sample_spy_data,
            bond_data=None,
            ratios=[(1.0, 0.0)],
            durations=[30],
            intervals=[7],
            max_workers=1,
        )

        # Check DataFrame structure
        assert isinstance(results, pd.DataFrame)
        assert len(results) == 1

        # Should have parameter columns
        assert any(
            "ratio" in col.lower() or "duration" in col.lower() or "interval" in col.lower() for col in results.columns
        )

        # Should have metric columns
        metric_keywords = ["cagr", "sharpe", "drawdown", "volatility", "return"]
        has_metrics = any(any(keyword in col.lower() for keyword in metric_keywords) for col in results.columns)
        assert has_metrics, "Results should include performance metrics"

    def test_dca_optimization_parallel_execution(self, sample_spy_data):
        """Test DCA optimization with parallel workers."""
        # Skip if multiprocessing not available
        import multiprocessing

        if multiprocessing.cpu_count() < 2:
            pytest.skip("Requires multiple CPU cores")

        results = dca_optimizer(
            equity_data=sample_spy_data,
            bond_data=None,
            ratios=[(1.0, 0.0)],
            durations=[30, 60],
            intervals=[7, 14],
            max_workers=2,  # Parallel execution
        )

        # Should complete successfully
        assert len(results) == 4

    @pytest.mark.slow
    def test_dca_optimization_comprehensive_grid(self, sample_spy_data):
        """Test optimization with larger parameter grid (marked slow)."""
        results = dca_optimizer(
            equity_data=sample_spy_data,
            bond_data=None,
            ratios=[(1.0, 0.0)],
            durations=[30, 60, 90, 120],  # 4 durations
            intervals=[7, 14, 21],  # 3 intervals
            max_workers=2,
        )

        # Should have 4 x 3 = 12 trials
        assert len(results) == 12

        # All trials should have valid metrics
        assert_valid_optimization_results(results)


class TestDCAOptimizerErrorHandling:
    """Test error handling in DCA optimizer."""

    def test_optimization_with_insufficient_data(self):
        """Test optimization with very short data series."""
        # Create very short dataset
        short_data = pd.DataFrame(
            {"Close": [100, 101, 102]},
            index=pd.date_range("2023-01-01", periods=3, freq="D"),
        )

        # Should either handle gracefully or raise clear error
        try:
            results = dca_optimizer(
                equity_data=short_data,
                bond_data=None,
                ratios=[(1.0, 0.0)],
                durations=[10],  # Longer than data
                intervals=[7],
                max_workers=1,
            )
            # If it succeeds, results should be empty or have NaN values
            assert results is not None
        except (ValueError, IndexError, KeyError):
            # Expected - insufficient data
            pass

    def test_optimization_with_empty_parameters(self, sample_spy_data):
        """Test optimization with empty parameter lists."""
        # Empty ratios should fail or return empty results
        with pytest.raises((ValueError, TypeError)):
            dca_optimizer(
                equity_data=sample_spy_data,
                bond_data=None,
                ratios=[],  # Empty
                durations=[30],
                intervals=[7],
                max_workers=1,
            )
