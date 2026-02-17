"""Test NautilusTrader installation and basic functionality.

This script verifies that NautilusTrader is installed correctly and can be imported.
Run this after installing dependencies with `uv sync`.

Usage:
    uv run python scripts/test_nautilus_install.py
"""

from __future__ import annotations


def test_import():
    """Test that nautilus_trader can be imported."""
    print("Step 1: Testing import...")
    try:
        import nautilus_trader

        print("✅ NautilusTrader imported successfully!")
        print(f"   Version: {nautilus_trader.__version__}")
        return True
    except ImportError as e:
        print(f"❌ Failed to import nautilus_trader: {e}")
        print("   Run: uv sync")
        return False


def test_basic_objects():
    """Test that basic Nautilus objects can be created."""
    print("\nStep 2: Testing basic object creation...")
    try:
        from nautilus_trader.backtest.engine import BacktestEngine
        from nautilus_trader.model.identifiers import Venue

        # Create engine
        _ = BacktestEngine()
        print("✅ BacktestEngine created")

        # Create venue
        venue = Venue("SIM")
        print(f"✅ Venue created: {venue}")

        return True
    except Exception as e:
        print(f"❌ Failed to create basic objects: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_adapter():
    """Test that our NautilusAdapter can be imported."""
    print("\nStep 3: Testing our adapter...")
    try:
        from finbot.adapters.nautilus import NautilusAdapter

        adapter = NautilusAdapter()
        print("✅ NautilusAdapter created")
        print(f"   Name: {adapter.name}")
        print(f"   Version: {adapter.version}")
        print(f"   Simulator ID: {adapter.simulator_id if hasattr(adapter, 'simulator_id') else 'N/A'}")
        return True
    except Exception as e:
        print(f"❌ Failed to create adapter: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("NautilusTrader Installation Test")
    print("=" * 60)

    results = []

    # Test 1: Import
    results.append(("Import", test_import()))

    # Test 2: Basic objects (only if import succeeded)
    if results[0][1]:
        results.append(("Basic Objects", test_basic_objects()))
    else:
        print("\n⏭️  Skipping remaining tests (import failed)")
        results.append(("Basic Objects", None))

    # Test 3: Our adapter (only if basic objects succeeded)
    if len(results) > 1 and results[1][1]:
        results.append(("Adapter", test_adapter()))
    elif len(results) > 1:
        print("\n⏭️  Skipping adapter test (basic objects failed)")
        results.append(("Adapter", None))

    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    for name, passed in results:
        if passed is None:
            status = "⏭️  SKIPPED"
        elif passed:
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        print(f"{status} - {name}")

    # Overall result
    print("\n" + "=" * 60)
    if all(r[1] for r in results if r[1] is not None):
        print("✅ ALL TESTS PASSED")
        print("\nNext steps:")
        print("1. Read: docs/planning/e6-t1-implementation-guide.md")
        print("2. Start implementing the adapter TODOs")
        print("3. Create a backtest test script")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("\nTroubleshooting:")
        print("1. Make sure you ran: uv sync")
        print("2. Check Python version: python --version (should be 3.12-3.14)")
        print("3. Check for error messages above")
        return 1


if __name__ == "__main__":
    exit(main())
