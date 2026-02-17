"""NautilusTrader adapter for engine-agnostic backtesting.

This adapter implements the BacktestEngine interface using NautilusTrader's
backtesting capabilities. It enables running backtests through the Nautilus
engine while maintaining compatibility with our typed contracts.

Status: PILOT - Minimal viable implementation for evaluation
"""

from finbot.adapters.nautilus.nautilus_adapter import NautilusAdapter

__all__ = ["NautilusAdapter"]
