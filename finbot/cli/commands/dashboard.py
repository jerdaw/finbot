"""CLI command to launch the Streamlit dashboard."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import click


@click.command()
@click.option("--port", default=8501, help="Port to run the dashboard on.")
@click.option("--host", default="localhost", help="Host to bind the dashboard to.")
def dashboard(port: int, host: str) -> None:
    """Launch the Finbot web dashboard.

    \b
    Examples:
      finbot dashboard
      finbot dashboard --port 8080
      finbot dashboard --host 0.0.0.0 --port 8501
    """
    app_path = Path(__file__).resolve().parent.parent.parent / "dashboard" / "app.py"
    if not app_path.exists():
        click.echo(f"Error: dashboard app not found at {app_path}", err=True)
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
