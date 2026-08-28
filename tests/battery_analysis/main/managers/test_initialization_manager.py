from unittest.mock import Mock

from battery_analysis.main.managers.initialization_manager import InitializationManager


class TestInitializationManager:
    def setup_method(self):
        self.main_window = Mock()
        self.manager = InitializationManager(self.main_window)

    def test_initialization(self):
        self.manager.initialize()

    def test_get_total_steps(self):
        result = self.manager.get_total_steps()
        assert isinstance(result, int)

    def test_get_executed_steps(self):
        result = self.manager.get_executed_steps()
        assert isinstance(result, dict)
