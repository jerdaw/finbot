"""Update command for running daily data update pipeline."""

from __future__ import annotations

import click

from finbot.config import logger
from finbot.libs.logger.audit import audit_operation


@click.command()
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be updated without making changes",
)
@click.option(
    "--skip-prices",
    is_flag=True,
    help="Skip price data updates",
)
@click.option(
    "--skip-simulations",
    is_flag=True,
    help="Skip simulation updates",
)
@click.pass_context
def update(  # noqa: C901 - CLI command handlers are inherently complex
    ctx: click.Context,
    dry_run: bool,
    skip_prices: bool,
    skip_simulations: bool,
) -> None:
    """Run daily data update pipeline.

    \b
    Updates all data sources and regenerates simulations:
      1. Fetch latest price histories (Yahoo Finance, Google Finance)
      2. Fetch latest economic data (FRED, Shiller)
      3. Re-run all fund simulations
      4. Re-run all index simulations

    \b
    Examples:
      finbot update
      finbot update --dry-run
      finbot update --skip-simulations
    """
    verbose = ctx.obj.get("verbose", False)
    parameters = {
        "dry_run": dry_run,
        "skip_prices": skip_prices,
        "skip_simulations": skip_simulations,
        "verbose": verbose,
        "trace_id": ctx.obj.get("trace_id"),
    }

    with audit_operation(
        logger,
        operation="update",
        component="cli.update",
        parameters=parameters,
    ):
        if dry_run:
            click.echo("DRY RUN MODE - No changes will be made\n")

        if verbose:
            logger.info("Starting daily update pipeline")

        # Import update_daily script
        try:
            if dry_run:
                click.echo("Would execute daily update pipeline:")
                click.echo("  1. Update price histories (YF, GF)")
                click.echo("  2. Update economic data (FRED, Shiller)")
                click.echo("  3. Re-run overnight LIBOR approximation")
                click.echo("  4. Re-run index simulations")
                click.echo("  5. Re-run fund simulations")
                click.echo("\nUse without --dry-run to execute")
                return

            # Run actual update
            click.echo("Running daily update pipeline...")

            if not skip_prices:
                click.echo("\n[1/5] Updating price histories...")
                try:
                    from scripts.update_daily import update_yf_price_histories

                    update_yf_price_histories()
                    click.echo("  ✓ Price histories updated")
                except Exception as e:
                    click.echo(f"  ✗ Price history update failed: {e}", err=True)
                    if verbose:
                        import traceback

                        traceback.print_exc()

                click.echo("\n[2/5] Updating economic data...")
                try:
                    from scripts.update_daily import update_fred_data, update_shiller_data

                    update_fred_data()
                    update_shiller_data()
                    click.echo("  ✓ Economic data updated")
                except Exception as e:
                    click.echo(f"  ✗ Economic data update failed: {e}", err=True)
                    if verbose:
                        import traceback

                        traceback.print_exc()
            else:
                click.echo("\n[1-2/5] Skipping price and economic data updates")

            if not skip_simulations:
                click.echo("\n[3/5] Approximating overnight LIBOR...")
                try:
                    from scripts.update_daily import approximate_overnight_libor

                    approximate_overnight_libor()
                    click.echo("  ✓ LIBOR approximation complete")
                except Exception as e:
                    click.echo(f"  ✗ LIBOR approximation failed: {e}", err=True)
                    if verbose:
                        import traceback

                        traceback.print_exc()

                click.echo("\n[4/5] Running index simulations...")
                try:
                    from scripts.update_daily import sim_idcot1tr, sim_idcot7tr, sim_idcot20tr, sim_sp500tr

                    sim_sp500tr()
                    sim_idcot20tr()
                    sim_idcot7tr()
                    sim_idcot1tr()
                    click.echo("  ✓ Index simulations complete")
                except Exception as e:
                    click.echo(f"  ✗ Index simulations failed: {e}", err=True)
                    if verbose:
                        import traceback

                        traceback.print_exc()

                click.echo("\n[5/5] Running fund simulations...")
                try:
                    from scripts.update_daily import (
                        sim_2x_stt,
                        sim_3x_stt,
                        sim_ief,
                        sim_ntsx,
                        sim_qld,
                        sim_qqq,
                        sim_shy,
                        sim_spy,
                        sim_sso,
                        sim_tlt,
                        sim_tmf,
                        sim_tqqq,
                        sim_tyd,
                        sim_ubt,
                        sim_upro,
                        sim_ust,
                    )

                    fund_sims = [
                        sim_spy,
                        sim_sso,
                        sim_upro,
                        sim_qqq,
                        sim_qld,
                        sim_tqqq,
                        sim_tlt,
                        sim_ubt,
                        sim_tmf,
                        sim_ief,
                        sim_ust,
                        sim_tyd,
                        sim_shy,
                        sim_2x_stt,
                        sim_3x_stt,
                        sim_ntsx,
                    ]

                    total_funds = len(fund_sims)
                    for i, sim_func in enumerate(fund_sims, 1):
                        fund_name = sim_func.__name__.replace("sim_", "").upper()
                        try:
                            sim_func()
                            if verbose:
                                click.echo(f"  [{i}/{total_funds}] ✓ {fund_name}")
                        except Exception as e:
                            click.echo(f"  [{i}/{total_funds}] ✗ {fund_name}: {e}", err=True)

                    click.echo(f"  ✓ Fund simulations complete ({total_funds} funds)")
                except Exception as e:
                    click.echo(f"  ✗ Fund simulations failed: {e}", err=True)
                    if verbose:
                        import traceback

                        traceback.print_exc()
            else:
                click.echo("\n[3-5/5] Skipping simulations")

            click.echo("\n✓ Daily update pipeline complete")

            if verbose:
                logger.info("Daily update pipeline finished")

        except Exception as e:
            logger.error(f"Update pipeline failed: {e}")
            click.echo(f"\nError: Update pipeline failed: {e}", err=True)
            if verbose:
                import traceback

                traceback.print_exc()
            raise click.Abort from e
