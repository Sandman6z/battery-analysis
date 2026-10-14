from unittest.mock import Mock, patch

from battery_analysis.main.ui_components.window_setup import WindowSetup


class TestWindowSetup:
    def setup_method(self):
        self.window_setup = WindowSetup(Mock())

    def test_init_window(self):
        with patch.object(self.window_setup, "_load_application_icon", return_value=Mock()):
            self.window_setup.init_window()

    def test_toggle_statusbar_safe(self):
        self.window_setup.toggle_statusbar_safe()
