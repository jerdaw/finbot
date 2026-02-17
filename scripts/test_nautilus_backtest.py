"""Test running a minimal backtest through NautilusAdapter.

This script attempts to run a simple backtest to identify what needs to be implemented.
Each NotImplementedError will tell us the next TODO to tackle.

Usage:
    uv run python scripts/test_nautilus_backtest.py
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

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
    data = create_minimal_test_data()

    request = BacktestRunRequest(
        strategy_name="test_strategy",
        symbols=["SPY"],
        data=data,
        start_date=datetime(2020, 1, 2),
        end_date=datetime(2020, 1, 6),
        initial_cash=Decimal("100000"),
        parameters={},  # Empty for now
    )

    return request


def main():
    """Run the test."""
    print("=" * 60)
    print("NautilusTrader Backtest Test")
    print("=" * 60)
    print()
    print("This test will show us what needs to be implemented next.")
    print("Each NotImplementedError tells us the next TODO.")
    print()

    # Create adapter
    print("Step 1: Creating NautilusAdapter...")
    adapter = NautilusAdapter()
    print(f"✅ Created adapter: {adapter.name} v{adapter.version}")
    print()

    # Create request
    print("Step 2: Creating backtest request...")
    request = create_test_request()
    print("✅ Created request:")
    print(f"   Strategy: {request.strategy_name}")
    print(f"   Symbols: {request.symbols}")
    print(f"   Period: {request.start_date.date()} to {request.end_date.date()}")
    print(f"   Initial cash: ${request.initial_cash:,}")
    print()

    # Try to run backtest
    print("Step 3: Running backtest...")
    print("=" * 60)
    try:
        result = adapter.run_backtest(request)

        # If we get here, the backtest completed!
        print("=" * 60)
        print()
        print("🎉 BACKTEST COMPLETED!")
        print()
        print("Results:")
        print(f"  Final value: ${result.final_value:,}")
        print(f"  Total return: {result.total_return}%")
        print(f"  Engine: {result.metadata.engine}")
        print(f"  Engine version: {result.metadata.engine_version}")
        print()
        print("Next step: Compare these results with Backtrader for parity testing")
        return 0

    except NotImplementedError as e:
        print("=" * 60)
        print()
        print("❌ Hit a NotImplementedError (expected!)")
        print()
        print(f"Error message: {e}")
        print()
        print("This tells us what to implement next.")
        print()
        print("Next steps:")
        print("1. Find this TODO in finbot/adapters/nautilus/nautilus_adapter.py")
        print("2. Implement the missing functionality")
        print("3. Run this test again")
        print("4. Repeat until all TODOs are implemented")
        print()
        return 1

    except Exception as e:
        print("=" * 60)
        print()
        print("❌ Hit an unexpected error!")
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
