"""Unit tests for tracked collections (MSCI, FRED, Funds, CollectionTrackerBase)."""

from __future__ import annotations

import datetime
from decimal import Decimal
from pathlib import Path

import pandas as pd
import pytest

from finbot.constants.tracked_collections.tracked_msci import TRACKED_MSCI


class TestTrackedMSCI:
    """Tests for TRACKED_MSCI data."""

    def test_is_list_of_dicts(self):
        assert isinstance(TRACKED_MSCI, list)
        assert all(isinstance(entry, dict) for entry in TRACKED_MSCI)

    def test_entries_have_name_and_id(self):
        for entry in TRACKED_MSCI:
            assert "name" in entry
            assert "id" in entry

    def test_known_indexes_present(self):
        names = {e["name"] for e in TRACKED_MSCI}
        assert "ACWI" in names
        assert "EAFE" in names
        assert "CANADA" in names

    def test_ids_are_unique(self):
        ids = [e["id"] for e in TRACKED_MSCI]
        assert len(ids) == len(set(ids))


class TestFredData:
    """Tests for FredData dataclass."""

    def test_valid_creation(self):
        from finbot.constants.tracked_collections.tracked_fred import FredData

        fd = FredData(
            symbol="DGS10",
            name="10-Year Treasury Yield",
            category="Interest Rates",
            frequency="daily",
            seasonally_adjusted=False,
            start_date="1962-01-02",
            units="Percent",
        )
        assert fd.symbol == "DGS10"

    def test_symbol_uppercased(self):
        from finbot.constants.tracked_collections.tracked_fred import FredData

        fd = FredData(
            symbol="dgs10",
            name="10-Year Treasury Yield",
            category="Interest Rates",
            frequency="daily",
            seasonally_adjusted=False,
            start_date="1962-01-02",
            units="Percent",
        )
        assert fd.symbol == "DGS10"

    def test_invalid_symbol_raises(self):
        from finbot.constants.tracked_collections.tracked_fred import FredData

        with pytest.raises(ValueError, match="uppercase"):
            FredData(
                symbol="dgs-10!",
                name="Test",
                category="Interest Rates",
                frequency="daily",
                seasonally_adjusted=False,
                start_date="2000-01-01",
                units="Percent",
            )

    def test_invalid_frequency_raises(self):
        from finbot.constants.tracked_collections.tracked_fred import FredData

        with pytest.raises(ValueError, match="Frequency"):
            FredData(
                symbol="TEST",
                name="Test",
                category="Interest Rates",
                frequency="minutely",
                seasonally_adjusted=False,
                start_date="2000-01-01",
                units="Percent",
            )

    def test_invalid_category_raises(self):
        from finbot.constants.tracked_collections.tracked_fred import FredData

        with pytest.raises(ValueError, match="Category"):
            FredData(
                symbol="TEST",
                name="Test",
                category="Invalid Category",
                frequency="daily",
                seasonally_adjusted=False,
                start_date="2000-01-01",
                units="Percent",
            )

    def test_to_dict(self):
        from finbot.constants.tracked_collections.tracked_fred import FredData

        fd = FredData(
            symbol="DFF",
            name="Federal Funds Rate",
            category="Interest Rates",
            frequency="daily",
            seasonally_adjusted=False,
            start_date="1954-07-01",
            units="Percent",
        )
        d = fd.to_dict()
        assert d["symbol"] == "DFF"
        assert "name" in d

    def test_to_df(self):
        from finbot.constants.tracked_collections.tracked_fred import FredData

        fd = FredData(
            symbol="DFF",
            name="Federal Funds Rate",
            category="Interest Rates",
            frequency="daily",
            seasonally_adjusted=False,
            start_date="1954-07-01",
            units="Percent",
        )
        df = fd.to_df()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1

    def test_get_start_as_date(self):
        from finbot.constants.tracked_collections.tracked_fred import FredData

        fd = FredData(
            symbol="DFF",
            name="Federal Funds Rate",
            category="Interest Rates",
            frequency="daily",
            seasonally_adjusted=False,
            start_date="1954-07-01",
            units="Percent",
        )
        d = fd.get_start_as_date()
        assert isinstance(d, datetime.date)
        assert d == datetime.date(1954, 7, 1)


