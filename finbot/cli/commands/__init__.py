"""CLI command implementations."""

from finbot.cli.commands.backtest import backtest
from finbot.cli.commands.dashboard import dashboard
from finbot.cli.commands.optimize import optimize
from finbot.cli.commands.simulate import simulate
from finbot.cli.commands.status import status
from finbot.cli.commands.update import update

__all__ = ["backtest", "dashboard", "optimize", "simulate", "status", "update"]
