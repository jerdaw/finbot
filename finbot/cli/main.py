"""Main CLI entry point for Finbot."""

from __future__ import annotations

import click

from finbot.cli.commands import backtest, optimize, simulate, update
from finbot.config import logger


@click.group()
@click.version_option(version="1.0.0", prog_name="finbot")
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose logging output",
)
@click.pass_context
def cli(ctx: click.Context, verbose: bool) -> None:
    """Finbot - Financial simulation and backtesting platform.

    \b
    Available commands:
      simulate   Run fund, bond, or Monte Carlo simulations
      backtest   Execute strategy backtests
      optimize   Run portfolio optimization (DCA, rebalance)
      update     Run daily data update pipeline

    \b
    Examples:
      finbot simulate --fund UPRO --start 2020-01-01
      finbot backtest --strategy Rebalance --asset SPY
      finbot optimize --method dca --assets SPY,TLT
      finbot update --dry-run
    """
    # Store verbose flag in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose

    if verbose:
        logger.info("Verbose mode enabled")


# Register commands
cli.add_command(simulate)
cli.add_command(backtest)
cli.add_command(optimize)
cli.add_command(update)


if __name__ == "__main__":
    cli()
