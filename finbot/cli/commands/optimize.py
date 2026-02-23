"""Optimize command for running portfolio optimization."""

from __future__ import annotations

import click
import pandas as pd

from finbot.cli.utils.output import save_output
from finbot.cli.validators import POSITIVE_FLOAT, TICKER
from finbot.config import logger
from finbot.libs.logger.audit import audit_operation


@click.command()
@click.option(
    "--method",
    type=click.Choice(["dca"], case_sensitive=False),
    required=True,
    help="Optimization method (currently: dca)",
)
@click.option(
    "--asset",
    type=TICKER,
    required=True,
    help="Asset ticker to optimize (e.g., SPY, QQQ)",
)
@click.option(
    "--cash",
    type=POSITIVE_FLOAT,
    default=1000.0,
    show_default=True,
    help="Starting cash amount (must be positive)",
)
@click.option(
    "--output",
    type=click.Path(),
    help="Output file path for optimization results (CSV, parquet, or JSON)",
)
@click.option(
    "--plot",
    is_flag=True,
    help="Display matplotlib plots of optimization results",
)
@click.pass_context
def optimize(  # noqa: C901 - CLI command handlers are inherently complex
    ctx: click.Context,
    method: str,
    asset: str,
    cash: float,
    output: str | None,
    plot: bool,
) -> None:
    """Run portfolio optimization.

    \b
    Finds optimal DCA (Dollar Cost Averaging) schedules for an asset.
    Tests different front-loading ratios, DCA durations, purchase intervals,
    and trial durations to find the schedule that maximizes risk-adjusted returns.

    \b
    DCA Optimization Parameters (automatic):
      - Ratio range: 1x to 10x front-loading of purchases
      - DCA durations: 1 day to 3 years
      - Purchase intervals: daily to quarterly
      - Trial durations: 3 and 5 years

    \b
    Examples:
      finbot optimize --method dca --asset SPY
      finbot optimize --method dca --asset QQQ --cash 5000 --plot
      finbot optimize --method dca --asset UPRO --output results.csv
    """
    verbose = ctx.obj.get("verbose", False)
    parameters = {
        "method": method,
        "asset": asset,
        "cash": cash,
        "output": output,
        "plot": plot,
        "verbose": verbose,
        "trace_id": ctx.obj.get("trace_id"),
    }

    with audit_operation(
        logger,
        operation="optimize",
        component="cli.optimize",
        parameters=parameters,
    ):
        if verbose:
            logger.info(f"Starting {method.upper()} optimization for {asset}")

        if method.lower() == "dca":
            # Load price data
            try:
                from finbot.utils.data_collection_utils.yfinance.get_history import (
                    get_history,
                )

                click.echo(f"Loading price data for {asset}...")
                price_df = get_history(asset, adjust_price=True)

                if len(price_df) == 0:
                    click.echo("Error: Could not load price data", err=True)
                    raise click.Abort from None

                # Extract Close prices as a Series for the optimizer
                price_series = price_df["Close"]

                if verbose:
                    logger.info(f"Loaded {len(price_series)} data points for {asset}")

            except Exception as e:
                logger.error(f"Failed to load price data: {e}")
                click.echo(f"Error: Could not load price data: {e}", err=True)
                raise click.Abort from e

            # Run DCA optimization
            try:
                from finbot.services.optimization.dca_optimizer import (
                    analyze_results_helper,
                    dca_optimizer,
                )

                click.echo("Running DCA optimization...")
                click.echo(f"  Asset: {asset}")
                click.echo(f"  Starting cash: ${cash:,.2f}")
                click.echo("  This may take a while for large datasets...")

                # Get raw results (don't auto-analyze so we control plotting)
                raw_result = dca_optimizer(
                    price_history=price_series,
                    ticker=asset,
                    starting_cash=cash,
                    save_df=False,
                    analyze_results=False,
                )
                assert isinstance(raw_result, pd.DataFrame)
                raw_df = raw_result

                if verbose:
                    logger.info(f"Optimization complete: {len(raw_df)} trial results")

                # Analyze results
                ratio_df, duration_df = analyze_results_helper(raw_df, plot=plot)

                # Display ratio analysis
                click.echo("\nOptimization Results by DCA Ratio (front-loading):")
                for ratio_val in ratio_df.index:
                    row = ratio_df.loc[ratio_val]
                    click.echo(
                        f"  Ratio {ratio_val:.1f}x: "
                        f"Sharpe={row.iloc[0]:.4f}, "
                        f"CAGR={row.iloc[1]:.2f}%, "
                        f"Max DD={row.iloc[3]:.2f}%"
                    )

                # Display duration analysis
                click.echo("\nOptimization Results by DCA Duration (trading days):")
                for dur_val in duration_df.index:
                    row = duration_df.loc[dur_val]
                    click.echo(
                        f"  {dur_val:>5} days: Sharpe={row.iloc[0]:.4f}, CAGR={row.iloc[1]:.2f}%, Max DD={row.iloc[3]:.2f}%"
                    )

                # Save output if requested
                if output:
                    save_output(raw_df, output, verbose=verbose)

            except Exception as e:
                logger.error(f"Optimization failed: {e}")
                click.echo(f"Error: Optimization failed: {e}", err=True)
                if verbose:
                    import traceback

                    traceback.print_exc()
                raise click.Abort from e

        else:
            click.echo(f"Error: Unknown optimization method '{method}'", err=True)
            raise click.Abort from None
