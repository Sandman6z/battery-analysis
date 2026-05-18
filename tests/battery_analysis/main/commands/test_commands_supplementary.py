"""
Command module supplementary tests — covers all 10 Command implementations,
the base Command ABC, and CommandManager edge cases not in existing tests.
"""

from unittest.mock import Mock, patch

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
    "SaveSettingsCommand": ("main_window", "save_settings", True, False),
    "ProcessExcelCommand": ("data_processor", "process_excel_with_pandas", {"result"}, {}),
    "ProcessAllExcelCommand": ("data_processor", "process_all_excel_files", ["result"], []),
    "GetXlsxInfoCommand": ("data_processor", "get_xlsxinfo", True, False),
    "SaveTableCommand": ("data_processor", "save_table", True, False),
    "UpdateConfigCommand": ("data_processor", "update_config", True, False),
    "CheckInputCommand": ("battery_calculator", "check_input", True, False),
    "HandleDataErrorCommand": ("data_processor", "handle_data_error_recovery", True, False),
}

# Presenter-based commands all follow: self.<attr> = presenter; self.presenter.on_*()
PRESENTER_ATTR = "presenter"


class TestAllCommands:
    """Parametrized tests over all concrete command classes"""

    @pytest.fixture(params=[
        "RunAnalysisCommand", "CalculateBatteryCommand", "AnalyzeDataCommand",
        "ProcessExcelCommand", "ProcessAllExcelCommand", "GetXlsxInfoCommand",
        "SaveTableCommand", "UpdateConfigCommand", "CheckInputCommand",
        "HandleDataErrorCommand", "ExportReportCommand", "GenerateReportCommand",
        "BatchProcessingCommand", "SaveSettingsCommand",
    ], ids=lambda x: x)
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
        if cmd_name in ("ProcessExcelCommand",):
            assert cmd.execute() == {}
        elif cmd_name in ("ProcessAllExcelCommand",):
            assert cmd.execute() == []
        else:
            assert cmd.execute() is False

    def _build(self, cmd_name):
        """Build (cmd_class, deps_dict, dep_name) for a command."""
        from battery_analysis.main.commands.analysis_commands import (
            RunAnalysisCommand, CalculateBatteryCommand,
        )
        from battery_analysis.main.commands.report_commands import (
            ExportReportCommand, GenerateReportCommand,
            BatchProcessingCommand, SaveSettingsCommand,
        )
        from battery_analysis.main.commands.data_commands import (
            AnalyzeDataCommand, ProcessExcelCommand, ProcessAllExcelCommand,
            GetXlsxInfoCommand, SaveTableCommand, UpdateConfigCommand,
            CheckInputCommand, HandleDataErrorCommand,
        )

        classes = {
            "RunAnalysisCommand": RunAnalysisCommand,
            "CalculateBatteryCommand": CalculateBatteryCommand,
            "AnalyzeDataCommand": AnalyzeDataCommand,
            "ProcessExcelCommand": ProcessExcelCommand,
            "ProcessAllExcelCommand": ProcessAllExcelCommand,
            "GetXlsxInfoCommand": GetXlsxInfoCommand,
            "SaveTableCommand": SaveTableCommand,
            "UpdateConfigCommand": UpdateConfigCommand,
            "CheckInputCommand": CheckInputCommand,
            "HandleDataErrorCommand": HandleDataErrorCommand,
            "ExportReportCommand": ExportReportCommand,
            "GenerateReportCommand": GenerateReportCommand,
            "BatchProcessingCommand": BatchProcessingCommand,
            "SaveSettingsCommand": SaveSettingsCommand,
        }

        cls = classes[cmd_name]

        if cmd_name in PRESENTER_CMDS:
            dep = Mock()
            return cls, {"presenter": dep}, "presenter"

        if cmd_name == "RunAnalysisCommand":
            dep = Mock()
            return cls, {"analysis_runner": dep}, "analysis_runner"

        if cmd_name == "SaveSettingsCommand":
            dep = Mock()
            return cls, {"main_window": dep}, "main_window"

        if cmd_name == "ProcessExcelCommand":
            dep = Mock()
            dep.process_excel_with_pandas.return_value = {"result": True}
            return cls, {"data_processor": dep, "file_path": "test.xlsx"}, "data_processor"

        if cmd_name == "ProcessAllExcelCommand":
            dep = Mock()
            dep.process_all_excel_files.return_value = ["result"]
            return cls, {"data_processor": dep, "directory": "/path"}, "data_processor"

        if cmd_name == "CheckInputCommand":
            dep = Mock()
            dep.check_input.return_value = True
            return cls, {"battery_calculator": dep}, "battery_calculator"

        if cmd_name in ("GetXlsxInfoCommand", "SaveTableCommand", "UpdateConfigCommand",
                        "HandleDataErrorCommand"):
            extra = {}
            if cmd_name == "UpdateConfigCommand":
                extra = {"test_info": {"key": "val"}}
            elif cmd_name == "HandleDataErrorCommand":
                extra = {"error_msg": "bad"}
            dep = Mock()
            return cls, {"data_processor": dep, **extra}, "data_processor"

        raise ValueError(f"Unknown command: {cmd_name}")

    def _method_name(self, cmd_name):
        """Return the method name that the command calls on its dependency."""
        return {
            "RunAnalysisCommand": "run_analysis",
            "CalculateBatteryCommand": "on_calculate_battery",
            "AnalyzeDataCommand": "on_analyze_data",
            "ProcessExcelCommand": "process_excel_with_pandas",
            "ProcessAllExcelCommand": "process_all_excel_files",
            "GetXlsxInfoCommand": "get_xlsxinfo",
            "SaveTableCommand": "save_table",
            "UpdateConfigCommand": "update_config",
            "CheckInputCommand": "check_input",
            "HandleDataErrorCommand": "handle_data_error_recovery",
            "ExportReportCommand": "on_export_report",
            "GenerateReportCommand": "on_generate_report",
            "BatchProcessingCommand": "on_batch_processing",
            "SaveSettingsCommand": "save_settings",
        }[cmd_name]


# ===========================================================================
# TestCommandManagerSupplementary
# ===========================================================================

class TestCommandManagerSupplementary:
    """CommandManager edge cases not in existing tests"""

    def test_execute_command_success(self):
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
        assert mgr.execute_command("run_analysis") is True

    def test_execute_command_catches_exception(self):
        mw = Mock()
        mw.analysis_runner = Mock()
        mw.analysis_runner.run_analysis.side_effect = RuntimeError("fail")
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
        assert mgr.execute_command("run_analysis") is False

    def test_get_all_commands_returns_copy(self):
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
        cmds = mgr.get_all_commands()
        orig_len = len(cmds)
        cmds["new"] = "test"
        assert len(mgr.get_all_commands()) == orig_len  # original unchanged

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
        assert hasattr(mw, "save_settings_command")
        assert hasattr(mw, "export_report_command")
        assert hasattr(mw, "batch_processing_command")
        assert hasattr(mw, "generate_report_command")
        assert hasattr(mw, "analyze_data_command")
        assert hasattr(mw, "calculate_battery_command")

    def test_all_commands_registered(self):
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
        cmds = mgr.get_all_commands()
        assert "run_analysis" in cmds
        assert "save_settings" in cmds
        assert "export_report" in cmds
        assert "batch_processing" in cmds
        assert "generate_report" in cmds
        assert "analyze_data" in cmds
        assert "calculate_battery" in cmds
