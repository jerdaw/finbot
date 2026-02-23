"""Tests for bond ladder simulator orchestration with deterministic mocks."""

from __future__ import annotations

import pandas as pd

from finbot.services.simulation.bond_ladder.bond_ladder_simulator import bond_ladder_simulator


def _yield_history() -> pd.DataFrame:
    index = pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-03"])
    return pd.DataFrame(
        {
            "DGS1": [1.0, 1.1, 1.2],
            "DGS2": [1.2, 1.3, 1.4],
        },
        index=index,
    )


def test_bond_ladder_simulator_returns_scaled_fund(monkeypatch) -> None:
    yh = _yield_history()

    monkeypatch.setattr(
        "finbot.services.simulation.bond_ladder.bond_ladder_simulator.get_periods_per_year",
        lambda _df: 1,
    )
    monkeypatch.setattr(
        "finbot.services.simulation.bond_ladder.bond_ladder_simulator.build_yield_curve",
        lambda *_args, **_kwargs: [0.01, 0.02],
    )
    monkeypatch.setattr(
        "finbot.services.simulation.bond_ladder.bond_ladder_simulator.make_annual_ladder",
        lambda *_args, **_kwargs: object(),
    )
    monkeypatch.setattr(
        "finbot.services.simulation.bond_ladder.bond_ladder_simulator.loop",
        lambda *_args, **_kwargs: {
            yh.index[0]: 100.0,
            yh.index[1]: 102.0,
            yh.index[2]: 103.0,
        },
    )

    fund = bond_ladder_simulator(
        min_maturity_years=1,
        max_maturity_years=2,
        yield_history=yh,
        save_db=False,
    )

    assert list(fund.columns) == ["Close", "Change"]
    assert len(fund) == 3
    assert fund["Close"].iloc[0] == 1.0
    assert fund.index.equals(yh.index)


def test_bond_ladder_simulator_save_db_calls_writer(monkeypatch) -> None:
    yh = _yield_history()
    save_calls: list[pd.DataFrame] = []

    monkeypatch.setattr(
        "finbot.services.simulation.bond_ladder.bond_ladder_simulator.get_periods_per_year",
        lambda _df: 1,
    )
    monkeypatch.setattr(
        "finbot.services.simulation.bond_ladder.bond_ladder_simulator.build_yield_curve",
        lambda *_args, **_kwargs: [0.01, 0.02],
    )
    monkeypatch.setattr(
        "finbot.services.simulation.bond_ladder.bond_ladder_simulator.make_annual_ladder",
        lambda *_args, **_kwargs: object(),
    )
    monkeypatch.setattr(
        "finbot.services.simulation.bond_ladder.bond_ladder_simulator.loop",
        lambda *_args, **_kwargs: {
            yh.index[0]: 100.0,
            yh.index[1]: 102.0,
            yh.index[2]: 103.0,
        },
    )
    monkeypatch.setattr(
        "finbot.services.simulation.bond_ladder.bond_ladder_simulator._save_fund_to_db",
        lambda df: save_calls.append(df.copy()),
    )

    bond_ladder_simulator(
        min_maturity_years=1,
        max_maturity_years=2,
        yield_history=yh,
        save_db=True,
    )

    assert len(save_calls) == 1
    assert len(save_calls[0]) == 3
