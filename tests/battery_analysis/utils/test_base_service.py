import pytest
from unittest.mock import Mock, patch
from battery_analysis.utils.base_service import BaseService


class TestBaseService:
    def setup_method(self):
        self.service = BaseService()

    def test_init(self):
        assert hasattr(self.service, 'logger')

    def test_log_info(self):
        message = "Test info"
        result = self.service.log_info(message)
        assert result is None

    def test_log_error(self):
        message = "Test error"
        result = self.service.log_error(message)
        assert result is None