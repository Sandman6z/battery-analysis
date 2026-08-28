from unittest.mock import Mock

from battery_analysis.main.ui_components.menu_manager import MenuManager


class TestMenuManager:
    def setup_method(self):
        mock_main = Mock()
        mock_main.menuBar = Mock(return_value=Mock())
        mock_font = Mock()
        mock_font.pointSize.return_value = 9
        mock_main.font.return_value = mock_font
        self.manager = MenuManager(mock_main)

    def test_setup_menu_shortcuts(self):
        self.manager.setup_menu_shortcuts()

    def test_connect_menu_actions(self):
        self.manager.connect_menu_actions()

    def test_update_menu_texts(self):
        self.manager.update_menu_texts()

    def test_update_statusbar_messages(self):
        self.manager.update_statusbar_messages()

    def test_toggle_toolbar_safe(self):
        self.manager.toggle_toolbar_safe()

    def test_toggle_statusbar_safe(self):
        self.manager.toggle_statusbar_safe()

    def test_zoom_in(self):
        self.manager.zoom_in()

    def test_zoom_out(self):
        self.manager.zoom_out()

    def test_reset_zoom(self):
        self.manager.reset_zoom()
