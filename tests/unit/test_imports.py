"""Smoke tests: verify key modules can be imported without errors."""


def test_import_config():
    from config import logger, settings

    assert settings is not None
    assert logger is not None


def test_import_config_singleton():
    from config import Config

    assert Config is not None
    assert hasattr(Config, "MAX_THREADS")
    assert isinstance(Config.MAX_THREADS, int)


def test_import_backtest_runner():
    from finbot.services.backtesting.backtest_runner import BacktestRunner

    assert BacktestRunner is not None


def test_import_run_backtest():
    from finbot.services.backtesting.run_backtest import run_backtest

    assert callable(run_backtest)


def test_import_backtest_batch():
    from finbot.services.backtesting.backtest_batch import backtest_batch

    assert callable(backtest_batch)


def test_import_strategies():
    from finbot.services.backtesting.strategies.macd_single import MACDSingle
    from finbot.services.backtesting.strategies.no_rebalance import NoRebalance
    from finbot.services.backtesting.strategies.rebalance import Rebalance
    from finbot.services.backtesting.strategies.sma_crossover import SMACrossover

    assert Rebalance is not None
    assert NoRebalance is not None
    assert SMACrossover is not None
    assert MACDSingle is not None


def test_import_fund_simulator():
    from finbot.services.simulation.fund_simulator import fund_simulator

    assert callable(fund_simulator)


def test_import_bond_ladder_simulator():
    from finbot.services.simulation.bond_ladder.bond_ladder_simulator import bond_ladder_simulator

    assert callable(bond_ladder_simulator)


def test_import_monte_carlo():
    from finbot.services.simulation.monte_carlo.monte_carlo_simulator import monte_carlo_simulator

    assert callable(monte_carlo_simulator)


def test_import_sim_specific_funds():
    from finbot.services.simulation.sim_specific_funds import sim_spy, sim_tqqq, sim_upro

    assert callable(sim_spy)
    assert callable(sim_upro)
    assert callable(sim_tqqq)


def test_import_sim_specific_indexes():
    from finbot.services.simulation.sim_specific_bond_indexes import sim_idcot20tr
    from finbot.services.simulation.sim_specific_stock_indexes import sim_nd100tr, sim_sp500tr

    assert callable(sim_sp500tr)
    assert callable(sim_nd100tr)
    assert callable(sim_idcot20tr)


def test_import_dca_optimizer():
    from finbot.services.optimization.dca_optimizer import dca_optimizer

    assert callable(dca_optimizer)


def test_import_rebalance_optimizer():
    from finbot.services.optimization.rebalance_optimizer import RebalanceOptimizer

    assert RebalanceOptimizer is not None


def test_import_update_daily():
    from scripts.update_daily import update_daily

    assert callable(update_daily)
