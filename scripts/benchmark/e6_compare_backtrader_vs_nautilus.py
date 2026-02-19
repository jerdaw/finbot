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
    scenario_id: str
    strategy_equivalent: bool
    equivalence_notes: str
    confidence: str


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


def _build_backtrader_request(scenario: str) -> BacktestRunRequest:
    if scenario not in {"gs01", "legacy_pilot"}:
        raise ValueError(f"Unsupported scenario: {scenario}")
    return BacktestRunRequest(
        strategy_name="NoRebalance",
        symbols=("SPY",),
        start=pd.Timestamp("2019-01-01"),
        end=pd.Timestamp("2020-12-31"),
        initial_cash=100_000.0,
        parameters={"equity_proportions": [1.0]},
    )


def _build_nautilus_request(scenario: str) -> BacktestRunRequest:
    if scenario == "gs01":
        return BacktestRunRequest(
            strategy_name="NoRebalance",
            symbols=("SPY",),
            start=pd.Timestamp("2019-01-01"),
            end=pd.Timestamp("2020-12-31"),
            initial_cash=100_000.0,
            parameters={"equity_proportions": [1.0]},
        )
    if scenario != "legacy_pilot":
        raise ValueError(f"Unsupported scenario: {scenario}")
    return BacktestRunRequest(
        strategy_name="Rebalance",
        symbols=("SPY",),
        start=pd.Timestamp("2019-01-01"),
        end=pd.Timestamp("2020-12-31"),
        initial_cash=100_000.0,
        parameters={"rebal_proportions": [1.0], "rebal_interval": 21},
    )


def _collect_samples(
    samples: int, engine: str, adapter, request: BacktestRunRequest
) -> tuple[list[BenchmarkSample], dict[str, object]]:
    rows: list[BenchmarkSample] = []
    last_assumptions: dict[str, object] = {}
    for _ in range(samples):
        result, elapsed, peak_mb = _measure_run(lambda: adapter.run(request))
        last_assumptions = dict(result.assumptions)
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
    return rows, last_assumptions


def _summarize(
    engine: str,
    scenario: str,
    scenario_id: str,
    rows: list[BenchmarkSample],
    assumptions: dict[str, object],
) -> BenchmarkSummary:
    strategy_equivalent = bool(assumptions.get("strategy_equivalent", engine == "backtrader"))
    confidence = str(assumptions.get("confidence", "high" if strategy_equivalent else "medium"))
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
        scenario_id=scenario_id,
        strategy_equivalent=strategy_equivalent,
        equivalence_notes=str(assumptions.get("equivalence_notes", "Backtrader baseline scenario.")),
        confidence=confidence,
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
        "| Engine | Scenario | Scenario ID | Samples | Mode | Equivalent | Confidence | Median Runtime (s) | Median Peak Memory (MB) | ROI | CAGR | Max Drawdown | Ending Value |",
        "| --- | --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    lines.extend(
        (
            f"| {summary.engine} | {summary.scenario} | {summary.scenario_id} | {summary.samples} | {summary.adapter_mode} | "
            f"{'yes' if summary.strategy_equivalent else 'no'} | {summary.confidence} | "
            f"{summary.median_run_seconds:.4f} | {summary.median_peak_memory_mb:.2f} | "
            f"{summary.roi:.6f} | {summary.cagr:.6f} | {summary.max_drawdown:.6f} | {summary.ending_value:.2f} |"
        )
        for summary in summaries
    )
    lines.extend(
        [
            "",
            "## Equivalence Notes",
            "",
            *[f"- `{summary.engine}` `{summary.scenario_id}`: {summary.equivalence_notes}" for summary in summaries],
        ]
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
    parser.add_argument(
        "--scenario",
        choices=["gs01", "legacy_pilot"],
        default="gs01",
        help="Benchmark scenario: gs01 for like-for-like NoRebalance, legacy_pilot for prior rebalance->EMA mapping.",
    )
    args = parser.parse_args()

    history_path = args.history_dir / "SPY_history_1d.parquet"
    if not history_path.exists():
        raise FileNotFoundError(f"History file not found: {history_path}")

    price_histories = {"SPY": _load_history(history_path)}

    bt_adapter = BacktraderAdapter(price_histories)
    bt_request = _build_backtrader_request(args.scenario)
    bt_rows, bt_assumptions = _collect_samples(
        samples=args.samples, engine="backtrader", adapter=bt_adapter, request=bt_request
    )
    bt_assumptions.setdefault("strategy_equivalent", True)
    bt_assumptions.setdefault("equivalence_notes", "Backtrader baseline for frozen GS-01 NoRebalance scenario.")
    bt_assumptions.setdefault("confidence", "high")

    nt_adapter = NautilusAdapter(
        price_histories,
        enable_backtrader_fallback=False,
        enable_native_execution=True,
    )
    nt_request = _build_nautilus_request(args.scenario)
    nt_rows, nt_assumptions = _collect_samples(
        samples=args.samples, engine="nautilus-pilot", adapter=nt_adapter, request=nt_request
    )
    if args.scenario == "legacy_pilot":
        nt_assumptions.setdefault("strategy_equivalent", False)
        nt_assumptions.setdefault(
            "equivalence_notes",
            "Legacy E6 pilot mapping uses rebalance request mapped to EMA-cross strategy.",
        )
        nt_assumptions.setdefault("confidence", "medium")
    else:
        nt_assumptions.setdefault("strategy_equivalent", True)
        nt_assumptions.setdefault("equivalence_notes", "NoRebalance mapped to native long-only buy-and-hold strategy.")
        nt_assumptions.setdefault("confidence", "high")

    summaries = [
        _summarize(
            "backtrader",
            "SPY 2019-2020 buy-and-hold",
            args.scenario,
            bt_rows,
            bt_assumptions,
        ),
        _summarize(
            "nautilus-pilot",
            "SPY 2019-2020 native run",
            args.scenario,
            nt_rows,
            nt_assumptions,
        ),
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
