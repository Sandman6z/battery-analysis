import pytest
from unittest.mock import Mock, patch
from battery_analysis.main.ui_components.ui_manager import UIManager


class TestUIManager:
    def setup_method(self):
        self.manager = UIManager()

    def test_init_ui(self):
        main_window = Mock()
        result = self.manager.init_ui(main_window)
        assert result is True

    def test_update_ui(self):
        ui_elements = {"label": Mock()}
        data = {"label": "Test"}
        result = self.manager.update_ui(ui_elements, data)
        assert result is True

    def test_reset_ui(self):
        ui_elements = {"label": Mock()}
        result = self.manager.reset_ui(ui_elements)
        assert result is True