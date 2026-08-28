from battery_analysis.main.services.config_service import ConfigService


class TestConfigService:
    def setup_method(self):
        self.service = ConfigService()

    def test_initialization(self):
        assert self.service is not None

    def test_get_config_value_default(self):
        result = self.service.get_config_value("nonexistent.key", "default_val")
        assert result == "default_val"

    def test_get_config_sections(self):
        result = self.service.get_config_sections()
        assert isinstance(result, list)
