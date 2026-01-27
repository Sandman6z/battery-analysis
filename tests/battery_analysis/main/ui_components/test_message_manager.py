import pytest
from unittest.mock import Mock, patch
from battery_analysis.main.ui_components.message_manager import MessageManager


class TestMessageManager:
    def setup_method(self):
        self.manager = MessageManager()

    def test_show_message(self):
        message = "Test message"
        message_type = "info"
        result = self.manager.show_message(message, message_type)
        assert result is True

    def test_show_error(self):
        error_message = "Test error"
        result = self.manager.show_error(error_message)
        assert result is True

    def test_show_success(self):
        success_message = "Test success"
        result = self.manager.show_success(success_message)
        assert result is True