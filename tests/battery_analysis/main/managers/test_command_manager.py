import pytest
from unittest.mock import Mock, patch
from battery_analysis.main.managers.command_manager import CommandManager


class TestCommandManager:
    def setup_method(self):
        self.manager = CommandManager()

    def test_register_command(self):
        command_name = "test_command"
        command = Mock()
        result = self.manager.register_command(command_name, command)
        assert result is True

    def test_execute_command(self):
        command_name = "test_command"
        command = Mock()
        command.execute.return_value = {"status": "success"}
        self.manager.register_command(command_name, command)
        result = self.manager.execute_command(command_name)
        assert result is not None

    def test_unregister_command(self):
        command_name = "test_command"
        command = Mock()
        self.manager.register_command(command_name, command)
        result = self.manager.unregister_command(command_name)
        assert result is True