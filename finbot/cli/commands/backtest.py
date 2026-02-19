"""Backtest command for running strategy backtests."""

from __future__ import annotations

import click
import pandas as pd

from finbot.cli.utils.output import save_output
from finbot.cli.validators import DATE, POSITIVE_FLOAT, TICKER
from finbot.config import logger
from finbot.libs.logger.audit import audit_operation

# Available strategies for validation
AVAILABLE_STRATEGIES = [
    "Rebalance",
    "NoRebalance",
    "SMACrossover",
    "SMACrossoverDouble",
    "SMACrossoverTriple",
    "MACDSingle",
    "MACDDual",
    "DipBuySMA",
    "DipBuyStdev",
    "SMARebalMix",
    "DualMomentum",
    "RiskParity",
]


@click.command()
@click.option(
    "--strategy",
    type=click.Choice(AVAILABLE_STRATEGIES, case_sensitive=False),
    required=True,
    help="Strategy name (e.g., Rebalance, SMACrossover, MACDSingle)",
)
@click.option(
    "--asset",
    type=TICKER,
    required=True,
    help="Asset ticker to backtest (e.g., SPY, QQQ)",
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
    "--cash",
    type=POSITIVE_FLOAT,
    default=100000.0,
    show_default=True,
    help="Initial cash amount (must be positive)",
)
@click.option(
    "--output",
    type=click.Path(),
    help="Output file path for results (CSV, parquet, or JSON)",
)
@click.option(
    "--plot",
    is_flag=True,
    help="Display backtrader plot of backtest results",
)
@click.pass_context
def backtest(  # noqa: C901 - CLI command handlers are inherently complex
    ctx: click.Context,
    strategy: str,
    asset: str,
    start: str | None,
    end: str | None,
    cash: float,
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
    parameters = {
        "strategy": strategy,
        "asset": asset,
        "start": start,
        "end": end,
        "cash": cash,
        "output": output,
        "plot": plot,
        "verbose": verbose,
        "trace_id": ctx.obj.get("trace_id"),
    }

    with audit_operation(
        logger,
        operation="backtest",
        component="cli.backtest",
        parameters=parameters,
    ):
        if verbose:
            logger.info(f"Starting backtest: {strategy} on {asset}")

        # Import strategy (strategy is already validated by Click.Choice)
        try:
            from finbot.services.backtesting.strategies.dip_buy_sma import DipBuySMA
            from finbot.services.backtesting.strategies.dip_buy_stdev import DipBuyStdev
            from finbot.services.backtesting.strategies.dual_momentum import DualMomentum
            from finbot.services.backtesting.strategies.macd_dual import MACDDual
            from finbot.services.backtesting.strategies.macd_single import MACDSingle
            from finbot.services.backtesting.strategies.no_rebalance import NoRebalance
            from finbot.services.backtesting.strategies.rebalance import Rebalance
            from finbot.services.backtesting.strategies.risk_parity import RiskParity
            from finbot.services.backtesting.strategies.sma_crossover import SMACrossover
            from finbot.services.backtesting.strategies.sma_crossover_double import SMACrossoverDouble
            from finbot.services.backtesting.strategies.sma_crossover_triple import SMACrossoverTriple
            from finbot.services.backtesting.strategies.sma_rebal_mix import SmaRebalMix

            # Map strategy names to classes (no need to validate, Click.Choice did it)
            strategy_map: dict[str, type] = {
                "rebalance": Rebalance,
                "norebalance": NoRebalance,
                "smacrossover": SMACrossover,
                "smacrossoverdouble": SMACrossoverDouble,
                "smacrossovertriple": SMACrossoverTriple,
                "macdsingle": MACDSingle,
                "macddual": MACDDual,
                "dipbuysma": DipBuySMA,
                "dipbuystdev": DipBuyStdev,
                "smarebalmix": SmaRebalMix,
                "dualmomentum": DualMomentum,
                "riskparity": RiskParity,
            }

            strategy_key = strategy.lower().replace("_", "").replace("-", "")
            strategy_class = strategy_map[strategy_key]

        except (ImportError, AttributeError, KeyError) as e:
            logger.error(f"Failed to import strategy: {e}")
            click.echo(f"Error: Could not load strategy '{strategy}': {e}", err=True)
            raise click.Abort from e

        # Load price data
        try:
            from finbot.utils.data_collection_utils.yfinance.get_history import get_history

            click.echo(f"Loading {asset} price data...")
            price_data = get_history(asset, adjust_price=True)

            if len(price_data) == 0:
                click.echo("Error: No data available for specified asset", err=True)
                raise click.Abort

            if verbose:
                logger.info(f"Loaded {len(price_data)} data points for {asset}")

        except Exception as e:
            logger.error(f"Failed to load price data: {e}")
            click.echo(f"Error: Could not load price data for {asset}: {e}", err=True)
            raise click.Abort from e

        # Run backtest
        try:
            import backtrader as bt

            from finbot.services.backtesting.backtest_runner import BacktestRunner
            from finbot.services.backtesting.brokers.fixed_commission_scheme import FixedCommissionScheme

            click.echo(f"Running backtest: {strategy} on {asset}...")

            # Single-asset strategies need proportions=(1.0,) for rebalance-based strategies
            strat_kwargs: dict[str, object] = {}
            if strategy_key in ("rebalance", "smarebalmix"):
                strat_kwargs["proportions"] = (1.0,)

            runner = BacktestRunner(
                price_histories={asset: price_data},
                start=pd.Timestamp(start) if start else None,
                end=pd.Timestamp(end) if end else None,
                duration=None,
                start_step=None,
                init_cash=cash,
                strat=strategy_class,
                strat_kwargs=strat_kwargs,
                broker=bt.brokers.BackBroker,
                broker_kwargs={},
                broker_commission=FixedCommissionScheme,
                sizer=bt.sizers.AllInSizer,
                sizer_kwargs={},
                plot=plot,
            )

            results = runner.run_backtest()

            if verbose:
                logger.info("Backtest complete")

            # results is a DataFrame (one row) from compute_stats
            starting_value = results["Starting Value"].iloc[0]
            ending_value = results["Ending Value"].iloc[0]
            roi = results["ROI"].iloc[0]

            click.echo("\nBacktest Results:")
            click.echo(f"  Strategy: {strategy}")
            click.echo(f"  Asset: {asset}")
            click.echo(f"  Initial capital: ${starting_value:,.2f}")
            click.echo(f"  Final value: ${ending_value:,.2f}")
            click.echo(f"  Total return: {roi:+.2%}")

            click.echo("\nPerformance Metrics:")
            for col, label in (
                ("CAGR", "CAGR"),
                ("Sharpe", "Sharpe Ratio"),
                ("Calmar", "Calmar Ratio"),
                ("Max Drawdown", "Max Drawdown"),
                ("Annualized Volatility", "Annualized Volatility"),
                ("Win Days %", "Win Days %"),
            ):
                if col in results.columns:
                    click.echo(f"  {label}: {results[col].iloc[0]:.4f}")

            # Save output if requested
            if output:
                save_output(results, output, verbose=verbose)

        except Exception as e:
            logger.error(f"Backtest failed: {e}")
            click.echo(f"Error: Backtest failed: {e}", err=True)
            if verbose:
                import traceback

                traceback.print_exc()
            raise click.Abort from e
