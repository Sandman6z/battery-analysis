from unittest.mock import Mock, patch
from battery_analysis.main.ui_components.config_manager import ConfigManager


class TestConfigManager:
    def setup_method(self):
        mock_main_window = Mock()
        self.manager = ConfigManager(mock_main_window)

    def test_get_config(self):
        result = self.manager.get_config("test_key")
        assert isinstance(result, list)

    def test_has_config(self):
        result = self.manager.has_config()
        assert isinstance(result, bool)

    def test_reload_config(self):
        self.manager.reload_config()

    def test_save_user_settings(self):
        self.manager.save_user_settings()

    def test_get_current_config_path(self):
        result = self.manager.get_current_config_path()
        assert result is None or isinstance(result, str)
