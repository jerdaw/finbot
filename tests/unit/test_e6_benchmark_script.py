"""Unit tests for E6 benchmark scenario wiring."""

from __future__ import annotations

from scripts.benchmark.e6_compare_backtrader_vs_nautilus import (
    SCENARIO_EQUIVALENCE_TOLERANCES,
    SCENARIOS,
    BenchmarkSummary,
    _apply_tolerance_classification,
    _build_backtrader_request,
    _build_nautilus_request,
    _derive_confidence,
    _evaluate_strategy_equivalence,
)


def test_benchmark_scenarios_include_post_e6_phase2_targets() -> None:
    assert "gs02" in SCENARIOS
    assert "gs03" in SCENARIOS


def test_gs02_requests_use_dualmomentum_symbols_and_params() -> None:
    cfg = SCENARIOS["gs02"]
    bt_request = _build_backtrader_request(cfg)
    nt_request = _build_nautilus_request(cfg)

    assert bt_request.strategy_name == "DualMomentum"
    assert nt_request.strategy_name == "DualMomentum"
    assert bt_request.symbols == ("SPY", "TLT")
    assert nt_request.symbols == ("SPY", "TLT")
    assert bt_request.parameters["lookback"] == 252
    assert nt_request.parameters["rebal_interval"] == 21


def test_gs03_requests_use_riskparity_symbols_and_params() -> None:
    cfg = SCENARIOS["gs03"]
    bt_request = _build_backtrader_request(cfg)
    nt_request = _build_nautilus_request(cfg)

    assert bt_request.strategy_name == "RiskParity"
    assert nt_request.strategy_name == "RiskParity"
    assert bt_request.symbols == ("SPY", "QQQ", "TLT")
    assert nt_request.symbols == ("SPY", "QQQ", "TLT")
    assert bt_request.parameters["vol_window"] == 63
    assert nt_request.parameters["rebal_interval"] == 21


def test_confidence_is_high_for_full_native_equivalent() -> None:
    confidence = _derive_confidence(
        engine="nautilus-pilot",
        assumptions={"execution_fidelity": "full_native"},
        strategy_equivalent=True,
    )
    assert confidence == "high"


def test_confidence_is_medium_for_proxy_native_equivalent() -> None:
    confidence = _derive_confidence(
        engine="nautilus-pilot",
        assumptions={"execution_fidelity": "proxy_native"},
        strategy_equivalent=True,
    )
    assert confidence == "medium"


def test_confidence_is_low_for_full_native_non_equivalent() -> None:
    confidence = _derive_confidence(
        engine="nautilus-pilot",
        assumptions={"execution_fidelity": "full_native"},
        strategy_equivalent=False,
    )
    assert confidence == "low"


def test_confidence_is_medium_for_shadow_backtrader_equivalent() -> None:
    confidence = _derive_confidence(
        engine="nautilus-pilot",
        assumptions={"execution_fidelity": "full_native", "valuation_fidelity": "shadow_backtrader"},
        strategy_equivalent=True,
    )
    assert confidence == "medium"


def _make_summary(
    *, engine: str, scenario_id: str, roi: float, cagr: float, max_drawdown: float, ending: float
) -> BenchmarkSummary:
    return BenchmarkSummary(
        engine=engine,
        scenario="test",
        samples=3,
        median_run_seconds=1.0,
        median_peak_memory_mb=1.0,
        roi=roi,
        cagr=cagr,
        max_drawdown=max_drawdown,
        ending_value=ending,
        adapter_mode="native_backtrader" if engine == "backtrader" else "native_nautilus_full",
        scenario_id=scenario_id,
        strategy_equivalent=True,
        equivalence_notes="base",
        confidence="high",
    )


def test_evaluate_strategy_equivalence_fails_when_gs02_thresholds_are_exceeded() -> None:
    tolerance = SCENARIO_EQUIVALENCE_TOLERANCES["gs02"]
    baseline = _make_summary(
        engine="backtrader",
        scenario_id="gs02",
        roi=1.000277,
        cagr=0.044082,
        max_drawdown=-0.272478,
        ending=200027.71,
    )
    candidate = _make_summary(
        engine="nautilus-pilot",
        scenario_id="gs02",
        roi=0.896277,
        cagr=0.040549,
        max_drawdown=-0.340714,
        ending=189627.72,
    )

    equivalent, note = _evaluate_strategy_equivalence(
        baseline=baseline,
        candidate=candidate,
        tolerance=tolerance,
    )
    assert equivalent is False
    assert "result=fail" in note


def test_apply_tolerance_classification_updates_nautilus_summary() -> None:
    baseline = _make_summary(
        engine="backtrader",
        scenario_id="gs02",
        roi=1.0,
        cagr=0.04,
        max_drawdown=-0.25,
        ending=200000.0,
    )
    candidate = _make_summary(
        engine="nautilus-pilot",
        scenario_id="gs02",
        roi=0.995,
        cagr=0.0395,
        max_drawdown=-0.252,
        ending=198500.0,
    )

    updated = _apply_tolerance_classification(
        scenario_id="gs02",
        baseline_summary=baseline,
        nautilus_summary=candidate,
        nautilus_assumptions={"execution_fidelity": "full_native"},
    )

    assert updated.strategy_equivalent is True
    assert updated.confidence == "high"
    assert "Tolerance-gated classification vs Backtrader baseline" in updated.equivalence_notes
