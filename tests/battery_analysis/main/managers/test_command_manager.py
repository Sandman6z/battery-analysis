from unittest.mock import Mock
from battery_analysis.main.managers.command_manager import CommandManager


class TestCommandManager:
    def setup_method(self):
        main_window = Mock()
        main_window.analysis_runner = Mock()
        main_window.main_controller = Mock()
        main_window.config_manager = Mock()
        main_window.dialog_manager = Mock()
        main_window.validation_manager = Mock()
        main_window.path_manager = Mock()
        main_window.data_processor = Mock()
        main_window.report_manager = Mock()
        main_window.ui_manager = Mock()
        self.manager = CommandManager(main_window)

    def test_get_command_exists(self):
        cmd = self.manager.get_command("run_analysis")
        assert cmd is not None

    def test_get_command_nonexistent(self):
        cmd = self.manager.get_command("nonexistent")
        assert cmd is None

    def test_get_all_commands(self):
        cmds = self.manager.get_all_commands()
        assert isinstance(cmds, dict)
        assert len(cmds) > 0

    def test_execute_command_nonexistent(self):
        result = self.manager.execute_command("nonexistent")
        assert result is False