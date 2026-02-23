"""Simulate command for running fund/bond/Monte Carlo simulations."""

from __future__ import annotations

import click
import pandas as pd

from finbot.cli.utils.output import save_output
from finbot.cli.validators import DATE, TICKER
from finbot.config import logger
from finbot.libs.logger.audit import audit_operation


@click.command()
@click.option(
    "--fund",
    type=TICKER,
    help="Fund ticker to simulate (e.g., UPRO, TQQQ, TMF)",
)
@click.option(
    "--start",
    type=DATE,
    help="Start date (YYYY-MM-DD format, e.g., 2020-01-15)",
)
@click.option(
    "--end",
    type=DATE,
    help="End date (YYYY-MM-DD format, e.g., 2024-12-31)",
)
@click.option(
    "--output",
    type=click.Path(),
    help="Output file path (CSV, parquet, or JSON)",
)
@click.option(
    "--plot",
    is_flag=True,
    help="Display interactive plot of simulation results",
)
@click.pass_context
def simulate(  # noqa: C901 - CLI command handlers are inherently complex
    ctx: click.Context,
    fund: str | None,
    start: str | None,
    end: str | None,
    output: str | None,
    plot: bool,
) -> None:
    """Run fund simulations.

    \b
    Simulates leveraged ETF performance using underlying index data.
    Supports all funds in sim_specific_funds.py (SPY, SSO, UPRO, QQQ,
    QLD, TQQQ, TLT, UBT, TMF, IEF, UST, TYD, SHY, etc.).

    \b
    Examples:
      finbot simulate --fund UPRO
      finbot simulate --fund TQQQ --start 2020-01-01 --output results.csv
      finbot simulate --fund TMF --plot
    """
    verbose = ctx.obj.get("verbose", False)

    if not fund:
        click.echo("Error: --fund is required", err=True)
        click.echo("Example: finbot simulate --fund UPRO", err=True)
        raise click.Abort from None

    fund = fund.upper()
    parameters = {
        "fund": fund,
        "start": start,
        "end": end,
        "output": output,
        "plot": plot,
        "verbose": verbose,
        "trace_id": ctx.obj.get("trace_id"),
    }

    with audit_operation(
        logger,
        operation="simulate",
        component="cli.simulate",
        parameters=parameters,
    ):
        if verbose:
            logger.info(f"Starting simulation for {fund}")

        # Import simulation function
        try:
            from finbot.services.simulation import sim_specific_funds

            sim_function_name = f"sim_{fund.lower()}"
            if not hasattr(sim_specific_funds, sim_function_name):
                available_funds = [
                    name.replace("sim_", "").upper()
                    for name in dir(sim_specific_funds)
                    if name.startswith("sim_") and not name.startswith("sim__")
                ]
                click.echo(f"Error: Unknown fund '{fund}'", err=True)
                click.echo(f"Available funds: {', '.join(sorted(available_funds))}", err=True)
                raise click.Abort from None

            sim_function = getattr(sim_specific_funds, sim_function_name)

        except ImportError as e:
            logger.error(f"Failed to import simulation module: {e}")
            click.echo(f"Error: Could not load simulation module: {e}", err=True)
            raise click.Abort from e

        # Run simulation
        try:
            click.echo(f"Simulating {fund}...")
            result = sim_function()

            # Filter by date range if specified
            if start:
                result = result[result.index >= pd.Timestamp(start)]
            if end:
                result = result[result.index <= pd.Timestamp(end)]

            if verbose:
                logger.info(f"Simulation complete: {len(result)} data points")

            # Display summary
            if len(result) > 0:
                first_date = result.index[0].strftime("%Y-%m-%d")
                last_date = result.index[-1].strftime("%Y-%m-%d")
                first_price = result["Close"].iloc[0]
                last_price = result["Close"].iloc[-1]
                total_return = ((last_price / first_price) - 1) * 100

                click.echo(f"\nSimulation Results for {fund}:")
                click.echo(f"  Period: {first_date} to {last_date}")
                click.echo(f"  Data points: {len(result):,}")
                click.echo(f"  Starting price: ${first_price:.2f}")
                click.echo(f"  Ending price: ${last_price:.2f}")
                click.echo(f"  Total return: {total_return:+.2f}%")

            # Save output if requested
            if output:
                save_output(result, output, verbose=verbose)

            # Plot if requested
            if plot:
                try:
                    import plotly.graph_objects as go

                    fig = go.Figure()
                    fig.add_trace(
                        go.Scatter(
                            x=result.index,
                            y=result["Close"],
                            mode="lines",
                            name=fund,
                            line={"color": "blue", "width": 2},
                        )
                    )
                    fig.update_layout(
                        title=f"{fund} Simulated Price History",
                        xaxis_title="Date",
                        yaxis_title="Price ($)",
                        hovermode="x unified",
                        height=600,
                    )
                    fig.show()

                except ImportError:
                    click.echo("Warning: plotly not available for plotting", err=True)

        except Exception as e:
            logger.error(f"Simulation failed: {e}")
            click.echo(f"Error: Simulation failed: {e}", err=True)
            if verbose:
                import traceback

                traceback.print_exc()
            raise click.Abort from e
