from unittest.mock import Mock, patch

import pytest

from battery_analysis.main.ui_components.window_setup import WindowSetup


class TestWindowSetup:
    def setup_method(self):
        self.window_setup = WindowSetup(Mock())

    def test_init_window(self):
        with patch.object(self.window_setup, "_load_application_icon", return_value=Mock()):
            self.window_setup.init_window()

    def test_toggle_toolbar_safe(self):
        self.window_setup.toggle_toolbar_safe()

    def test_toggle_statusbar_safe(self):
        self.window_setup.toggle_statusbar_safe()

    @pytest.mark.skip(reason="需要 Qt 运行环境")
    def test_setup_menu_shortcuts(self):
        self.window_setup.setup_menu_shortcuts()
