import pytest
from unittest.mock import Mock, patch
from battery_analysis.main.services.environment_service import EnvironmentService


class TestEnvironmentService:
    def setup_method(self):
        self.service = EnvironmentService()

    def test_get_environment_info(self):
        result = self.service.get_environment_info()
        assert isinstance(result, dict)

    def test_check_environment(self):
        result = self.service.check_environment()
        assert isinstance(result, dict)

    def test_get_system_resources(self):
        result = self.service.get_system_resources()
        assert isinstance(result, dict)