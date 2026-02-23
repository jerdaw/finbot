from __future__ import annotations

from datetime import datetime

import numpy as np
import pandas as pd
import pytest

from finbot.services.simulation.monte_carlo.monte_carlo_simulator import monte_carlo_simulator
from finbot.services.simulation.sim_specific_bond_indexes import sim_idcot1tr, sim_idcot7tr, sim_idcot20tr
from finbot.services.simulation.sim_specific_funds import _sim_fund, sim_ntsx, simulate_fund
from finbot.services.simulation.sim_specific_stock_indexes import _get_yield_from_shiller, sim_nd100tr, sim_sp500tr


def test_get_yield_from_shiller_interpolates(monkeypatch: pytest.MonkeyPatch) -> None:
    idx = pd.date_range("2024-01-01", periods=3, freq="D")
    shiller_idx = pd.to_datetime(["2024-01-01", "2024-01-03"])
    shiller_df = pd.DataFrame(
        {"Dividend D": [2.0, 3.0], "S&P Comp. P": [100.0, 120.0]},
        index=shiller_idx,
    )
    price_index = pd.DataFrame({"Close": [10.0, 10.5, 11.0]}, index=idx)
    monkeypatch.setattr(
        "finbot.services.simulation.sim_specific_stock_indexes.get_shiller_data",
        lambda: shiller_df,
    )

    out = _get_yield_from_shiller(price_index)

    assert list(out.columns) == ["Yield"]
    assert len(out) == 3
    assert out["Yield"].isna().sum() == 0


def test_sim_sp500tr_uses_adj_close_and_overwrite(monkeypatch: pytest.MonkeyPatch) -> None:
    idx = pd.date_range("2024-01-01", periods=3, freq="D")
    base_hist = pd.DataFrame({"Adj Close": [100.0, 101.0, 102.0], "Close": [99.0, 100.0, 101.0]}, index=idx)
    tr_hist = pd.DataFrame({"Close": [200.0, 201.0, 202.0]}, index=idx)
    captured: dict[str, object] = {}

    def _get_history(ticker: str) -> pd.DataFrame:
        return tr_hist if ticker == "^SP500TR" else base_hist

    def _stub_sim(**kwargs):
        captured.update(kwargs)
        return pd.DataFrame({"Close": [1.0], "Change": [0.0]})

    monkeypatch.setattr("finbot.services.simulation.sim_specific_stock_indexes.get_history", _get_history)
    monkeypatch.setattr(
        "finbot.services.simulation.sim_specific_stock_indexes._get_yield_from_shiller",
        lambda _: pd.DataFrame({"Yield": [0.2, 0.2, 0.2]}, index=idx),
    )
    monkeypatch.setattr("finbot.services.simulation.sim_specific_stock_indexes.stock_index_simulator", _stub_sim)

    out = sim_sp500tr(overwrite_sim_with_index=True, save_db=False, force_update=True, adj=0.5)

    assert not out.empty
    assert captured["fund_name"] == "SP500TR_sim"
    assert captured["overwrite_sim_with_index"] is True
    assert captured["additive_constant"] == 0.5
    assert isinstance(captured["index_closes"], pd.Series)


def test_sim_nd100tr_warning_and_no_overwrite(monkeypatch: pytest.MonkeyPatch) -> None:
    idx = pd.date_range("2024-01-01", periods=3, freq="D")
    base_hist = pd.DataFrame({"Close": [10.0, 11.0, 12.0]}, index=idx)
    captured: dict[str, object] = {}

    monkeypatch.setattr("finbot.services.simulation.sim_specific_stock_indexes.get_history", lambda _ticker: base_hist)
    monkeypatch.setattr(
        "finbot.services.simulation.sim_specific_stock_indexes.get_xndx",
        lambda: pd.DataFrame({"Close": [1.0]}, index=pd.to_datetime(["2024-01-01"])),
    )
    monkeypatch.setattr(
        "finbot.services.simulation.sim_specific_stock_indexes.stock_index_simulator",
        lambda **kwargs: captured.update(kwargs) or pd.DataFrame({"Close": [1.0], "Change": [0.0]}),
    )

    with pytest.warns(UserWarning):
        sim_nd100tr(overwrite_sim_with_index=False, save_db=False)

    assert captured["fund_name"] == "ND100TR_sim"
    assert captured["overwrite_sim_with_index"] is False
    assert captured["index_closes"] is None


