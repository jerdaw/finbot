"""Status command for showing data freshness and pipeline health."""

from __future__ import annotations

import click

from finbot.config import logger
from finbot.libs.logger.audit import audit_operation


@click.command()
@click.option(
    "--stale-only",
    is_flag=True,
    help="Only show stale data sources",
)
@click.pass_context
def status(ctx: click.Context, stale_only: bool) -> None:
    """Show data freshness and pipeline health.

    \b
    Displays the status of all data sources:
      - Last update time and age
      - File count and total size
      - Staleness warnings

    \b
    Examples:
      finbot status
      finbot status --stale-only
    """
    verbose = ctx.obj.get("verbose", False)
    parameters = {
        "stale_only": stale_only,
        "verbose": verbose,
        "trace_id": ctx.obj.get("trace_id"),
    }

    with audit_operation(
        logger,
        operation="status",
        component="cli.status",
        parameters=parameters,
    ):
        if verbose:
            logger.info("Checking data source freshness")

        from finbot.services.data_quality.check_data_freshness import check_all_freshness

        statuses = check_all_freshness()

        if stale_only:
            statuses = [s for s in statuses if s.is_stale]
            if not statuses:
                click.echo("All data sources are fresh.")
                return

        # Build table using prettytable
        from prettytable import PrettyTable

        table = PrettyTable()
        table.field_names = ["Source", "Files", "Size", "Last Updated", "Age", "Status"]
        table.align["Source"] = "l"
        table.align["Files"] = "r"
        table.align["Size"] = "r"
        table.align["Last Updated"] = "l"
        table.align["Age"] = "r"
        table.align["Status"] = "c"

        stale_count = 0
        for s in statuses:
            if s.is_stale:
                stale_count += 1
                status_icon = "STALE"
            else:
                status_icon = "OK"

            last_updated = s.newest_file.strftime("%Y-%m-%d %H:%M") if s.newest_file else "-"

            table.add_row(
                [
                    s.source.name,
                    s.file_count,
                    s.size_str,
                    last_updated,
                    s.age_str,
                    status_icon,
                ]
            )

        click.echo("\nData Source Status")
        click.echo("=" * 18)
        click.echo(table)

        # Summary
        total_files = sum(s.file_count for s in statuses)
        total_size = sum(s.total_size_bytes for s in statuses)
        size_mb = total_size / (1024 * 1024)
        click.echo(f"\nTotal: {total_files} files ({size_mb:.1f} MB) across {len(statuses)} sources")

        if stale_count > 0:
            click.echo(f"Warning: {stale_count} source(s) are stale. Run 'finbot update' to refresh.")
        else:
            click.echo("All data sources are fresh.")

        if verbose:
            click.echo("\nStaleness thresholds:")
            for s in statuses:
                click.echo(f"  {s.source.name}: {s.source.max_age_days} days (max)")
