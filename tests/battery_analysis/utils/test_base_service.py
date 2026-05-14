import pytest
from unittest.mock import Mock, patch
from battery_analysis.utils.base_service import BaseService


class TestBaseService:
    def setup_method(self):
        self.service = BaseService()

    def test_init(self):
        assert hasattr(self.service, 'logger')

    def test_log_success(self):
        message = "Test info"
        # _log_success should not throw
        self.service._log_success(message)

    def test_handle_error(self):
        e = Exception("test error")
        message = "An error occurred"
        success, msg = self.service._handle_error(e, message)
        assert success is False
        assert "test error" in msg
        assert "An error occurred" in msg

    def test_safe_operation_success(self):
        result = self.service._safe_operation(lambda x: x + 1, 41)
        assert result == 42

    def test_safe_operation_failure(self):
        def failing():
            raise ValueError("boom")
        result = self.service._safe_operation(failing)
        assert result is None
