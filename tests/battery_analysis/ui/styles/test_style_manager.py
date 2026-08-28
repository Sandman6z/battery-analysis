from unittest.mock import Mock

import pytest

from battery_analysis.ui.styles.style_manager import StyleManager


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
