"""只为真实分析命令及其初始化契约保留测试。"""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from battery_analysis.main.commands import Command, RunAnalysisCommand
from battery_analysis.main.managers.command_manager import CommandManager


class TestCommandBase:
    def test_cannot_instantiate(self):
        with pytest.raises(TypeError):
            Command()

    def test_subclass_must_implement_execute(self):
        with pytest.raises(TypeError):
            type("BadCmd", (Command,), {})()

    def test_concrete_subclass_is_valid(self):
        impl = type("GoodCmd", (Command,), {"execute": lambda self: True})()
        assert impl.execute() is True


class TestRunAnalysisCommand:
    def test_execute_success(self):
        runner = Mock()
        assert RunAnalysisCommand(runner).execute() is True
        runner.run_analysis.assert_called_once_with()

    def test_execute_error_returns_false(self):
        runner = Mock()
        runner.run_analysis.side_effect = RuntimeError("boom")
        assert RunAnalysisCommand(runner).execute() is False

    def test_manager_needs_no_presenter_and_creates_only_real_command(self):
        window = SimpleNamespace(analysis_runner=Mock())
        manager = CommandManager(window)
        assert manager.main_window is window
        assert set(vars(window)) == {"analysis_runner", "run_analysis_command"}
        assert window.run_analysis_command.execute() is True
        window.analysis_runner.run_analysis.assert_called_once_with()
