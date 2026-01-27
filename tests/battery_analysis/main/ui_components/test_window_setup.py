import pytest
from unittest.mock import Mock, patch
from battery_analysis.main.ui_components.window_setup import WindowSetup


class TestWindowSetup:
    def setup_method(self):
        self.setup = WindowSetup()

    def test_setup_window(self):
        main_window = Mock()
        result = self.setup.setup_window(main_window)
        assert result is True

    def test_configure_layout(self):
        main_window = Mock()
        result = self.setup.configure_layout(main_window)
        assert result is True

    def test_setup_signals(self):
        main_window = Mock()
        result = self.setup.setup_signals(main_window)
        assert result is True