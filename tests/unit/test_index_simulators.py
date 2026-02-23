"""Tests for stock and bond index simulators."""

from __future__ import annotations

import pandas as pd

from finbot.services.simulation.bond_index_simulator import bond_index_simulator
from finbot.services.simulation.stock_index_simulator import stock_index_simulator


def _series(values: list[float]) -> pd.Series:
    idx = pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-03"])
    return pd.Series(values, index=idx)


def test_stock_index_simulator_builds_from_underlying(monkeypatch) -> None:
    monkeypatch.setattr("finbot.services.simulation.stock_index_simulator.is_sufficiently_updated", lambda *_: False)

    result = stock_index_simulator(
        fund_name="test_stock_sim",
        underlying_closes=_series([100.0, 101.0, 102.0]),
        underlying_yields=None,
        overwrite_sim_with_index=False,
        save_index=False,
        force_update=True,
    )

    assert list(result.columns) == ["Close", "Change"]
    assert result["Close"].iloc[0] == 1


def test_bond_index_simulator_uses_bond_ladder(monkeypatch) -> None:
    base_df = pd.DataFrame(
        {
            "Close": [1.0, 1.01, 1.02],
            "Change": [None, 0.01, 0.00990099],
        },
        index=pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-03"]),
    )

    monkeypatch.setattr("finbot.services.simulation.bond_index_simulator.is_sufficiently_updated", lambda *_: False)
    monkeypatch.setattr(
        "finbot.services.simulation.bond_index_simulator.bond_ladder_simulator",
        lambda *_args, **_kwargs: base_df.copy(),
    )

    result = bond_index_simulator(
        fund_name="test_bond_sim",
        min_maturity_years=1,
        max_maturity_years=3,
        overwrite_sim_with_index=False,
        save_index=False,
        force_update=True,
    )

    assert len(result) == 3
    assert list(result.columns) == ["Close", "Change"]
    assert result["Close"].iloc[0] == 1
