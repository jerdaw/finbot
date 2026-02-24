"""Unit tests for rebalance proportion generator."""

from unittest.mock import patch

from finbot.services.backtesting.gen_rebal_proportions import (
    _parse_prods,
    gen_rebal_proportions,
)


class TestParseProds:
    """Tests for _parse_prods() helper."""

    def test_valid_proportions_sum_to_one(self):
        result = _parse_prods(((0.3, 0.2), (0.3, 0.2)))
        assert result == (0.3, 0.2, 0.3, 0.2)

    def test_invalid_proportions_returns_none(self):
        result = _parse_prods(((0.3, 0.2), (0.1, 0.1)))
        assert result is None

    def test_exact_sum_one(self):
        result = _parse_prods(((0.5,), (0.5,)))
        assert result == (0.5, 0.5)

    def test_close_but_not_one_returns_none(self):
        result = _parse_prods(((0.33, 0.33), (0.33, 0.0)))
        assert result is None  # 0.99 != 1.0


class TestGenRebalProportions:
    """Tests for gen_rebal_proportions()."""

    @patch("finbot.services.backtesting.gen_rebal_proportions.process_map")
    def test_returns_tuple_of_tuples(self, mock_process_map):
        mock_process_map.return_value = [(0.5, 0.5), None, (0.3, 0.7)]
        result = gen_rebal_proportions(0.1, 2, 1)
        assert isinstance(result, tuple)
        assert all(isinstance(r, tuple) for r in result)
        assert len(result) == 2  # None filtered out

    @patch("finbot.services.backtesting.gen_rebal_proportions.process_map")
    def test_filters_none_results(self, mock_process_map):
        mock_process_map.return_value = [None, None, (0.5, 0.5)]
        result = gen_rebal_proportions(0.1, 2, 1)
        assert len(result) == 1
        assert result[0] == (0.5, 0.5)

    @patch("finbot.services.backtesting.gen_rebal_proportions.process_map")
    def test_custom_mins_maxs(self, mock_process_map):
        mock_process_map.return_value = [(0.4, 0.6)]
        result = gen_rebal_proportions(0.1, 2, 1, custom_mins=[0.2, 0.2], custom_maxs=[0.8, 0.8])
        assert len(result) == 1

    @patch("finbot.services.backtesting.gen_rebal_proportions.process_map")
    def test_empty_result_when_all_none(self, mock_process_map):
        mock_process_map.return_value = [None, None]
        result = gen_rebal_proportions(0.1, 2, 1)
        assert result == ()
