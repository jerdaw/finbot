"""Main CLI entry point for Finbot."""

from __future__ import annotations

import click

from finbot.cli.commands import backtest, dashboard, optimize, simulate, status, update
from finbot.config import logger
from finbot.libs.logger.audit import generate_trace_id, set_trace_id


@click.group()
@click.version_option(version="1.0.0", prog_name="finbot")
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose logging output",
)
@click.option(
    "--trace-id",
    type=str,
    default=None,
    help="Optional trace ID for structured audit logs (auto-generated when omitted)",
)
@click.pass_context
def cli(ctx: click.Context, verbose: bool, trace_id: str | None) -> None:
    """Finbot - Financial simulation and backtesting platform.

    Disclaimer: Research/education use only. See DISCLAIMER.md.

    \b
    Available commands:
      simulate   Run fund, bond, or Monte Carlo simulations
      backtest   Execute strategy backtests
      optimize   Run portfolio optimization (DCA, rebalance)
      update     Run daily data update pipeline
      status     Show data freshness and pipeline health
      dashboard  Launch the Streamlit web dashboard

    \b
    Examples:
      finbot simulate --fund UPRO --start 2020-01-01
      finbot backtest --strategy Rebalance --asset SPY
      finbot optimize --method dca --asset SPY
      finbot update --dry-run
      finbot dashboard --port 8501
    """
    # Store verbose flag in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["trace_id"] = trace_id or generate_trace_id()
    set_trace_id(ctx.obj["trace_id"])

    if verbose:
        logger.info("Verbose mode enabled", extra={"trace_id": ctx.obj["trace_id"]})


# Register commands
cli.add_command(simulate)
cli.add_command(backtest)
cli.add_command(optimize)
cli.add_command(update)
cli.add_command(status)
cli.add_command(dashboard)


if __name__ == "__main__":
    cli()
