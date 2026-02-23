"""Main CLI entry point for Finbot."""

from __future__ import annotations

import os
from pathlib import Path

import click

from finbot.cli.commands import backtest, dashboard, optimize, simulate, status, update
from finbot.config import logger
from finbot.libs.logger.audit import generate_trace_id, set_trace_id


def _get_disclaimer_text() -> str:
    """Return shortened disclaimer text for CLI display."""
    return """
╔══════════════════════════════════════════════════════════════════════════════╗
║                              IMPORTANT DISCLAIMER                            ║
╚══════════════════════════════════════════════════════════════════════════════╝

Finbot is for EDUCATIONAL AND RESEARCH PURPOSES ONLY.

⚠️  NOT FINANCIAL ADVICE: This software does not provide financial, investment,
    or medical advice. Do not use it as a substitute for professional guidance.

⚠️  PAST PERFORMANCE: Historical results do not predict future returns.
    You may lose money. Strategies that worked historically may fail.

⚠️  NO WARRANTY: Provided "AS IS" without any warranty. Results may contain
    errors, omissions, or inaccuracies. Use at your own risk.

⚠️  CONSULT PROFESSIONALS: Always consult qualified financial advisors, tax
    professionals, and healthcare providers before making important decisions.

⚠️  YOUR RESPONSIBILITY: You are solely responsible for your decisions and
    any losses you incur. The authors assume NO LIABILITY for your use.

📄 Read the full disclaimer: DISCLAIMER.md
   https://github.com/jerdaw/finbot/blob/main/DISCLAIMER.md

By using this software, you acknowledge and accept all risks and limitations.
"""


def _check_first_run() -> bool:
    """Check if this is the first run by looking for a marker file."""
    marker_path = Path.home() / ".finbot" / ".disclaimer_accepted"
    return not marker_path.exists()


def _mark_disclaimer_shown() -> None:
    """Create marker file to indicate disclaimer has been shown."""
    marker_dir = Path.home() / ".finbot"
    marker_dir.mkdir(parents=True, exist_ok=True)
    marker_path = marker_dir / ".disclaimer_accepted"
    marker_path.write_text(f"Disclaimer shown at: {Path.cwd()}\n")


def _show_disclaimer() -> None:
    """Display the disclaimer notice."""
    click.echo(_get_disclaimer_text())


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
@click.option(
    "--disclaimer",
    is_flag=True,
    help="Display the full disclaimer notice",
)
@click.pass_context
def cli(ctx: click.Context, verbose: bool, trace_id: str | None, disclaimer: bool) -> None:
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

    # Show disclaimer if explicitly requested or on first run
    if disclaimer:
        _show_disclaimer()
        ctx.exit()
    elif _check_first_run() and not os.getenv("FINBOT_SKIP_DISCLAIMER"):
        _show_disclaimer()
        _mark_disclaimer_shown()
        click.echo("\nTo see this disclaimer again, run: finbot --disclaimer [COMMAND]\n")


# Register commands
cli.add_command(simulate)
cli.add_command(backtest)
cli.add_command(optimize)
cli.add_command(update)
cli.add_command(status)
cli.add_command(dashboard)


if __name__ == "__main__":
    cli()
