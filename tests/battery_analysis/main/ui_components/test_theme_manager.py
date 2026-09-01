from unittest.mock import Mock, patch

from battery_analysis.main.ui_components.theme_manager import ThemeManager


class TestThemeManager:
    def setup_method(self):
        self.manager = ThemeManager(Mock())
        # 模拟 QApplication.instance() 返回一个 Mock
        self._patcher = patch(
            "battery_analysis.ui.styles.style_manager.QApplication.instance",
            return_value=Mock(),
        )
        self._patcher.start()
        # 重置为 light 主题（避免前一个测试的状态泄漏）
        self.manager.set_theme("light")

    def teardown_method(self):
        self._patcher.stop()

    def test_set_theme_light(self):
        self.manager.set_theme("light")
        assert self.manager.get_current_theme() == "light"

    def test_set_theme_dark(self):
        self.manager.set_theme("dark")
        assert self.manager.get_current_theme() == "dark"

    def test_get_current_theme(self):
        assert self.manager.get_current_theme() == "light"

    def test_get_available_themes(self):
        themes = self.manager.get_available_themes()
        assert "light" in themes
        assert "dark" in themes

    def test_set_theme_does_not_process_events(self):
        """set_theme 不调用 processEvents（unpolish/polish 已触发重绘）"""
        with patch(
            "battery_analysis.ui.styles.style_manager.QApplication.processEvents"
        ) as mock_pe:
            self.manager.set_theme("light")
            mock_pe.assert_not_called()
