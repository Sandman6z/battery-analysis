import pytest
from unittest.mock import Mock, patch
from battery_analysis.utils.config_manager import ConfigManager


class TestConfigManager:
    def setup_method(self):
        self.manager = ConfigManager()

    def test_load_config(self):
        result = self.manager.load_config()
        assert isinstance(result, dict)

    def test_save_config(self):
        config_data = {"settings": {}}
        result = self.manager.save_config(config_data)
        assert result is True

    def test_get_config_value(self):
        key = "test_key"
        default = "default"
        result = self.manager.get_config_value(key, default)
        assert isinstance(result, str)