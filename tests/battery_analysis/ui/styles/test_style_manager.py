from unittest.mock import Mock, patch

import pytest

from battery_analysis.ui.styles.style_manager import (
    _LIGHT_TOKENS,
    _DARK_TOKENS,
    StyleManager,
    ThemeEngine,
    get_theme_engine,
)


class TestThemeEngine:
    """ThemeEngine 单元测试"""

    def setup_method(self):
        # 模拟 QApplication.instance()
        self._patcher = patch(
            "battery_analysis.ui.styles.style_manager.QApplication.instance",
            return_value=Mock(),
        )
        self._patcher.start()

    def teardown_method(self):
        self._patcher.stop()

    def test_light_tokens_defined(self):
        """_LIGHT_TOKENS 应包含所有必要令牌"""
        required_tokens = [
            "bg_primary", "bg_card", "bg_input", "text_primary", "text_secondary",
            "accent_green", "accent_blue", "accent_red", "border_default", "border_focus",
        ]
        for token in required_tokens:
            assert token in _LIGHT_TOKENS, f"Missing token: {token}"

    def test_dark_tokens_defined(self):
        """_DARK_TOKENS 应包含所有必要令牌"""
        required_tokens = [
            "bg_primary", "bg_card", "bg_input", "text_primary", "text_secondary",
            "accent_green", "accent_blue", "accent_red", "border_default", "border_focus",
        ]
        for token in required_tokens:
            assert token in _DARK_TOKENS, f"Missing token: {token}"

    def test_light_dark_tokens_same_keys(self):
        """_LIGHT_TOKENS 和 _DARK_TOKENS 应有相同的键"""
        assert set(_LIGHT_TOKENS.keys()) == set(_DARK_TOKENS.keys())

    def test_theme_engine_default_theme(self):
        """ThemeEngine 默认主题应为 light"""
        engine = ThemeEngine()
        assert engine.get_current_theme() == "light"

    def test_theme_engine_set_theme(self):
        """ThemeEngine 应能切换主题"""
        engine = ThemeEngine()
        engine.set_theme("dark")
        assert engine.get_current_theme() == "dark"
        engine.set_theme("light")
        assert engine.get_current_theme() == "light"

    def test_theme_engine_invalid_theme(self):
        """ThemeEngine 应回退到 light 主题"""
        engine = ThemeEngine()
        engine.set_theme("invalid_theme")
        assert engine.get_current_theme() == "light"

    def test_theme_engine_render(self):
        """ThemeEngine._render 应替换所有令牌"""
        engine = ThemeEngine()
        engine._qss_template = "QWidget { background-color: {bg_primary}; color: {text_primary}; }"
        result = engine._render()
        assert "{bg_primary}" not in result
        assert "{text_primary}" not in result
        assert _LIGHT_TOKENS["bg_primary"] in result
        assert _LIGHT_TOKENS["text_primary"] in result

    def test_theme_engine_available_themes(self):
        """get_available_themes 应返回 light 和 dark"""
        engine = ThemeEngine()
        themes = engine.get_available_themes()
        assert "light" in themes
        assert "dark" in themes


class TestStyleManager:
    def setup_method(self):
        self.manager = StyleManager()

    @pytest.mark.skip(reason="需要 Qt 运行环境")
    def test_load_style(self):
        style_name = "battery_analyzer"
        result = self.manager.load_style(style_name)
        assert isinstance(result, str)

    @pytest.mark.skip(reason="需要 Qt 运行环境")
    def test_apply_style(self):
        widget = Mock()
        style = "QWidget { background-color: white; }"
        result = self.manager.apply_style(widget, style)
        assert result is True

    @pytest.mark.skip(reason="需要 Qt 运行环境")
    def test_get_available_styles(self):
        result = self.manager.get_available_styles()
        assert isinstance(result, list)
