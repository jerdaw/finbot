"""Tests for approximate overnight LIBOR simulation helper."""

from __future__ import annotations

import pandas as pd
import pytest

from finbot.services.simulation.approximate_overnight_libor import approximate_overnight_libor


def test_approximate_overnight_libor_composes_columns_and_interpolates(monkeypatch) -> None:
    idx = pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-03"])
    yield_history = pd.DataFrame(
        {
            "SOFR": [1.0, None, None],
            "DFF": [None, 1.1, None],
            "TB3MS": [None, None, 1.2],
        },
        index=idx,
    )

    monkeypatch.setattr(
        "finbot.services.simulation.approximate_overnight_libor.get_yields",
        lambda: yield_history,
    )

    result = approximate_overnight_libor(save=False)
    assert result.name == "Yield"
    assert len(result) == 3
    assert result.notna().all()


def test_approximate_overnight_libor_raises_when_no_columns(monkeypatch) -> None:
    idx = pd.to_datetime(["2020-01-01", "2020-01-02"])
    empty = pd.DataFrame(index=idx)
    monkeypatch.setattr("finbot.services.simulation.approximate_overnight_libor.get_yields", lambda: empty)

    with pytest.raises(ValueError, match="No yield data available"):
        approximate_overnight_libor(save=False)
