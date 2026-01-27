import pytest
from unittest.mock import Mock, patch
from battery_analysis.main.managers.initialization_manager import InitializationManager


class TestInitializationManager:
    def setup_method(self):
        self.manager = InitializationManager()

    def test_initialize_application(self):
        with patch('battery_analysis.main.managers.initialization_manager.InitializationOrchestrator') as mock_orchestrator:
            mock_instance = Mock()
            mock_orchestrator.return_value = mock_instance
            mock_instance.initialize.return_value = True
            result = self.manager.initialize_application()
            assert result is True

    def test_get_initialization_status(self):
        result = self.manager.get_initialization_status()
        assert isinstance(result, dict)

    def test_cleanup(self):
        result = self.manager.cleanup()
        assert result is True