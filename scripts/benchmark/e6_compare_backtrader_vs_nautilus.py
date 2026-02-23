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


@dataclass(frozen=True)
class ScenarioConfig:
    """Frozen benchmark scenario configuration."""

    scenario_id: str
    description: str
    symbols: tuple[str, ...]
    start: pd.Timestamp
    end: pd.Timestamp
    strategy_name: str
    parameters: dict[str, object]
    backtrader_equivalence_note: str
    nautilus_equivalence_note: str
    nautilus_confidence: str
    nautilus_strategy_equivalent: bool


@dataclass(frozen=True)
class EquivalenceTolerance:
    """Scenario-specific tolerance envelope for Backtrader vs Nautilus comparability."""

    roi_abs: float
    cagr_abs: float
    max_drawdown_abs: float
    ending_value_relative: float


SCENARIOS: dict[str, ScenarioConfig] = {
    "gs01": ScenarioConfig(
        scenario_id="gs01",
        description="SPY 2019-2020 buy-and-hold",
        symbols=("SPY",),
        start=pd.Timestamp("2019-01-01"),
        end=pd.Timestamp("2020-12-31"),
        strategy_name="NoRebalance",
        parameters={"equity_proportions": [1.0]},
        backtrader_equivalence_note="Backtrader baseline for frozen GS-01 NoRebalance scenario.",
        nautilus_equivalence_note="NoRebalance mapped to native long-only buy-and-hold strategy.",
        nautilus_confidence="high",
        nautilus_strategy_equivalent=True,
    ),
    "gs02": ScenarioConfig(
        scenario_id="gs02",
        description="SPY/TLT 2010-2026 dual momentum",
        symbols=("SPY", "TLT"),
        start=pd.Timestamp("2010-01-04"),
        end=pd.Timestamp("2026-02-09"),
        strategy_name="DualMomentum",
        parameters={"lookback": 252, "rebal_interval": 21},
        backtrader_equivalence_note="Backtrader baseline for frozen GS-02 DualMomentum scenario.",
        nautilus_equivalence_note=(
            "DualMomentum mapped to deterministic pilot proxy mirroring strategy signal/rebalance logic."
        ),
        nautilus_confidence="medium",
        nautilus_strategy_equivalent=True,
    ),
    "gs03": ScenarioConfig(
        scenario_id="gs03",
        description="SPY/QQQ/TLT 2010-2026 risk parity",
        symbols=("SPY", "QQQ", "TLT"),
        start=pd.Timestamp("2010-01-04"),
        end=pd.Timestamp("2026-02-09"),
        strategy_name="RiskParity",
        parameters={"vol_window": 63, "rebal_interval": 21},
        backtrader_equivalence_note="Backtrader baseline for frozen GS-03 RiskParity scenario.",
        nautilus_equivalence_note=(
            "RiskParity mapped to deterministic pilot proxy mirroring inverse-volatility rebalance logic."
        ),
        nautilus_confidence="medium",
        nautilus_strategy_equivalent=True,
    ),
    "legacy_pilot": ScenarioConfig(
        scenario_id="legacy_pilot",
        description="SPY 2019-2020 native run",
        symbols=("SPY",),
        start=pd.Timestamp("2019-01-01"),
        end=pd.Timestamp("2020-12-31"),
        strategy_name="Rebalance",
        parameters={"rebal_proportions": [1.0], "rebal_interval": 21},
        backtrader_equivalence_note="Backtrader baseline for legacy pilot mapping scenario.",
        nautilus_equivalence_note="Legacy E6 pilot mapping uses rebalance request mapped to EMA-cross strategy.",
        nautilus_confidence="medium",
        nautilus_strategy_equivalent=False,
    ),
}

SCENARIO_EQUIVALENCE_TOLERANCES: dict[str, EquivalenceTolerance] = {
    # GS-02/GS-03 thresholds reflect acceptable drift for native-vs-native pilot comparability.
    "gs02": EquivalenceTolerance(
        roi_abs=0.08,
        cagr_abs=0.012,
        max_drawdown_abs=0.03,
        ending_value_relative=0.08,
    ),
    "gs03": EquivalenceTolerance(
        roi_abs=0.10,
        cagr_abs=0.015,
        max_drawdown_abs=0.04,
        ending_value_relative=0.10,
    ),
}


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


def _build_backtrader_request(config: ScenarioConfig) -> BacktestRunRequest:
    return BacktestRunRequest(
        strategy_name=config.strategy_name,
        symbols=config.symbols,
        start=config.start,
        end=config.end,
        initial_cash=100_000.0,
        parameters=dict(config.parameters),
    )


