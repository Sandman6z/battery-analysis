import pytest
from unittest.mock import Mock, patch
from battery_analysis.main.ui_components.progress_dialog import ProgressDialog


class TestProgressDialog:
    def setup_method(self):
        self.dialog = ProgressDialog()

    def test_update_progress(self):
        progress = 50
        message = "Test progress"
        result = self.dialog.update_progress(progress, message)
        assert result is True

    def test_close_dialog(self):
        result = self.dialog.close_dialog()
        assert result is True

    def test_set_range(self):
        min_value = 0
        max_value = 100
        result = self.dialog.set_range(min_value, max_value)
        assert result is True