"""Run a minimal backtest through NautilusAdapter.

This script runs a simple backtest and reports any remaining adapter functionality
that must be implemented before the smoke test can complete.

Usage:
    uv run python scripts/test_nautilus_backtest.py
"""

from __future__ import annotations

import pandas as pd

from finbot.adapters.nautilus import NautilusAdapter
from finbot.core.contracts.models import BacktestRunRequest


def create_minimal_test_data() -> dict[str, pd.DataFrame]:
    """Create minimal test data for backtesting.

    Returns:
        Dict mapping symbol to OHLCV DataFrame
    """
    # Create 5 days of simple price data
    dates = pd.date_range("2020-01-02", periods=5, freq="D")

    spy_data = pd.DataFrame(
        {
            "Open": [100.0, 101.0, 102.0, 103.0, 104.0],
            "High": [102.0, 103.0, 104.0, 105.0, 106.0],
            "Low": [99.0, 100.0, 101.0, 102.0, 103.0],
            "Close": [101.0, 102.0, 103.0, 104.0, 105.0],
            "Volume": [1000000, 1100000, 1200000, 1300000, 1400000],
        },
        index=dates,
    )

    return {"SPY": spy_data}


def create_test_request() -> BacktestRunRequest:
    """Create a minimal backtest request.

    Returns:
        BacktestRunRequest for testing
    """
    request = BacktestRunRequest(
        strategy_name="test_strategy",
        symbols=("SPY",),  # tuple, not list
        start=pd.Timestamp("2020-01-02"),
        end=pd.Timestamp("2020-01-06"),
        initial_cash=100000.0,  # float, not Decimal
        parameters={},  # Empty for now
    )

    return request


def main():
    """Run the smoke test."""
    print("=" * 60)
    print("NautilusTrader backtest smoke test")
    print("=" * 60)
    print()
    print("This check reports the next missing adapter capability if the run cannot complete.")
    print()

    # Create adapter
    print("Step 1: Creating NautilusAdapter...")
    adapter = NautilusAdapter(price_histories=create_minimal_test_data())
    print(f"Created adapter: {adapter.name} v{adapter.version}")
    print()

    # Create request
    print("Step 2: Creating backtest request...")
    request = create_test_request()
    print("Created request:")
    print(f"   Strategy: {request.strategy_name}")
    print(f"   Symbols: {request.symbols}")
    print(f"   Period: {request.start} to {request.end}")
    print(f"   Initial cash: ${request.initial_cash:,}")
    print()

    # Try to run backtest
    print("Step 3: Running backtest...")
    print("=" * 60)
    try:
        result = adapter.run_backtest(request)

        # If we get here, the backtest completed.
        print("=" * 60)
        print()
        print("BACKTEST COMPLETED")
        print()
        print("Results:")
        print(f"  Final value: ${result.metrics['final_value']:,}")
        print(f"  Total return: {result.metrics['total_return_pct']:.2f}%")
        print(f"  Engine: {result.metadata.engine_name}")
        print(f"  Engine version: {result.metadata.engine_version}")
        print()
        print("Next step: Compare these results with Backtrader for parity testing")
        return 0

    except NotImplementedError as e:
        print("=" * 60)
        print()
        print("NotImplementedError encountered")
        print()
        print(f"Error message: {e}")
        print()
        print("This identifies the next adapter capability to implement.")
        print()
        print("Next steps:")
        print("1. Find the related missing implementation in finbot/adapters/nautilus/nautilus_adapter.py")
        print("2. Implement the missing functionality")
        print("3. Run this test again")
        print("4. Repeat until the smoke test completes")
        print()
        return 1

    except Exception as e:
        print("=" * 60)
        print()
        print("Unexpected error encountered")
        print()
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {e}")
        print()
        print("Stack trace:")
        import traceback

        traceback.print_exc()
        print()
        return 1


if __name__ == "__main__":
    exit(main())
