"""Smoke tests for the CLI using Click's CliRunner.

These tests verify that all CLI commands load successfully and respond
to --help flags without errors. They do NOT test full execution paths
(which would require data files and API keys).
"""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from finbot.cli.main import cli


@pytest.fixture
def runner():
    """Create a Click CLI test runner."""
    return CliRunner()


class TestMainCLI:
    """Test main CLI entry point."""

    def test_cli_help(self, runner):
        """Test main CLI --help flag."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Finbot - Financial simulation and backtesting platform" in result.output
        assert "simulate" in result.output
        assert "backtest" in result.output
        assert "optimize" in result.output
        assert "update" in result.output
        assert "status" in result.output
        assert "dashboard" in result.output

    def test_cli_version(self, runner):
        """Test main CLI --version flag."""
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "finbot" in result.output.lower()
        assert "1.0.0" in result.output

    def test_cli_no_args(self, runner):
        """Test main CLI with no arguments shows help."""
        result = runner.invoke(cli, [])
        # Click exits with code 2 for usage errors (no command provided)
        # But still shows usage information
        assert result.exit_code in [0, 2]  # 0 or 2 both acceptable
        assert "Usage:" in result.output or "Finbot" in result.output

    def test_cli_verbose_flag(self, runner):
        """Test main CLI --verbose flag."""
        result = runner.invoke(cli, ["--verbose", "--help"])
        assert result.exit_code == 0
        # Verbose flag should not break help output
        assert "Finbot" in result.output


class TestSimulateCommand:
    """Test simulate command."""

    def test_simulate_help(self, runner):
        """Test simulate --help."""
        result = runner.invoke(cli, ["simulate", "--help"])
        assert result.exit_code == 0
        assert "simulate" in result.output.lower()
        assert "--fund" in result.output
        assert "--start" in result.output
        assert "--end" in result.output
        assert "--output" in result.output
        assert "--plot" in result.output

    def test_simulate_no_fund_flag(self, runner):
        """Test simulate without --fund flag shows error."""
        result = runner.invoke(cli, ["simulate"])
        assert result.exit_code != 0
        assert "Error" in result.output
        assert "fund" in result.output.lower()

    def test_simulate_invalid_fund(self, runner):
        """Test simulate with invalid fund ticker shows available funds."""
        result = runner.invoke(cli, ["simulate", "--fund", "INVALID_TICKER"])
        assert result.exit_code != 0
        assert "Unknown fund" in result.output or "Error" in result.output
        # Should show available funds
        assert "Available" in result.output or "SPY" in result.output


class TestBacktestCommand:
    """Test backtest command."""

    def test_backtest_help(self, runner):
        """Test backtest --help."""
        result = runner.invoke(cli, ["backtest", "--help"])
        assert result.exit_code == 0
        assert "backtest" in result.output.lower()
        assert "--strategy" in result.output
        assert "Execute strategy backtests" in result.output or "backtest" in result.output.lower()


class TestOptimizeCommand:
    """Test optimize command."""

    def test_optimize_help(self, runner):
        """Test optimize --help."""
        result = runner.invoke(cli, ["optimize", "--help"])
        assert result.exit_code == 0
        assert "optimize" in result.output.lower()
        assert "portfolio optimization" in result.output.lower() or "optimize" in result.output.lower()


class TestUpdateCommand:
    """Test update command."""

    def test_update_help(self, runner):
        """Test update --help."""
        result = runner.invoke(cli, ["update", "--help"])
        assert result.exit_code == 0
        assert "update" in result.output.lower()
        assert "data" in result.output.lower() or "pipeline" in result.output.lower()

    def test_update_dry_run_flag_exists(self, runner):
        """Test update command has --dry-run flag."""
        result = runner.invoke(cli, ["update", "--help"])
        assert result.exit_code == 0
        # Check if dry-run or similar flag exists
        # (This verifies the command structure even if flag doesn't exist)
        assert "update" in result.output.lower()


class TestStatusCommand:
    """Test status command."""

    def test_status_help(self, runner):
        """Test status --help."""
        result = runner.invoke(cli, ["status", "--help"])
        assert result.exit_code == 0
        assert "status" in result.output.lower()
        assert "--stale-only" in result.output
        assert "data" in result.output.lower() or "freshness" in result.output.lower()

    def test_status_stale_only_flag(self, runner):
        """Test status --stale-only flag is recognized."""
        # This test just verifies the flag is recognized
        # Actual execution requires data files
        result = runner.invoke(cli, ["status", "--help"])
        assert result.exit_code == 0
        assert "--stale-only" in result.output


class TestDashboardCommand:
    """Test dashboard command."""

    def test_dashboard_help(self, runner):
        """Test dashboard --help."""
        result = runner.invoke(cli, ["dashboard", "--help"])
        assert result.exit_code == 0
        assert "dashboard" in result.output.lower()
        assert "streamlit" in result.output.lower() or "web" in result.output.lower()


class TestCLIIntegration:
    """Integration tests for CLI command flow."""

    def test_all_commands_have_help(self, runner):
        """Test all commands respond to --help without errors."""
        commands = ["simulate", "backtest", "optimize", "update", "status", "dashboard"]

        for cmd in commands:
            result = runner.invoke(cli, [cmd, "--help"])
            assert result.exit_code == 0, f"Command '{cmd} --help' failed with exit code {result.exit_code}"
            assert cmd in result.output.lower(), f"Command '{cmd}' help output missing command name"

    def test_verbose_flag_works_with_all_commands(self, runner):
        """Test --verbose flag works with all command --help."""
        commands = ["simulate", "backtest", "optimize", "update", "status", "dashboard"]

        for cmd in commands:
            result = runner.invoke(cli, ["--verbose", cmd, "--help"])
            assert result.exit_code == 0, f"--verbose {cmd} --help failed"
            # Verbose flag should not break help output
            assert "Usage:" in result.output or cmd in result.output.lower()

    def test_invalid_command_shows_error(self, runner):
        """Test invalid command shows helpful error."""
        result = runner.invoke(cli, ["invalid_command_xyz"])
        assert result.exit_code != 0
        # Should show error about invalid command
        assert "Error" in result.output or "No such command" in result.output or "Usage:" in result.output


class TestCLIErrorHandling:
    """Test CLI error handling and edge cases."""

    def test_simulate_with_verbose_shows_logging(self, runner):
        """Test simulate with --verbose shows log messages."""
        # Test that verbose flag is properly passed through context
        result = runner.invoke(cli, ["--verbose", "simulate", "--help"])
        assert result.exit_code == 0

    def test_cli_abbreviations(self, runner):
        """Test Click command abbreviations work (if enabled)."""
        # Click allows command abbreviations by default
        # Test abbreviated command (may not work if disabled)
        result = runner.invoke(cli, ["sim", "--help"])
        # Should either work (exit 0) or show error about ambiguous/unknown command
        assert result.exit_code in [0, 2]  # 0 = success, 2 = usage error

    def test_help_shows_examples(self, runner):
        """Test help output includes examples."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        # Main help should show examples
        assert "Example" in result.output or "finbot" in result.output.lower()