def _build_nautilus_request(config: ScenarioConfig) -> BacktestRunRequest:
    return BacktestRunRequest(
        strategy_name=config.strategy_name,
        symbols=config.symbols,
        start=config.start,
        end=config.end,
        initial_cash=100_000.0,
        parameters=dict(config.parameters),
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
    confidence = _derive_confidence(engine=engine, assumptions=assumptions, strategy_equivalent=strategy_equivalent)
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


def _relative_delta(candidate: float, baseline: float) -> float:
    denominator = abs(baseline)
    if denominator <= 1e-12:
        return abs(candidate - baseline)
    return abs(candidate - baseline) / denominator


def _evaluate_strategy_equivalence(
    *,
    baseline: BenchmarkSummary,
    candidate: BenchmarkSummary,
    tolerance: EquivalenceTolerance,
) -> tuple[bool, str]:
    roi_delta = abs(candidate.roi - baseline.roi)
    cagr_delta = abs(candidate.cagr - baseline.cagr)
    max_drawdown_delta = abs(candidate.max_drawdown - baseline.max_drawdown)
    ending_relative_delta = _relative_delta(candidate.ending_value, baseline.ending_value)

    checks = {
        "roi_abs": roi_delta <= tolerance.roi_abs,
        "cagr_abs": cagr_delta <= tolerance.cagr_abs,
        "max_drawdown_abs": max_drawdown_delta <= tolerance.max_drawdown_abs,
        "ending_value_relative": ending_relative_delta <= tolerance.ending_value_relative,
    }
    equivalent = all(checks.values())
    failed = [name for name, passed in checks.items() if not passed]
    status = "pass" if equivalent else f"fail ({', '.join(failed)})"
    note = (
        "Tolerance-gated classification vs Backtrader baseline: "
        f"roi_abs={roi_delta:.6f}<={tolerance.roi_abs:.6f}, "
        f"cagr_abs={cagr_delta:.6f}<={tolerance.cagr_abs:.6f}, "
        f"max_drawdown_abs={max_drawdown_delta:.6f}<={tolerance.max_drawdown_abs:.6f}, "
        f"ending_value_relative={ending_relative_delta:.6f}<={tolerance.ending_value_relative:.6f}; "
        f"result={status}."
    )
    return equivalent, note


def _apply_tolerance_classification(
    *,
    scenario_id: str,
    baseline_summary: BenchmarkSummary,
    nautilus_summary: BenchmarkSummary,
    nautilus_assumptions: dict[str, object],
) -> BenchmarkSummary:
    tolerance = SCENARIO_EQUIVALENCE_TOLERANCES.get(scenario_id)
    if tolerance is None:
        return nautilus_summary

    equivalent, tolerance_note = _evaluate_strategy_equivalence(
        baseline=baseline_summary,
        candidate=nautilus_summary,
        tolerance=tolerance,
    )
    nautilus_summary.strategy_equivalent = equivalent
    nautilus_summary.confidence = _derive_confidence(
        engine="nautilus-pilot",
        assumptions=nautilus_assumptions,
        strategy_equivalent=equivalent,
    )
    nautilus_summary.equivalence_notes = f"{nautilus_summary.equivalence_notes} {tolerance_note}"
    return nautilus_summary


def _derive_confidence(*, engine: str, assumptions: dict[str, object], strategy_equivalent: bool) -> str:
    if engine != "nautilus-pilot":
        return "high" if strategy_equivalent else "medium"

    valuation_fidelity = str(assumptions.get("valuation_fidelity", "")).strip().lower()
    if valuation_fidelity == "shadow_backtrader":
        return "medium" if strategy_equivalent else "low"

    fidelity = str(assumptions.get("execution_fidelity", "")).strip().lower()
    if fidelity == "full_native":
        return "high" if strategy_equivalent else "low"
    if fidelity in {"proxy_native", "mapped_native"}:
        return "medium" if strategy_equivalent else "low"

    existing = assumptions.get("confidence")
    if existing is not None:
        return str(existing)
    return "high" if strategy_equivalent else "medium"


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
        choices=[*sorted(SCENARIOS.keys()), "all"],
        default="gs01",
        help="Benchmark scenario ID or 'all' for gs01/gs02/gs03.",
    )
    args = parser.parse_args()

    scenario_ids = ["gs01", "gs02", "gs03"] if args.scenario == "all" else [args.scenario]
    summaries: list[BenchmarkSummary] = []

    for scenario_id in scenario_ids:
        scenario_config = SCENARIOS[scenario_id]
        price_histories: dict[str, pd.DataFrame] = {}
        for symbol in scenario_config.symbols:
            history_path = args.history_dir / f"{symbol}_history_1d.parquet"
            if not history_path.exists():
                raise FileNotFoundError(f"History file not found: {history_path}")
            price_histories[symbol] = _load_history(history_path)

        bt_adapter = BacktraderAdapter(price_histories)
        bt_request = _build_backtrader_request(scenario_config)
        bt_rows, bt_assumptions = _collect_samples(
            samples=args.samples, engine="backtrader", adapter=bt_adapter, request=bt_request
        )
        bt_assumptions.setdefault("strategy_equivalent", True)
        bt_assumptions.setdefault("equivalence_notes", scenario_config.backtrader_equivalence_note)
        bt_assumptions.setdefault("execution_fidelity", "full_native")

        nt_adapter = NautilusAdapter(
            price_histories,
            enable_backtrader_fallback=False,
            enable_native_execution=True,
        )
        nt_request = _build_nautilus_request(scenario_config)
        nt_rows, nt_assumptions = _collect_samples(
            samples=args.samples, engine="nautilus-pilot", adapter=nt_adapter, request=nt_request
        )
        nt_assumptions.setdefault("strategy_equivalent", scenario_config.nautilus_strategy_equivalent)
        nt_assumptions.setdefault("equivalence_notes", scenario_config.nautilus_equivalence_note)
        nt_assumptions.setdefault("execution_fidelity", "unknown")

        bt_summary = _summarize(
            "backtrader",
            scenario_config.description,
            scenario_id,
            bt_rows,
            bt_assumptions,
        )
        nt_summary = _summarize(
            "nautilus-pilot",
            scenario_config.description,
            scenario_id,
            nt_rows,
            nt_assumptions,
        )
        nt_summary = _apply_tolerance_classification(
            scenario_id=scenario_id,
            baseline_summary=bt_summary,
            nautilus_summary=nt_summary,
            nautilus_assumptions=nt_assumptions,
        )

        summaries.extend([bt_summary, nt_summary])

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
