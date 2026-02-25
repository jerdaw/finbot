"""Unit tests for get_fred_data (mocked, no network or filesystem I/O)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pandas as pd
import pandas_datareader as pdr
import pytest


class TestGetFredDataValidation:
    """Tests for get_fred_data() argument validation."""

    def test_empty_list_raises_value_error(self) -> None:
        from finbot.utils.data_collection_utils.fred.get_fred_data import get_fred_data

        with pytest.raises(ValueError, match="At least one symbol"):
            get_fred_data([])

    def test_empty_string_raises_value_error(self) -> None:
        from finbot.utils.data_collection_utils.fred.get_fred_data import get_fred_data

        with pytest.raises(ValueError, match="At least one symbol"):
            get_fred_data("")

    def test_single_string_normalised_to_list(self) -> None:
        with patch("finbot.utils.data_collection_utils.fred.get_fred_data.get_pdr_base") as mock_base:
            mock_base.return_value = pd.DataFrame()

            from finbot.utils.data_collection_utils.fred.get_fred_data import get_fred_data

            get_fred_data("SP500")

            call_kwargs = mock_base.call_args
            assert call_kwargs.kwargs["symbols"] == ["SP500"]


class TestGetFredDataMocked:
    """Tests for get_fred_data() with get_pdr_base patched."""

    @pytest.fixture(autouse=True)
    def _mock_base(self) -> None:
        self._df = pd.DataFrame({"SP500": [1.0, 2.0]})
        patcher = patch("finbot.utils.data_collection_utils.fred.get_fred_data.get_pdr_base")
        self.mock_base: MagicMock = patcher.start()
        self.mock_base.return_value = self._df
        yield
        patcher.stop()

    def _call(self, **kwargs):  # type: ignore[no-untyped-def]
        from finbot.utils.data_collection_utils.fred.get_fred_data import get_fred_data

        return get_fred_data(**kwargs)

    def test_returns_pdr_base_result_unchanged(self) -> None:
        result = self._call(symbols=["SP500"])
        assert result is self._df

    def test_passes_fred_reader_class(self) -> None:
        self._call(symbols=["SP500"])
        call_kwargs = self.mock_base.call_args.kwargs
        assert call_kwargs["pdr_reader_class"] is pdr.fred.FredReader

    def test_passes_start_date(self) -> None:
        import datetime

        start = datetime.date(2010, 1, 1)
        self._call(symbols=["SP500"], start_date=start)
        call_kwargs = self.mock_base.call_args.kwargs
        assert call_kwargs["start_date"] == start

    def test_passes_end_date(self) -> None:
        import datetime

        end = datetime.date(2023, 12, 31)
        self._call(symbols=["SP500"], end_date=end)
        call_kwargs = self.mock_base.call_args.kwargs
        assert call_kwargs["end_date"] == end

    def test_passes_check_update_flag(self) -> None:
        self._call(symbols=["SP500"], check_update=True)
        call_kwargs = self.mock_base.call_args.kwargs
        assert call_kwargs["check_update"] is True

    def test_passes_force_update_flag(self) -> None:
        self._call(symbols=["SP500"], force_update=True)
        call_kwargs = self.mock_base.call_args.kwargs
        assert call_kwargs["force_update"] is True

    def test_passes_fred_data_dir_as_save_dir(self) -> None:
        from finbot.constants.path_constants import FRED_DATA_DIR

        self._call(symbols=["SP500"])
        call_kwargs = self.mock_base.call_args.kwargs
        assert call_kwargs["save_dir"] == FRED_DATA_DIR
