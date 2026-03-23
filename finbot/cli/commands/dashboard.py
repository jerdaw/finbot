"""CLI command to launch the Streamlit dashboard."""

from __future__ import annotations

import subprocess
import sys
from importlib.util import find_spec
from pathlib import Path

import click

from finbot.config import logger
from finbot.libs.logger.audit import audit_operation


def _streamlit_available() -> bool:
    """Return whether the optional Streamlit dependency is installed."""
    return find_spec("streamlit") is not None


@click.command()
@click.option("--port", default=8501, help="Port to run the dashboard on.")
@click.option("--host", default="localhost", help="Host to bind the dashboard to.")
@click.pass_context
def dashboard(ctx: click.Context, port: int, host: str) -> None:
    """Launch the Finbot web dashboard.

    \b
    Examples:
      finbot dashboard
      finbot dashboard --port 8080
      finbot dashboard --host 0.0.0.0 --port 8501
    """
    with audit_operation(
        logger,
        operation="dashboard",
        component="cli.dashboard",
        parameters={
            "port": port,
            "host": host,
            "trace_id": ctx.obj.get("trace_id"),
        },
    ):
        app_path = Path(__file__).resolve().parent.parent.parent / "dashboard" / "app.py"
        if not app_path.exists():
            click.echo(f"Error: dashboard app not found at {app_path}", err=True)
            raise SystemExit(1)
        if not _streamlit_available():
            click.echo(
                "Error: Streamlit is not installed. Install dashboard support with "
                "`uv sync --extra dashboard` or `pip install 'finbot[dashboard]'`.",
                err=True,
            )
            raise SystemExit(1)

        click.echo(f"Starting Finbot Dashboard at http://{host}:{port}")
        cmd = [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(app_path),
            "--server.port",
            str(port),
            "--server.address",
            host,
        ]
        subprocess.run(cmd, check=False)
