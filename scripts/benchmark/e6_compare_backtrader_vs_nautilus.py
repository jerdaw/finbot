"""Generate E6 comparative benchmark artifacts for Backtrader vs Nautilus pilot."""

from __future__ import annotations

import argparse
import json
import platform
import time
import tracemalloc
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from statistics import median

import pandas as pd

from finbot.adapters.nautilus import NautilusAdapter
from finbot.core.contracts import BacktestRunRequest
from finbot.services.backtesting.adapters import BacktraderAdapter


@dataclass
class BenchmarkSample:
    """Single benchmark sample."""

    run_seconds: float
    peak_memory_mb: float
    mode: str
    roi: float
    cagr: float
    max_drawdown: float
    ending_value: float


@dataclass
class BenchmarkSummary:
    """Median benchmark summary over multiple samples."""

    engine: str
    scenario: str
    samples: int
    median_run_seconds: float
    median_peak_memory_mb: float
    roi: float
    cagr: float
    max_drawdown: float
    ending_value: float
    adapter_mode: str


def _load_history(path: Path) -> pd.DataFrame:
    df = pd.read_parquet(path).copy()
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    return df.sort_index()


def _measure_run(fn) -> tuple[object, float, float]:
    tracemalloc.start()
    start = time.perf_counter()
    result = fn()
    elapsed = time.perf_counter() - start
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return result, elapsed, peak / (1024 * 1024)


def _run_backtrader(price_histories: dict[str, pd.DataFrame]) -> BacktestRunRequest:
    return BacktestRunRequest(
        strategy_name="NoRebalance",
        symbols=("SPY",),
        start=pd.Timestamp("2019-01-01"),
        end=pd.Timestamp("2020-12-31"),
        initial_cash=100_000.0,
        parameters={"equity_proportions": [1.0]},
    )


def _run_nautilus_native(price_histories: dict[str, pd.DataFrame]) -> BacktestRunRequest:
    return BacktestRunRequest(
        strategy_name="Rebalance",
        symbols=("SPY",),
        start=pd.Timestamp("2019-01-01"),
        end=pd.Timestamp("2020-12-31"),
        initial_cash=100_000.0,
        parameters={"rebal_proportions": [1.0], "rebal_interval": 21},
    )


def _collect_samples(samples: int, engine: str, adapter, request: BacktestRunRequest) -> list[BenchmarkSample]:
    rows: list[BenchmarkSample] = []
    for _ in range(samples):
        result, elapsed, peak_mb = _measure_run(lambda: adapter.run(request))
        default_mode = "native_backtrader" if engine == "backtrader" else "unknown"
        mode = str(result.assumptions.get("adapter_mode", default_mode))
        rows.append(
            BenchmarkSample(
                run_seconds=elapsed,
                peak_memory_mb=peak_mb,
                mode=mode,
                roi=float(result.metrics.get("roi", 0.0)),
                cagr=float(result.metrics.get("cagr", 0.0)),
                max_drawdown=float(result.metrics.get("max_drawdown", 0.0)),
                ending_value=float(result.metrics.get("ending_value", 0.0)),
            )
        )
    return rows


def _summarize(engine: str, scenario: str, rows: list[BenchmarkSample]) -> BenchmarkSummary:
    return BenchmarkSummary(
        engine=engine,
        scenario=scenario,
        samples=len(rows),
        median_run_seconds=median(row.run_seconds for row in rows),
        median_peak_memory_mb=median(row.peak_memory_mb for row in rows),
        roi=median(row.roi for row in rows),
        cagr=median(row.cagr for row in rows),
        max_drawdown=median(row.max_drawdown for row in rows),
        ending_value=median(row.ending_value for row in rows),
        adapter_mode=rows[-1].mode,
    )


def _write_artifacts(
    output_dir: Path,
    run_date: str,
    environment: dict[str, str],
    summaries: list[BenchmarkSummary],
) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"e6-benchmark-{run_date}.json"
    md_path = output_dir / f"e6-benchmark-{run_date}.md"

    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "environment": environment,
        "summaries": [asdict(summary) for summary in summaries],
    }
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# E6 Comparative Benchmark Artifact",
        "",
        f"- Generated: {payload['generated_at']}",
        f"- Python: {environment['python_version']}",
        f"- Platform: {environment['platform']}",
        "",
        "| Engine | Scenario | Samples | Mode | Median Runtime (s) | Median Peak Memory (MB) | ROI | CAGR | Max Drawdown | Ending Value |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    lines.extend(
        (
            f"| {summary.engine} | {summary.scenario} | {summary.samples} | {summary.adapter_mode} | "
            f"{summary.median_run_seconds:.4f} | {summary.median_peak_memory_mb:.2f} | "
            f"{summary.roi:.6f} | {summary.cagr:.6f} | {summary.max_drawdown:.6f} | {summary.ending_value:.2f} |"
        )
        for summary in summaries
    )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", type=int, default=3, help="Number of runs per engine/scenario.")
    parser.add_argument(
        "--history-dir",
        type=Path,
        default=Path("finbot/data/yfinance_data/history"),
        help="Directory containing SPY_history_1d.parquet.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("docs/research/artifacts"),
        help="Directory where JSON/Markdown artifacts are written.",
    )
    args = parser.parse_args()

    history_path = args.history_dir / "SPY_history_1d.parquet"
    if not history_path.exists():
        raise FileNotFoundError(f"History file not found: {history_path}")

    price_histories = {"SPY": _load_history(history_path)}

    bt_adapter = BacktraderAdapter(price_histories)
    bt_request = _run_backtrader(price_histories)
    bt_rows = _collect_samples(samples=args.samples, engine="backtrader", adapter=bt_adapter, request=bt_request)

    nt_adapter = NautilusAdapter(
        price_histories,
        enable_backtrader_fallback=False,
        enable_native_execution=True,
    )
    nt_request = _run_nautilus_native(price_histories)
    nt_rows = _collect_samples(samples=args.samples, engine="nautilus-pilot", adapter=nt_adapter, request=nt_request)

    summaries = [
        _summarize("backtrader", "SPY 2019-2020 buy-and-hold", bt_rows),
        _summarize("nautilus-pilot", "SPY 2019-2020 rebalance->EMA pilot", nt_rows),
    ]

    run_date = datetime.now(UTC).strftime("%Y-%m-%d")
    environment = {
        "python_version": platform.python_version(),
        "platform": platform.platform(),
    }
    json_path, md_path = _write_artifacts(args.output_dir, run_date, environment, summaries)
    print(f"Wrote benchmark JSON: {json_path}")
    print(f"Wrote benchmark markdown: {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
