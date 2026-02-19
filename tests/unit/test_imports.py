"""Smoke tests: verify key modules can be imported without errors."""


def test_import_config():
    from finbot.config import logger, settings

    assert settings is not None
    assert logger is not None


def test_import_settings_accessors():
    from finbot.config import settings_accessors

    assert settings_accessors is not None
    assert hasattr(settings_accessors, "MAX_THREADS")
    assert isinstance(settings_accessors.MAX_THREADS, int)


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


def test_import_dashboard_app():
    import finbot.dashboard.app  # noqa: F401


def test_import_dashboard_components():
    from finbot.dashboard.components.charts import (
        create_bar_chart,
        create_drawdown_chart,
        create_fan_chart,
        create_heatmap,
        create_histogram_chart,
        create_time_series_chart,
    )

    assert callable(create_time_series_chart)
    assert callable(create_histogram_chart)
    assert callable(create_bar_chart)
    assert callable(create_heatmap)
    assert callable(create_fan_chart)
    assert callable(create_drawdown_chart)


def test_import_dashboard_sidebar():
    from finbot.dashboard.components.sidebar import asset_selector, date_range_selector, fund_selector

    assert callable(fund_selector)
    assert callable(asset_selector)
    assert callable(date_range_selector)


def test_import_dashboard_cli():
    from finbot.cli.commands.dashboard import dashboard

    assert callable(dashboard)


def test_import_dual_momentum():
    from finbot.services.backtesting.strategies.dual_momentum import DualMomentum

    assert DualMomentum is not None


def test_import_risk_parity():
    from finbot.services.backtesting.strategies.risk_parity import RiskParity

    assert RiskParity is not None


def test_import_multi_asset_monte_carlo():
    from finbot.services.simulation.monte_carlo.multi_asset_monte_carlo import multi_asset_monte_carlo

    assert callable(multi_asset_monte_carlo)


def test_import_inflation_adjusted_returns():
    from finbot.utils.finance_utils.get_inflation_adjusted_returns import get_inflation_adjusted_returns

    assert callable(get_inflation_adjusted_returns)


def test_import_health_economics():
    from finbot.services.health_economics import (
        HealthIntervention,
        cost_effectiveness_analysis,
        optimize_treatment,
        simulate_qalys,
    )

    assert HealthIntervention is not None
    assert callable(simulate_qalys)
    assert callable(cost_effectiveness_analysis)
    assert callable(optimize_treatment)


def test_import_core_contracts():
    from finbot.core.contracts import BacktestEngine, BacktestRunResult, MarketDataProvider

    assert BacktestEngine is not None
    assert MarketDataProvider is not None
    assert BacktestRunResult is not None


def test_import_backtrader_adapter():
    from finbot.services.backtesting.adapters import BacktraderAdapter

    assert BacktraderAdapter is not None


def test_import_nautilus_adapter():
    from finbot.adapters.nautilus import NautilusAdapter

    assert NautilusAdapter is not None
