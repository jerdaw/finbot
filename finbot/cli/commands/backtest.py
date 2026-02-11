"""Backtest command for running strategy backtests."""

from __future__ import annotations

import click
import pandas as pd

from config import logger
from finbot.cli.utils.output import save_output


@click.command()
@click.option(
    "--strategy",
    type=str,
    required=True,
    help="Strategy name (e.g., Rebalance, SMACrossover, MACDSingle)",
)
@click.option(
    "--asset",
    type=str,
    required=True,
    help="Asset ticker to backtest (e.g., SPY, QQQ)",
)
@click.option(
    "--start",
    type=str,
    help="Start date (YYYY-MM-DD format)",
)
@click.option(
    "--end",
    type=str,
    help="End date (YYYY-MM-DD format)",
)
@click.option(
    "--cash",
    type=float,
    default=100000.0,
    help="Initial cash amount (default: 100000)",
)
@click.option(
    "--commission",
    type=float,
    default=0.001,
    help="Commission rate (default: 0.001 = 0.1%)",
)
@click.option(
    "--output",
    type=click.Path(),
    help="Output file path for results (CSV, parquet, or JSON)",
)
@click.option(
    "--plot",
    is_flag=True,
    help="Display interactive plot of backtest results",
)
@click.pass_context
def backtest(  # noqa: C901 - CLI command handlers are inherently complex
    ctx: click.Context,
    strategy: str,
    asset: str,
    start: str | None,
    end: str | None,
    cash: float,
    commission: float,
    output: str | None,
    plot: bool,
) -> None:
    """Run strategy backtests.

    \b
    Tests trading strategies on historical data with realistic
    commissions and performance metrics.

    \b
    Available strategies:
      - Rebalance: Periodic portfolio rebalancing
      - NoRebalance: Buy and hold
      - SMACrossover: Single moving average crossover
      - SMACrossoverDouble: Dual moving average system
      - SMACrossoverTriple: Triple moving average cascade
      - MACDSingle: MACD indicator-based entries
      - MACDDual: Dual MACD timeframes
      - DipBuySMA: Buy dips relative to moving average
      - DipBuyStdev: Buy dips using standard deviation
      - SMARebalMix: Combined SMA timing + rebalancing

    \b
    Examples:
      finbot backtest --strategy Rebalance --asset SPY
      finbot backtest --strategy SMACrossover --asset QQQ --cash 50000
      finbot backtest --strategy MACDDual --asset SPY --output results.csv --plot
    """
    verbose = ctx.obj.get("verbose", False)

    if verbose:
        logger.info(f"Starting backtest: {strategy} on {asset}")

    # Import strategy
    try:
        from finbot.services.backtesting import strategies

        # Map strategy names to classes
        strategy_map = {
            "rebalance": strategies.rebalance.Rebalance,
            "norebalance": strategies.no_rebalance.NoRebalance,
            "smacrossover": strategies.sma_crossover.SMACrossover,
            "smacrossoverdouble": strategies.sma_crossover_double.SMACrossoverDouble,
            "smacrossovertriple": strategies.sma_crossover_triple.SMACrossoverTriple,
            "macdsingle": strategies.macd_single.MACDSingle,
            "macddual": strategies.macd_dual.MACDDual,
            "dipbuysma": strategies.dip_buy_sma.DipBuySMA,
            "dipbuystdev": strategies.dip_buy_stdev.DipBuyStdev,
            "smarebalmix": strategies.sma_rebal_mix.SMARebalMix,
        }

        strategy_key = strategy.lower().replace("_", "").replace("-", "")
        if strategy_key not in strategy_map:
            available = ", ".join(strategy_map.keys())
            click.echo(f"Error: Unknown strategy '{strategy}'", err=True)
            click.echo(f"Available strategies: {available}", err=True)
            raise click.Abort

        strategy_class = strategy_map[strategy_key]

    except (ImportError, AttributeError) as e:
        logger.error(f"Failed to import strategy: {e}")
        click.echo(f"Error: Could not load strategy '{strategy}': {e}", err=True)
        raise click.Abort from e

    # Load price data
    try:
        from finbot.utils.data_collection_utils.yfinance.get_history import get_history

        click.echo(f"Loading {asset} price data...")
        price_data = get_history(asset, adjust_price=True)

        # Filter by date range if specified
        if start:
            price_data = price_data[price_data.index >= pd.Timestamp(start)]
        if end:
            price_data = price_data[price_data.index <= pd.Timestamp(end)]

        if len(price_data) == 0:
            click.echo("Error: No data available for specified date range", err=True)
            raise click.Abort

        if verbose:
            logger.info(f"Loaded {len(price_data)} data points for {asset}")

    except Exception as e:
        logger.error(f"Failed to load price data: {e}")
        click.echo(f"Error: Could not load price data for {asset}: {e}", err=True)
        raise click.Abort from e

    # Run backtest
    try:
        from finbot.services.backtesting.backtest_runner import BacktestRunner

        click.echo(f"Running backtest: {strategy} on {asset}...")

        runner = BacktestRunner(strategy=strategy_class, data=price_data, cash=cash, commission=commission)

        results = runner.run()

        if verbose:
            logger.info("Backtest complete")

        # Display summary
        final_value = results.get("final_value", 0)
        total_return = results.get("total_return", 0)

        click.echo("\nBacktest Results:")
        click.echo(f"  Strategy: {strategy}")
        click.echo(f"  Asset: {asset}")
        click.echo(f"  Initial capital: ${cash:,.2f}")
        click.echo(f"  Final value: ${final_value:,.2f}")
        click.echo(f"  Total return: {total_return:+.2f}%")

        # Compute detailed statistics if available
        try:
            from finbot.services.backtesting.compute_stats import compute_stats

            if "portfolio_value" in results and "returns" in results:
                stats = compute_stats(
                    portfolio_values=results["portfolio_value"],
                    returns=results["returns"],
                )

                click.echo("\nPerformance Metrics:")
                if "cagr" in stats:
                    click.echo(f"  CAGR: {stats['cagr']:.2f}%")
                if "sharpe" in stats:
                    click.echo(f"  Sharpe Ratio: {stats['sharpe']:.2f}")
                if "sortino" in stats:
                    click.echo(f"  Sortino Ratio: {stats['sortino']:.2f}")
                if "max_drawdown" in stats:
                    click.echo(f"  Max Drawdown: {stats['max_drawdown']:.2f}%")
                if "win_rate" in stats:
                    click.echo(f"  Win Rate: {stats['win_rate']:.2f}%")

        except Exception as e:
            if verbose:
                logger.warning(f"Could not compute detailed statistics: {e}")

        # Save output if requested
        if output and "portfolio_value" in results:
            results_df = pd.DataFrame(
                {
                    "portfolio_value": results["portfolio_value"],
                    "returns": results.get("returns", []),
                }
            )
            save_output(results_df, output, verbose=verbose)

        # Plot if requested
        if plot and "portfolio_value" in results:
            try:
                import plotly.graph_objects as go

                portfolio_values = results["portfolio_value"]

                fig = go.Figure()
                fig.add_trace(
                    go.Scatter(
                        x=list(range(len(portfolio_values))),
                        y=portfolio_values,
                        mode="lines",
                        name="Portfolio Value",
                        line={"color": "green", "width": 2},
                    )
                )
                fig.update_layout(
                    title=f"Backtest Results: {strategy} on {asset}",
                    xaxis_title="Trading Days",
                    yaxis_title="Portfolio Value ($)",
                    hovermode="x unified",
                    height=600,
                )
                fig.show()

            except ImportError:
                click.echo("Warning: plotly not available for plotting", err=True)

    except Exception as e:
        logger.error(f"Backtest failed: {e}")
        click.echo(f"Error: Backtest failed: {e}", err=True)
        if verbose:
            import traceback

            traceback.print_exc()
        raise click.Abort from e
