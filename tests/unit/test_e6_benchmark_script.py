"""Unit tests for E6 benchmark scenario wiring."""

from __future__ import annotations

from scripts.benchmark.e6_compare_backtrader_vs_nautilus import (
    SCENARIOS,
    _build_backtrader_request,
    _build_nautilus_request,
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
