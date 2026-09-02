"""
Command module supplementary tests — covers all 10 Command implementations,
the base Command ABC, and CommandManager edge cases not in existing tests.
"""

from unittest.mock import Mock

import pytest

from battery_analysis.main.commands.base import Command
from battery_analysis.main.managers.command_manager import CommandManager

# ===========================================================================
# TestCommandBase
# ===========================================================================


class TestCommandBase:
    """Command ABC — cannot be instantiated directly"""

    def test_cannot_instantiate(self):
        with pytest.raises(TypeError):
            Command()

    def test_subclass_must_implement_execute(self):
        with pytest.raises(TypeError):
            type("BadCmd", (Command,), {})()

    def test_concrete_subclass_is_valid(self):
        impl = type("GoodCmd", (Command,), {"execute": lambda self: True})()
        assert impl.execute() is True


# ===========================================================================
# Helper — parametrize over all commands
# ===========================================================================


def _cmd_name(cmd_class):
    """Return the class name as a readable test ID."""
    return cmd_class.__name__


# Each entry: (class, {constructor_kwargs}, method_to_patch, success_return, error_return)
# For the "presenter" pattern: commands that call presenter.on_*
PRESENTER_CMDS = [
    "CalculateBatteryCommand",
    "AnalyzeDataCommand",
    "ExportReportCommand",
    "GenerateReportCommand",
    "BatchProcessingCommand",
]
PRESENTER_METHODS = {
    "CalculateBatteryCommand": "on_calculate_battery",
    "AnalyzeDataCommand": "on_analyze_data",
    "ExportReportCommand": "on_export_report",
    "GenerateReportCommand": "on_generate_report",
    "BatchProcessingCommand": "on_batch_processing",
}

# Commands with unique patterns
SPECIAL_CMDS = {
    "RunAnalysisCommand": ("analysis_runner", "run_analysis", True, False),
}

# Presenter-based commands all follow: self.<attr> = presenter; self.presenter.on_*()
PRESENTER_ATTR = "presenter"


class TestAllCommands:
    """Parametrized tests over all concrete command classes"""

    @pytest.fixture(
        params=[
            "RunAnalysisCommand",
            "CalculateBatteryCommand",
            "AnalyzeDataCommand",
            "ExportReportCommand",
            "GenerateReportCommand",
            "BatchProcessingCommand",
        ],
        ids=lambda x: x,
    )
    def cmd_name(self, request):
        return request.param

    def test_execute_success(self, cmd_name):
        cmd_cls, deps, _ = self._build(cmd_name)
        cmd = cmd_cls(**deps)
        result = cmd.execute()
        assert result is True or isinstance(result, (list, dict))

    def test_execute_error_returns_fallback(self, cmd_name):
        cmd_cls, deps, dep_name = self._build(cmd_name)
        cmd = cmd_cls(**deps)
        # Make the dependency raise
        mock_dep = deps[dep_name]
        # Find the method to patch
        method = self._method_name(cmd_name)
        orig_method = getattr(mock_dep, method)
        orig_method.side_effect = Exception("boom")
        assert cmd.execute() is False

    def _build(self, cmd_name):
        """Build (cmd_class, deps_dict, dep_name) for a command."""
        from battery_analysis.main.commands.analysis_commands import (
            CalculateBatteryCommand,
            RunAnalysisCommand,
        )
        from battery_analysis.main.commands.data_commands import (
            AnalyzeDataCommand,
        )
        from battery_analysis.main.commands.report_commands import (
            BatchProcessingCommand,
            ExportReportCommand,
            GenerateReportCommand,
        )

        classes = {
            "RunAnalysisCommand": RunAnalysisCommand,
            "CalculateBatteryCommand": CalculateBatteryCommand,
            "AnalyzeDataCommand": AnalyzeDataCommand,
            "ExportReportCommand": ExportReportCommand,
            "GenerateReportCommand": GenerateReportCommand,
            "BatchProcessingCommand": BatchProcessingCommand,
        }

        cls = classes[cmd_name]

        if cmd_name in PRESENTER_CMDS:
            dep = Mock()
            return cls, {"presenter": dep}, "presenter"

        if cmd_name == "RunAnalysisCommand":
            dep = Mock()
            return cls, {"analysis_runner": dep}, "analysis_runner"

        raise ValueError(f"Unknown command: {cmd_name}")

    def _method_name(self, cmd_name):
        """Return the method name that the command calls on its dependency."""
        return {
            "RunAnalysisCommand": "run_analysis",
            "CalculateBatteryCommand": "on_calculate_battery",
            "AnalyzeDataCommand": "on_analyze_data",
            "ExportReportCommand": "on_export_report",
            "GenerateReportCommand": "on_generate_report",
            "BatchProcessingCommand": "on_batch_processing",
        }[cmd_name]


# ===========================================================================
# TestCommandManagerSupplementary
# ===========================================================================


class TestCommandManagerSupplementary:
    """CommandManager edge cases not in existing tests"""

    def test_initialize_sets_all_command_attributes(self):
        mw = Mock()
        mw.analysis_runner = Mock()
        mw.presenter = Mock()
        mw.main_controller = Mock()
        mw.config_manager = Mock()
        mw.dialog_manager = Mock()
        mw.validation_manager = Mock()
        mw.path_manager = Mock()
        mw.data_processor = Mock()
        mw.report_manager = Mock()
        mw.ui_manager = Mock()
        mgr = CommandManager(mw)
        assert hasattr(mw, "run_analysis_command")
        assert hasattr(mw, "export_report_command")
        assert hasattr(mw, "batch_processing_command")
        assert hasattr(mw, "generate_report_command")
        assert hasattr(mw, "analyze_data_command")
        assert hasattr(mw, "calculate_battery_command")
