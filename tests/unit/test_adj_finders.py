"""Unit tests for simulation adjustment finders (correlation optimization)."""

import numpy as np
import pandas as pd

from finbot.services.simulation.adj_finders import (
    get_best_corr_iterative,
    get_best_corr_search,
)


class TestGetBestCorrIterative:
    """Tests for get_best_corr_iterative()."""

    def test_returns_tuple_of_floats(self):
        sim = pd.Series(np.cumsum(np.random.default_rng(42).normal(0, 0.01, 100)) + 100)
        actual = sim * 1.01  # Slightly different
        adj, corr = get_best_corr_iterative(sim, actual, n_steps=100)
        assert isinstance(adj, float)
        assert isinstance(corr, float)

    def test_high_correlation_for_similar_series(self):
        rng = np.random.default_rng(42)
        base = np.cumsum(rng.normal(0.001, 0.01, 200)) + 100
        sim = pd.Series(base)
        actual = pd.Series(base * 1.001)
        _adj, corr = get_best_corr_iterative(sim, actual, n_steps=500)
        assert corr > 0.9

    def test_explicit_start_stop(self):
        sim = pd.Series(np.cumsum(np.random.default_rng(42).normal(0, 0.01, 100)) + 100)
        actual = sim * 1.01
        adj, _corr = get_best_corr_iterative(sim, actual, start=-0.01, stop=0.01, n_steps=50)
        assert -0.01 <= adj <= 0.01

    def test_default_start_stop_uses_mean(self):
        sim = pd.Series(np.cumsum(np.random.default_rng(42).normal(0, 0.01, 100)) + 100)
        actual = sim * 1.01
        adj, _corr = get_best_corr_iterative(sim, actual, n_steps=50)
        assert isinstance(adj, float)

    def test_n_steps_affects_resolution(self):
        rng = np.random.default_rng(42)
        base = np.cumsum(rng.normal(0.001, 0.01, 200)) + 100
        sim = pd.Series(base)
        actual = pd.Series(base + rng.normal(0, 0.5, 200))
        _adj_low, corr_low = get_best_corr_iterative(sim, actual, n_steps=10)
        _adj_high, corr_high = get_best_corr_iterative(sim, actual, n_steps=1000)
        assert corr_high >= corr_low - 0.01  # Higher resolution should be at least as good


class TestGetBestCorrSearch:
    """Tests for get_best_corr_search()."""

    def test_returns_tuple_of_floats(self):
        sim = pd.Series(np.cumsum(np.random.default_rng(42).normal(0, 0.01, 100)) + 100)
        actual = sim * 1.01
        adj, corr = get_best_corr_search(sim, actual, max_depth=5, n_parts=4)
        assert isinstance(adj, float)
        assert isinstance(corr, float)

    def test_convergence_with_depth(self):
        rng = np.random.default_rng(42)
        base = np.cumsum(rng.normal(0.001, 0.01, 200)) + 100
        sim = pd.Series(base)
        actual = pd.Series(base * 1.002)
        _adj, corr = get_best_corr_search(sim, actual, max_depth=10, n_parts=4)
        assert corr > 0.9

    def test_explicit_bounds(self):
        sim = pd.Series(np.cumsum(np.random.default_rng(42).normal(0, 0.01, 100)) + 100)
        actual = sim * 1.01
        adj, _corr = get_best_corr_search(sim, actual, start=-0.005, stop=0.005, max_depth=5)
        assert -0.005 <= adj <= 0.005

    def test_small_max_depth(self):
        sim = pd.Series(np.cumsum(np.random.default_rng(42).normal(0, 0.01, 100)) + 100)
        actual = sim * 1.01
        _adj, corr = get_best_corr_search(sim, actual, max_depth=1, n_parts=4)
        assert isinstance(corr, float)
