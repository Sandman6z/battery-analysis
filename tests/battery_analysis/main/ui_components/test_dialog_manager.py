import pytest
from unittest.mock import Mock, patch
from battery_analysis.main.ui_components.dialog_manager import DialogManager


class TestDialogManager:
    def setup_method(self):
        self.manager = DialogManager()

    def test_show_info_dialog(self):
        message = "Test info"
        title = "Info"
        with patch('battery_analysis.main.ui_components.dialog_manager.QMessageBox') as mock_message_box:
            mock_instance = Mock()
            mock_message_box.return_value = mock_instance
            mock_instance.exec_.return_value = 1
            result = self.manager.show_info_dialog(message, title)
            assert result is not None

    def test_show_error_dialog(self):
        message = "Test error"
        title = "Error"
        with patch('battery_analysis.main.ui_components.dialog_manager.QMessageBox') as mock_message_box:
            mock_instance = Mock()
            mock_message_box.return_value = mock_instance
            mock_instance.exec_.return_value = 1
            result = self.manager.show_error_dialog(message, title)
            assert result is not None

    def test_show_confirmation_dialog(self):
        message = "Test confirmation"
        title = "Confirm"
        with patch('battery_analysis.main.ui_components.dialog_manager.QMessageBox') as mock_message_box:
            mock_instance = Mock()
            mock_message_box.return_value = mock_instance
            mock_instance.exec_.return_value = 1
            result = self.manager.show_confirmation_dialog(message, title)
            assert result is not None