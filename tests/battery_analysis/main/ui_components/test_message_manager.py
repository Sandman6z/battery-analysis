from unittest.mock import Mock, patch
from battery_analysis.main.ui_components.message_manager import MessageManager


class TestMessageManager:
    def setup_method(self):
        self.manager = MessageManager(Mock())

    def test_show_message(self):
        with patch('battery_analysis.main.ui_components.message_manager.QW.QMessageBox'):
            self.manager.show_message("title", "message")

    def test_show_warning(self):
        with patch('battery_analysis.main.ui_components.message_manager.QW.QMessageBox'):
            self.manager.show_warning("title", "message")

    def test_show_error(self):
        with patch('battery_analysis.main.ui_components.message_manager.QW.QMessageBox'):
            self.manager.show_error("title", "message")