class TestFundData:
    """Tests for FundData dataclass."""

    def _make_fund(self, **overrides):
        from finbot.constants.tracked_collections.tracked_funds import FundData

        defaults = {
            "symbol": "SPY",
            "name": "SPDR S&P 500 ETF Trust",
            "asset_region": "us",
            "category": "equity",
            "sector": "broad market",
            "issuer": "state street",
            "issuer_region": "us",
            "inception_date": "1993-01-22",
            "mer": "0.09%",
            "leverage_multiple": "1.0",
            "leverage_reset_period": "",
            "underlying_index": "s&p 500",
            "url": "https://example.com",
        }
        defaults.update(overrides)
        return FundData(**defaults)

    def test_valid_creation(self):
        fund = self._make_fund()
        assert fund.symbol == "spy"  # lowercased

    def test_symbol_lowercased(self):
        fund = self._make_fund(symbol="SPY")
        assert fund.symbol == "spy"

    def test_invalid_symbol_raises(self):
        with pytest.raises(ValueError, match="lowercase"):
            self._make_fund(symbol="SPY-X!")

    def test_mer_format_validation(self):
        with pytest.raises(ValueError, match="MER"):
            self._make_fund(mer="0.09")  # missing %

    def test_high_mer_warns(self):
        with pytest.warns(UserWarning, match="greater than 3.00%"):
            self._make_fund(mer="5.00%")

    def test_inception_date_format(self):
        with pytest.raises(ValueError, match="YYYY-MM-DD"):
            self._make_fund(inception_date="01-22-1993")

    def test_get_mer_as_decimal(self):
        fund = self._make_fund(mer="0.09%")
        assert fund.get_mer_as_decimal() == Decimal("0.09") / Decimal("100")

    def test_get_inception_as_date(self):
        fund = self._make_fund(inception_date="1993-01-22")
        d = fund.get_inception_as_date()
        assert d == datetime.date(1993, 1, 22)


class TestCollectionTrackerBase:
    """Tests for CollectionTrackerBase using tmp_path."""

    def _create_csv(self, tmp_path: Path, data: list[dict]) -> Path:
        csv_path = tmp_path / "test.csv"
        df = pd.DataFrame(data)
        df.to_csv(csv_path, index=False)
        return csv_path

    def test_load_csv(self, tmp_path: Path):
        from finbot.constants.tracked_collections._utils import CollectionTrackerBase

        csv_path = self._create_csv(tmp_path, [{"symbol": "B", "name": "Beta"}, {"symbol": "A", "name": "Alpha"}])
        tracker = CollectionTrackerBase(csv_path)
        assert tracker.df.iloc[0]["symbol"] == "A"  # sorted by symbol

    def test_get_all_symbols(self, tmp_path: Path):
        from finbot.constants.tracked_collections._utils import CollectionTrackerBase

        csv_path = self._create_csv(tmp_path, [{"symbol": "C", "name": "C"}, {"symbol": "A", "name": "A"}])
        tracker = CollectionTrackerBase(csv_path)
        assert tracker.get_all_symbols() == ["A", "C"]

    def test_get_symbols_found(self, tmp_path: Path):
        from finbot.constants.tracked_collections._utils import CollectionTrackerBase

        csv_path = self._create_csv(tmp_path, [{"symbol": "X", "name": "Ex"}, {"symbol": "Y", "name": "Why"}])
        tracker = CollectionTrackerBase(csv_path)
        result = tracker.get_symbols("X")
        assert len(result) == 1

    def test_get_symbols_not_found_raises(self, tmp_path: Path):
        from finbot.constants.tracked_collections._utils import CollectionTrackerBase

        csv_path = self._create_csv(tmp_path, [{"symbol": "A", "name": "A"}])
        tracker = CollectionTrackerBase(csv_path)
        with pytest.raises(ValueError, match="do not exist"):
            tracker.get_symbols("Z")

    def test_delete_entry(self, tmp_path: Path):
        from finbot.constants.tracked_collections._utils import CollectionTrackerBase

        csv_path = self._create_csv(tmp_path, [{"symbol": "A", "name": "A"}, {"symbol": "B", "name": "B"}])
        tracker = CollectionTrackerBase(csv_path)
        tracker.delete_entry("A")
        assert "A" not in tracker.get_all_symbols()

    def test_to_df_returns_copy(self, tmp_path: Path):
        from finbot.constants.tracked_collections._utils import CollectionTrackerBase

        csv_path = self._create_csv(tmp_path, [{"symbol": "A", "name": "A"}])
        tracker = CollectionTrackerBase(csv_path)
        df_copy = tracker.to_df()
        df_copy.drop(df_copy.index, inplace=True)
        assert len(tracker.df) == 1  # Original unchanged
