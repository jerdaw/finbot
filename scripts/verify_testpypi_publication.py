#!/usr/bin/env python3
"""Verify that finbot is published on TestPyPI.

Usage:
    uv run python scripts/verify_testpypi_publication.py
    uv run python scripts/verify_testpypi_publication.py --version 1.0.0
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request

TESTPYPI_JSON_URL = "https://test.pypi.org/pypi/finbot/json"


def fetch_testpypi_payload() -> dict[str, object]:
    """Fetch TestPyPI package metadata for finbot."""
    try:
        with urllib.request.urlopen(TESTPYPI_JSON_URL, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            raise RuntimeError("Package 'finbot' not found on TestPyPI.") from exc
        raise RuntimeError(f"HTTP error from TestPyPI: {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Network error while contacting TestPyPI: {exc.reason}") from exc


def validate_publication(requested_version: str | None) -> int:
    """Validate that finbot exists on TestPyPI, optionally for a specific version."""
    payload = fetch_testpypi_payload()
    releases_obj = payload.get("releases")
    if not isinstance(releases_obj, dict):
        raise RuntimeError("Malformed TestPyPI response: missing 'releases'.")

    versions = sorted(releases_obj.keys())
    if not versions:
        raise RuntimeError("Package exists on TestPyPI but has no published versions.")

    print(f"Found finbot on TestPyPI with {len(versions)} version(s).")
    print(f"Latest version: {versions[-1]}")

    if requested_version:
        if requested_version not in releases_obj:
            raise RuntimeError(
                f"Version {requested_version!r} was not found on TestPyPI. Available versions: {', '.join(versions)}"
            )
        print(f"Requested version {requested_version!r} is available on TestPyPI.")

    return 0


def main() -> int:
    """Run CLI entrypoint."""
    parser = argparse.ArgumentParser(description="Verify finbot publication on TestPyPI.")
    parser.add_argument(
        "--version",
        type=str,
        default=None,
        help="Optional specific version to verify (example: 1.0.0).",
    )
    args = parser.parse_args()

    try:
        return validate_publication(args.version)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
