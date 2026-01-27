import pytest
from unittest.mock import Mock, patch
from battery_analysis.ui.frameworks.pyqt6_ui_framework import PyQt6UIFramework


class TestPyQt6UIFramework:
    def setup_method(self):
        self.framework = PyQt6UIFramework()

    def test_create_application(self):
        result = self.framework.create_application()
        assert result is not None

    def test_create_main_window(self):
        result = self.framework.create_main_window()
        assert result is not None

    def test_show_window(self):
        window = Mock()
        result = self.framework.show_window(window)
        assert result is True

    def test_run_application(self):
        app = Mock()
        app.exec.return_value = 0
        result = self.framework.run_application(app)
        assert result == 0