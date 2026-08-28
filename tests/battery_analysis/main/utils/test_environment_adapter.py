from unittest.mock import Mock

from battery_analysis.main.utils.environment_adapter import EnvironmentAdapter


class TestEnvironmentAdapter:
    def setup_method(self):
        mock_main = Mock()
        mock_main._get_service = Mock(return_value=Mock())
        mock_main.env_info = {"environment_type": None, "gui_available": True}
        self.adapter = EnvironmentAdapter(mock_main)

    def test_initialize_environment_detector(self):
        result = self.adapter.initialize_environment_detector()
        assert result is not None

    def test_handle_environment_adaptation(self):
        self.adapter.handle_environment_adaptation()

    def test_adapt_for_ide_environment(self):
        self.adapter.adapt_for_ide_environment()

    def test_adapt_for_container_environment(self):
        self.adapter.adapt_for_container_environment()

    def test_adapt_for_production_environment(self):
        self.adapter.adapt_for_production_environment()

    def test_handle_gui_unavailable(self):
        self.adapter.handle_gui_unavailable()
