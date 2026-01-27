import pytest
from unittest.mock import Mock, patch
from battery_analysis.main.ui_components.menu_manager import MenuManager


class TestMenuManager:
    def setup_method(self):
        self.manager = MenuManager()

    def test_create_menus(self):
        main_window = Mock()
        result = self.manager.create_menus(main_window)
        assert result is not None

    def test_add_menu_item(self):
        menu_name = "File"
        item_name = "Open"
        callback = Mock()
        result = self.manager.add_menu_item(menu_name, item_name, callback)
        assert result is True

    def test_remove_menu_item(self):
        menu_name = "File"
        item_name = "Open"
        result = self.manager.remove_menu_item(menu_name, item_name)
        assert result is True