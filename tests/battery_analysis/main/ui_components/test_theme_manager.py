import pytest
from unittest.mock import Mock, patch
from battery_analysis.main.ui_components.theme_manager import ThemeManager


class TestThemeManager:
    def setup_method(self):
        self.manager = ThemeManager(Mock())
        # 模拟 QApplication.instance() 返回一个 Mock
        self._patcher = patch('battery_analysis.main.ui_components.theme_manager.QW.QApplication.instance',
                              return_value=Mock())
        self._patcher.start()

    def teardown_method(self):
        self._patcher.stop()

    def test_set_theme(self):
        self.manager.set_theme("System Default")

    def test_toggle_statusbar(self):
        self.manager.toggle_statusbar()

    def test_initialize_theme_actions(self):
        self.manager._initialize_theme_actions()
