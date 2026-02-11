"""Command-line interface for Finbot.

This module provides CLI access to all major Finbot functionality:
- Simulate: Run fund/bond/Monte Carlo simulations
- Backtest: Execute strategy backtests
- Optimize: Run DCA or rebalance optimization
- Update: Run daily data update pipeline
"""

from finbot.cli.main import cli

__all__ = ["cli"]
