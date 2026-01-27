import pytest
from unittest.mock import Mock, patch
from battery_analysis.main.services.config_service import ConfigService


class TestConfigService:
    def setup_method(self):
        self.service = ConfigService()

    def test_load_config(self):
        config_path = "config.json"
        with patch('battery_analysis.main.services.config_service.json') as mock_json:
            mock_json.load.return_value = {"settings": {}}
            with patch('builtins.open', new_callable=Mock):
                result = self.service.load_config(config_path)
                assert isinstance(result, dict)

    def test_save_config(self):
        config_data = {"settings": {}}
        config_path = "config.json"
        with patch('battery_analysis.main.services.config_service.json') as mock_json:
            mock_json.dump.return_value = None
            with patch('builtins.open', new_callable=Mock):
                result = self.service.save_config(config_data, config_path)
                assert result is True

    def test_get_config_value(self):
        config_data = {"settings": {"key": "value"}}
        result = self.service.get_config_value(config_data, "settings.key")
        assert result == "value"

    def test_set_config_value(self):
        config_data = {"settings": {}}
        result = self.service.set_config_value(config_data, "settings.key", "value")
        assert result is True
        assert config_data["settings"]["key"] == "value"