@pytest.mark.parametrize(
    ("fn", "min_years", "max_years"),
    [
        (sim_idcot20tr, 20, 30),
        (sim_idcot7tr, 7, 10),
        (sim_idcot1tr, 1, 3),
    ],
)
def test_bond_index_wrappers_route_to_simulator(
    fn,
    min_years: int,
    max_years: int,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    monkeypatch.setattr(
        "finbot.services.simulation.sim_specific_bond_indexes.bond_index_simulator",
        lambda **kwargs: captured.update(kwargs) or pd.DataFrame({"Close": [1.0], "Change": [0.0]}),
    )
    monkeypatch.setattr(
        "finbot.services.simulation.sim_specific_bond_indexes.get_idcot20tr",
        lambda: pd.DataFrame({"Close": [100.0]}, index=pd.to_datetime(["2024-01-01"])),
    )
    monkeypatch.setattr(
        "finbot.services.simulation.sim_specific_bond_indexes.get_idcot7tr",
        lambda: pd.DataFrame({"Close": [100.0]}, index=pd.to_datetime(["2024-01-01"])),
    )
    monkeypatch.setattr(
        "finbot.services.simulation.sim_specific_bond_indexes.get_idcot1tr",
        lambda: pd.DataFrame({"Close": [100.0]}, index=pd.to_datetime(["2024-01-01"])),
    )

    out = fn(overwrite_sim_with_index=True, save_db=False, force_update=True, adj=0.01)

    assert not out.empty
    assert captured["min_maturity_years"] == min_years
    assert captured["max_maturity_years"] == max_years
    assert captured["additive_constant"] == 0.01
    assert isinstance(captured["index_closes"], pd.Series)


def test_simulate_fund_rejects_unknown_ticker() -> None:
    with pytest.raises(ValueError, match="Unknown fund ticker"):
        simulate_fund("INVALID")


def test_simulate_fund_forwards_registry_config(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}
    expected = pd.DataFrame({"Close": [1.0], "Change": [0.0]})

    def _stub(*args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs
        return expected

    monkeypatch.setattr("finbot.services.simulation.sim_specific_funds._sim_fund", _stub)

    out = simulate_fund("SPY", save_sim=False, force_update=True, adj=0.123, overwrite_sim_with_fund=False)

    assert out is expected
    args = captured["args"]
    assert args[0] == "SPY_sim"
    assert args[2] == 1.0
    assert args[3] == pytest.approx(0.0945 / 100)


def test_sim_fund_uses_cache_when_available(monkeypatch: pytest.MonkeyPatch) -> None:
    cached = pd.DataFrame({"Close": [10.0], "Change": [0.0]})
    monkeypatch.setattr("finbot.services.simulation.sim_specific_funds.is_sufficiently_updated", lambda _name: True)
    monkeypatch.setattr("finbot.services.simulation.sim_specific_funds.pd.read_parquet", lambda _path: cached)

    out = _sim_fund(
        "SPY_sim",
        underlying_func=lambda: pd.DataFrame(),
        leverage_mult=1.0,
        annual_er_pct=0.0,
        percent_daily_spread_cost=0.0,
        fund_swap_pct=0.0,
        additive_constant_default=0.0,
        save_sim=False,
    )

    assert out is cached


def test_sim_fund_generates_and_merges_actual_close(monkeypatch: pytest.MonkeyPatch) -> None:
    idx = pd.date_range("2024-01-01", periods=3, freq="D")
    simulated = pd.DataFrame({"Close": [100.0, 102.0, 104.0], "Change": [0.0, 0.02, 0.0196]}, index=idx)
    actual_close = pd.Series([99.0, 100.0, 101.0], index=idx, name="Close")

    monkeypatch.setattr("finbot.services.simulation.sim_specific_funds.is_sufficiently_updated", lambda _name: False)
    monkeypatch.setattr(
        "finbot.services.simulation.sim_specific_funds.fund_simulator", lambda **_kwargs: simulated.copy()
    )
    monkeypatch.setattr(
        "finbot.services.simulation.sim_specific_funds.get_history",
        lambda _ticker: pd.DataFrame({"Close": actual_close}),
    )
    monkeypatch.setattr(
        "finbot.services.simulation.sim_specific_funds.merge_price_histories",
        lambda _lhs, rhs, fix_point: rhs,
    )

    out = _sim_fund(
        "SPY_sim",
        underlying_func=lambda: pd.DataFrame({"Close": [1.0]}, index=pd.to_datetime(["2024-01-01"])),
        leverage_mult=1.0,
        annual_er_pct=0.0,
        percent_daily_spread_cost=0.0,
        fund_swap_pct=0.0,
        additive_constant_default=0.0,
        save_sim=False,
        overwrite_sim_with_fund=True,
    )

    assert list(out.columns) == ["Close", "Change"]
    assert out["Close"].iloc[-1] == pytest.approx(actual_close.iloc[-1])


def test_sim_ntsx_builds_composite_and_handles_missing_actual(monkeypatch: pytest.MonkeyPatch) -> None:
    idx = pd.date_range("2024-01-01", periods=4, freq="D")
    base = pd.DataFrame({"Close": [100.0, 101.0, 102.0, 103.0]}, index=idx)

    monkeypatch.setattr("finbot.services.simulation.sim_specific_funds.is_sufficiently_updated", lambda _name: False)
    monkeypatch.setattr("finbot.services.simulation.sim_specific_funds.sim_spy", lambda: base)
    monkeypatch.setattr("finbot.services.simulation.sim_specific_funds.sim_tlt", lambda: base)
    monkeypatch.setattr("finbot.services.simulation.sim_specific_funds.sim_ief", lambda: base)
    monkeypatch.setattr("finbot.services.simulation.sim_specific_funds.sim_shy", lambda: base)
    monkeypatch.setattr(
        "finbot.services.simulation.sim_specific_funds.get_history",
        lambda _ticker: (_ for _ in ()).throw(FileNotFoundError("missing")),
    )
    warnings: list[str] = []
    monkeypatch.setattr("finbot.services.simulation.sim_specific_funds.logger.warning", warnings.append)

    out = sim_ntsx(save_sim=False, overwrite_sim_with_fund=True)

    assert not out.empty
    assert "Close" in out.columns
    assert warnings


def test_monte_carlo_simulator_shapes_result(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "finbot.services.simulation.monte_carlo.monte_carlo_simulator.tqdm", lambda iterable, **_k: iterable
    )
    monkeypatch.setattr(
        "finbot.services.simulation.monte_carlo.monte_carlo_simulator.sim_type_nd",
        lambda **kwargs: np.linspace(kwargs["start_price"], kwargs["start_price"] + 3, kwargs["sim_periods"]),
    )
    idx = pd.date_range("2024-01-01", periods=10, freq="D")
    df = pd.DataFrame({"Adj Close": np.linspace(100.0, 110.0, len(idx))}, index=idx)

    out = monte_carlo_simulator(
        equity_data=df,
        equity_start=pd.Timestamp(datetime(2024, 1, 2)),
        equity_end=pd.Timestamp(datetime(2024, 1, 10)),
        sim_periods=4,
        n_sims=3,
    )

    assert out.shape == (3, 4)
    assert out.index.name == "Trials"
    assert out.columns.name == "Periods"