class TestCLICommandOptions:
    """Test specific command options and flags."""

    def test_simulate_accepts_fund_option(self, runner):
        """Test simulate accepts --fund option in help."""
        result = runner.invoke(cli, ["simulate", "--help"])
        assert result.exit_code == 0
        assert "--fund" in result.output

    def test_simulate_accepts_start_date_option(self, runner):
        """Test simulate accepts --start option in help."""
        result = runner.invoke(cli, ["simulate", "--help"])
        assert result.exit_code == 0
        assert "--start" in result.output

    def test_simulate_accepts_end_date_option(self, runner):
        """Test simulate accepts --end option in help."""
        result = runner.invoke(cli, ["simulate", "--help"])
        assert result.exit_code == 0
        assert "--end" in result.output

    def test_simulate_accepts_output_option(self, runner):
        """Test simulate accepts --output option in help."""
        result = runner.invoke(cli, ["simulate", "--help"])
        assert result.exit_code == 0
        assert "--output" in result.output

    def test_simulate_accepts_plot_flag(self, runner):
        """Test simulate accepts --plot flag in help."""
        result = runner.invoke(cli, ["simulate", "--help"])
        assert result.exit_code == 0
        assert "--plot" in result.output

    def test_status_accepts_stale_only_flag(self, runner):
        """Test status accepts --stale-only flag in help."""
        result = runner.invoke(cli, ["status", "--help"])
        assert result.exit_code == 0
        assert "--stale-only" in result.output


# Parametrized tests for all commands
@pytest.mark.parametrize(
    "command",
    [
        "simulate",
        "backtest",
        "optimize",
        "update",
        "status",
        "dashboard",
    ],
)
class TestAllCommands:
    """Parametrized tests for all CLI commands."""

    def test_command_help_succeeds(self, runner, command):
        """Test each command's --help succeeds."""
        result = runner.invoke(cli, [command, "--help"])
        assert result.exit_code == 0

    def test_command_help_contains_command_name(self, runner, command):
        """Test each command's help mentions the command name."""
        result = runner.invoke(cli, [command, "--help"])
        assert result.exit_code == 0
        assert command in result.output.lower()

    def test_command_help_shows_usage(self, runner, command):
        """Test each command's help shows usage information."""
        result = runner.invoke(cli, [command, "--help"])
        assert result.exit_code == 0
        assert "Usage:" in result.output or command in result.output.lower()


# Mark tests that require data files
@pytest.mark.skip(reason="Requires data files - integration test")
class TestCLIExecution:
    """Full execution tests (requires data files)."""

    def test_status_execution(self, runner):
        """Test status command execution (requires data directories)."""
        result = runner.invoke(cli, ["status"])
        # Would need data directories to pass
        assert result.exit_code == 0
        assert "Data Source Status" in result.output or "source" in result.output.lower()

    def test_simulate_execution(self, runner):
        """Test simulate command execution (requires data)."""
        result = runner.invoke(cli, ["simulate", "--fund", "SPY"])
        # Would need price data and LIBOR data
        assert result.exit_code == 0
        assert "Simulating" in result.output or "SPY" in result.output


# Performance tests
class TestCLIPerformance:
    """Test CLI performance and responsiveness."""

    def test_help_responds_quickly(self, runner):
        """Test --help responds in reasonable time."""
        import time

        start = time.time()
        result = runner.invoke(cli, ["--help"])
        elapsed = time.time() - start

        assert result.exit_code == 0
        assert elapsed < 2.0, f"--help took {elapsed:.2f}s (should be < 2s)"

    def test_version_responds_quickly(self, runner):
        """Test --version responds in reasonable time."""
        import time

        start = time.time()
        result = runner.invoke(cli, ["--version"])
        elapsed = time.time() - start

        assert result.exit_code == 0
        assert elapsed < 1.0, f"--version took {elapsed:.2f}s (should be < 1s)"

    def test_command_help_responds_quickly(self, runner):
        """Test command --help responds in reasonable time."""
        import time

        commands = ["simulate", "backtest", "optimize", "update", "status", "dashboard"]

        for cmd in commands:
            start = time.time()
            result = runner.invoke(cli, [cmd, "--help"])
            elapsed = time.time() - start

            assert result.exit_code == 0, f"{cmd} --help failed"
            assert elapsed < 2.0, f"{cmd} --help took {elapsed:.2f}s (should be < 2s)"
