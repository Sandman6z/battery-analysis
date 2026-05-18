from unittest.mock import Mock, patch, MagicMock
from battery_analysis.main.ui_components.dialog_manager import DialogManager


class TestDialogManager:
    def setup_method(self):
        self.manager = DialogManager(Mock())

    def test_handle_exit_yes(self):
        with patch('battery_analysis.main.ui_components.dialog_manager.QW.QMessageBox.question',
                   return_value=Mock()):
            self.manager.handle_exit()

    def test_handle_about(self):
        with patch('battery_analysis.main.ui_components.dialog_manager.QW.QMessageBox.about'):
            self.manager.handle_about()

    def test_show_information_message(self):
        with patch('battery_analysis.main.ui_components.dialog_manager.QW.QMessageBox.information'):
            self.manager.show_information_message("title", "message")

    def test_show_critical_message(self):
        with patch('battery_analysis.main.ui_components.dialog_manager.QW.QMessageBox.critical'):
            self.manager.show_critical_message("title", "message")

    def test_show_warning_message(self):
        with patch('battery_analysis.main.ui_components.dialog_manager.QW.QMessageBox.warning'):
            self.manager.show_warning_message("title", "message")

    def test_show_question_message(self):
        with patch('battery_analysis.main.ui_components.dialog_manager.QW.QMessageBox.question',
                   return_value=Mock()):
            result = self.manager.show_question_message("title", "message")
            assert result is not None

    def test_show_preferences(self):
        with patch('battery_analysis.main.ui_components.dialog_manager.PreferencesDialog'), \
             patch('battery_analysis.main.ui_components.dialog_manager.ConfigPathProvider'):
            self.manager.show_preferences()
