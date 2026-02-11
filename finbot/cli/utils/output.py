"""Output utility functions for CLI."""

from __future__ import annotations

from pathlib import Path

import click
import pandas as pd

from finbot.config import logger


def save_output(data: pd.DataFrame, output_path: str, verbose: bool = False) -> None:
    """Save DataFrame to specified output format.

    Args:
        data: DataFrame to save
        output_path: Output file path (determines format by extension)
        verbose: Enable verbose logging

    Supported formats:
        - .csv: Comma-separated values
        - .parquet: Apache Parquet format
        - .json: JSON format
    """
    output_file = Path(output_path)
    extension = output_file.suffix.lower()

    try:
        if extension == ".csv":
            data.to_csv(output_file)
            click.echo(f"✓ Results saved to {output_file} (CSV format)")

        elif extension == ".parquet":
            data.to_parquet(output_file)
            click.echo(f"✓ Results saved to {output_file} (Parquet format)")

        elif extension == ".json":
            data.to_json(output_file, orient="records", date_format="iso")
            click.echo(f"✓ Results saved to {output_file} (JSON format)")

        else:
            # Default to CSV if extension not recognized
            csv_path = output_file.with_suffix(".csv")
            data.to_csv(csv_path)
            click.echo(f"Warning: Unknown extension '{extension}', saved as CSV: {csv_path}")

        if verbose:
            logger.info(f"Saved {len(data)} rows to {output_file}")

    except Exception as e:
        logger.error(f"Failed to save output: {e}")
        click.echo(f"Error: Could not save output to {output_file}: {e}", err=True)
        raise
