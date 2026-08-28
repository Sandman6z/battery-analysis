from battery_analysis.main.services.environment_service import EnvironmentService


class TestEnvironmentService:
    def setup_method(self):
        self.service = EnvironmentService()

    def test_get_environment_info(self):
        result = self.service.get_environment_info()
        assert isinstance(result, dict)

    def test_get_environment_type(self):
        # Should not raise
        self.service.get_environment_type()

    def test_get_platform_info(self):
        result = self.service.get_platform_info()
        assert isinstance(result, dict)
