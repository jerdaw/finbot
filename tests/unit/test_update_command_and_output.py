from __future__ import annotations

import contextlib
import sys
import types

import pandas as pd
import pytest
from click.testing import CliRunner

from finbot.cli.commands.update import update
from finbot.cli.utils.output import save_output


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def fake_audit(monkeypatch: pytest.MonkeyPatch) -> None:
    @contextlib.contextmanager
    def _noop(*args, **kwargs):
        yield

    monkeypatch.setitem(update.callback.__globals__, "audit_operation", _noop)


def _install_fake_update_daily(monkeypatch: pytest.MonkeyPatch, call_log: list[str]) -> None:
    module = types.ModuleType("scripts.update_daily")

    def _mark(name: str):
        def _fn() -> None:
            call_log.append(name)

        return _fn

    module.update_yf_price_histories = _mark("update_yf_price_histories")
    module.update_fred_data = _mark("update_fred_data")
    module.update_shiller_data = _mark("update_shiller_data")
    module.approximate_overnight_libor = _mark("approximate_overnight_libor")
    module.sim_sp500tr = _mark("sim_sp500tr")
    module.sim_idcot20tr = _mark("sim_idcot20tr")
    module.sim_idcot7tr = _mark("sim_idcot7tr")
    module.sim_idcot1tr = _mark("sim_idcot1tr")

    for fund_name in [
        "sim_spy",
        "sim_sso",
        "sim_upro",
        "sim_qqq",
        "sim_qld",
        "sim_tqqq",
        "sim_tlt",
        "sim_ubt",
        "sim_tmf",
        "sim_ief",
        "sim_ust",
        "sim_tyd",
        "sim_shy",
        "sim_2x_stt",
        "sim_3x_stt",
        "sim_ntsx",
    ]:
        setattr(module, fund_name, _mark(fund_name))

    monkeypatch.setitem(sys.modules, "scripts.update_daily", module)


def test_update_dry_run_prints_plan(runner: CliRunner, fake_audit) -> None:
    result = runner.invoke(update, ["--dry-run"], obj={"verbose": False, "trace_id": "trace-1"})

    assert result.exit_code == 0
    assert "DRY RUN MODE" in result.output
    assert "Would execute daily update pipeline" in result.output
    assert "Use without --dry-run to execute" in result.output


def test_update_skip_paths_complete(runner: CliRunner, fake_audit) -> None:
    result = runner.invoke(
        update,
        ["--skip-prices", "--skip-simulations"],
        obj={"verbose": False, "trace_id": "trace-2"},
    )

    assert result.exit_code == 0
    assert "Skipping price and economic data updates" in result.output
    assert "Skipping simulations" in result.output
    assert "Daily update pipeline complete" in result.output


def test_update_full_run_executes_all_steps(runner: CliRunner, fake_audit, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []
    _install_fake_update_daily(monkeypatch, calls)

    result = runner.invoke(update, [], obj={"verbose": True, "trace_id": "trace-3"})

    assert result.exit_code == 0
    assert "Running daily update pipeline" in result.output
    assert "Price histories updated" in result.output
    assert "Economic data updated" in result.output
    assert "Index simulations complete" in result.output
    assert "Fund simulations complete (16 funds)" in result.output
    assert "Daily update pipeline complete" in result.output
    assert len(calls) == 24
    assert calls[:4] == [
        "update_yf_price_histories",
        "update_fred_data",
        "update_shiller_data",
        "approximate_overnight_libor",
    ]


def test_update_continues_when_substep_fails(runner: CliRunner, fake_audit, monkeypatch: pytest.MonkeyPatch) -> None:
    module = types.ModuleType("scripts.update_daily")

    def _raise() -> None:
        raise RuntimeError("boom")

    def _ok() -> None:
        return None

    module.update_yf_price_histories = _raise
    module.update_fred_data = _ok
    module.update_shiller_data = _ok
    module.approximate_overnight_libor = _ok
    module.sim_sp500tr = _ok
    module.sim_idcot20tr = _ok
    module.sim_idcot7tr = _ok
    module.sim_idcot1tr = _ok
    for fund_name in [
        "sim_spy",
        "sim_sso",
        "sim_upro",
        "sim_qqq",
        "sim_qld",
        "sim_tqqq",
        "sim_tlt",
        "sim_ubt",
        "sim_tmf",
        "sim_ief",
        "sim_ust",
        "sim_tyd",
        "sim_shy",
        "sim_2x_stt",
        "sim_3x_stt",
        "sim_ntsx",
    ]:
        setattr(module, fund_name, _ok)

    monkeypatch.setitem(sys.modules, "scripts.update_daily", module)

    result = runner.invoke(update, [], obj={"verbose": False, "trace_id": "trace-4"})

    assert result.exit_code == 0
    assert "Price history update failed: boom" in result.output
    assert "Daily update pipeline complete" in result.output


def test_save_output_routes_by_extension(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, str]] = []

    def _csv(self, path, *args, **kwargs):
        calls.append(("csv", str(path)))

    def _parquet(self, path, *args, **kwargs):
        calls.append(("parquet", str(path)))

    def _json(self, path, *args, **kwargs):
        calls.append(("json", str(path)))

    monkeypatch.setattr(pd.DataFrame, "to_csv", _csv, raising=True)
    monkeypatch.setattr(pd.DataFrame, "to_parquet", _parquet, raising=True)
    monkeypatch.setattr(pd.DataFrame, "to_json", _json, raising=True)

    df = pd.DataFrame({"a": [1, 2]})
    save_output(df, str(tmp_path / "out.csv"), verbose=True)
    save_output(df, str(tmp_path / "out.parquet"), verbose=False)
    save_output(df, str(tmp_path / "out.json"), verbose=False)
    save_output(df, str(tmp_path / "out.unknown"), verbose=False)

    assert calls[0][0] == "csv"
    assert calls[1][0] == "parquet"
    assert calls[2][0] == "json"
    assert calls[3][0] == "csv"
    assert calls[3][1].endswith(".csv")


def test_save_output_raises_on_write_failure(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    def _raise(self, *args, **kwargs):
        raise OSError("write failed")

    monkeypatch.setattr(pd.DataFrame, "to_csv", _raise, raising=True)

    with pytest.raises(OSError, match="write failed"):
        save_output(pd.DataFrame({"a": [1]}), str(tmp_path / "out.csv"))
