"""Optimize command for running portfolio optimization."""

from __future__ import annotations

import click
import numpy as np

from finbot.cli.utils.output import save_output
from finbot.config import logger


@click.command()
@click.option(
    "--method",
    type=click.Choice(["dca"], case_sensitive=False),
    required=True,
    help="Optimization method (currently: dca)",
)
@click.option(
    "--assets",
    type=str,
    required=True,
    help="Comma-separated asset tickers (e.g., SPY,TLT)",
)
@click.option(
    "--duration",
    type=int,
    default=10,
    help="Investment duration in years (default: 10)",
)
@click.option(
    "--interval",
    type=click.Choice(["monthly", "quarterly"], case_sensitive=False),
    default="monthly",
    help="Purchase interval (default: monthly)",
)
@click.option(
    "--ratios",
    type=str,
    help="Allocation ratios to test (e.g., 0.5,0.6,0.7,0.8,0.9)",
)
@click.option(
    "--output",
    type=click.Path(),
    help="Output file path for optimization results (CSV, parquet, or JSON)",
)
@click.option(
    "--plot",
    is_flag=True,
    help="Display interactive plot of optimization results",
)
@click.pass_context
def optimize(  # noqa: C901 - CLI command handlers are inherently complex
    ctx: click.Context,
    method: str,
    assets: str,
    duration: int,
    interval: str,
    ratios: str | None,
    output: str | None,
    plot: bool,
) -> None:
    """Run portfolio optimization.

    \b
    Finds optimal asset allocation ratios using various optimization methods.
    Currently supports DCA (Dollar Cost Averaging) optimization.

    \b
    DCA Optimization:
      Tests different allocation ratios across two assets to find
      the combination that maximizes risk-adjusted returns (Sharpe ratio).

    \b
    Examples:
      finbot optimize --method dca --assets SPY,TLT
      finbot optimize --method dca --assets UPRO,TMF --duration 15
      finbot optimize --method dca --assets SPY,TQQQ --ratios 0.6,0.7,0.8 --plot
    """
    verbose = ctx.obj.get("verbose", False)

    # Parse assets
    asset_list = [a.strip().upper() for a in assets.split(",")]
    if len(asset_list) != 2:
        click.echo("Error: Exactly 2 assets required for optimization", err=True)
        click.echo("Example: --assets SPY,TLT", err=True)
        raise click.Abort from None

    asset1, asset2 = asset_list

    if verbose:
        logger.info(f"Starting {method.upper()} optimization: {asset1}/{asset2}")

    if method.lower() == "dca":
        # Parse ratios
        if ratios:
            try:
                ratio_values = [float(r.strip()) for r in ratios.split(",")]
                ratio_array = np.array(ratio_values)
            except ValueError:
                click.echo("Error: Invalid ratio format", err=True)
                click.echo("Example: --ratios 0.5,0.6,0.7,0.8,0.9", err=True)
                raise click.Abort from None
        else:
            # Default: test ratios from 50% to 95% in 5% increments
            ratio_array = np.arange(0.5, 1.0, 0.05)

        # Load price data
        try:
            from finbot.utils.data_collection_utils.yfinance.get_history import (
                get_history,
            )

            click.echo(f"Loading price data for {asset1} and {asset2}...")
            asset1_data = get_history(asset1, adjust_price=True)
            asset2_data = get_history(asset2, adjust_price=True)

            if len(asset1_data) == 0 or len(asset2_data) == 0:
                click.echo("Error: Could not load price data", err=True)
                raise click.Abort from None

            if verbose:
                logger.info(f"Loaded {len(asset1_data)} data points for {asset1}")
                logger.info(f"Loaded {len(asset2_data)} data points for {asset2}")

        except Exception as e:
            logger.error(f"Failed to load price data: {e}")
            click.echo(f"Error: Could not load price data: {e}", err=True)
            raise click.Abort from e

        # Run DCA optimization
        try:
            from finbot.services.optimization.dca_optimizer import DCAOptimizer

            click.echo("Running DCA optimization...")
            click.echo(f"  Duration: {duration} years")
            click.echo(f"  Interval: {interval}")
            click.echo(f"  Testing {len(ratio_array)} allocation ratios")

            optimizer = DCAOptimizer(
                asset1_data=asset1_data,
                asset2_data=asset2_data,
                asset1_name=asset1,
                asset2_name=asset2,
            )

            results = optimizer.optimize(ratios=ratio_array, duration_years=duration, interval=interval)

            if verbose:
                logger.info(f"Optimization complete: {len(results)} results")

            # Find optimal by Sharpe ratio
            best_idx = results["sharpe"].idxmax()
            optimal = results.loc[best_idx]

            click.echo("\nOptimization Results:")
            click.echo(f"  Method: {method.upper()}")
            click.echo(f"  Assets: {asset1} / {asset2}")
            click.echo("\nOptimal Allocation (by Sharpe Ratio):")
            click.echo(f"  {asset1}: {optimal['ratio']:.1%}")
            click.echo(f"  {asset2}: {1 - optimal['ratio']:.1%}")
            click.echo("\nPerformance Metrics:")
            click.echo(f"  CAGR: {optimal['cagr']:.2f}%")
            click.echo(f"  Sharpe Ratio: {optimal['sharpe']:.2f}")
            click.echo(f"  Max Drawdown: {optimal['max_drawdown']:.2f}%")
            click.echo(f"  Std Deviation: {optimal['std_dev']:.2f}%")

            # Save output if requested
            if output:
                save_output(results, output, verbose=verbose)

            # Plot if requested
            if plot:
                try:
                    import plotly.graph_objects as go
                    from plotly.subplots import make_subplots

                    fig = make_subplots(
                        rows=2,
                        cols=2,
                        subplot_titles=[
                            "CAGR vs Allocation",
                            "Sharpe Ratio vs Allocation",
                            "Max Drawdown vs Allocation",
                            "Std Dev vs Allocation",
                        ],
                    )

                    # CAGR
                    fig.add_trace(
                        go.Scatter(
                            x=results["ratio"] * 100,
                            y=results["cagr"],
                            mode="lines+markers",
                            name="CAGR",
                        ),
                        row=1,
                        col=1,
                    )

                    # Sharpe Ratio
                    fig.add_trace(
                        go.Scatter(
                            x=results["ratio"] * 100,
                            y=results["sharpe"],
                            mode="lines+markers",
                            name="Sharpe",
                        ),
                        row=1,
                        col=2,
                    )

                    # Max Drawdown (absolute value)
                    fig.add_trace(
                        go.Scatter(
                            x=results["ratio"] * 100,
                            y=results["max_drawdown"].abs(),
                            mode="lines+markers",
                            name="Max DD",
                        ),
                        row=2,
                        col=1,
                    )

                    # Std Dev
                    fig.add_trace(
                        go.Scatter(
                            x=results["ratio"] * 100,
                            y=results["std_dev"],
                            mode="lines+markers",
                            name="Std Dev",
                        ),
                        row=2,
                        col=2,
                    )

                    fig.update_xaxes(title_text=f"{asset1} Allocation (%)")
                    fig.update_yaxes(title_text="CAGR (%)", row=1, col=1)
                    fig.update_yaxes(title_text="Sharpe Ratio", row=1, col=2)
                    fig.update_yaxes(title_text="Max DD (%)", row=2, col=1)
                    fig.update_yaxes(title_text="Std Dev (%)", row=2, col=2)

                    fig.update_layout(
                        title_text=f"DCA Optimization: {asset1}/{asset2}",
                        height=800,
                        showlegend=False,
                    )

                    fig.show()

                except ImportError:
                    click.echo("Warning: plotly not available for plotting", err=True)

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
