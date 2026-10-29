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

    def test_analyze_menu_runs_real_analysis(self):
        self.manager.connect_menu_actions()
        mw = self.manager.main_window
        mw.actionAnalyze_Data.triggered.connect.assert_called_once_with(
            mw.run_analysis_command.execute
        )
        mw.actionBatch_Processing.triggered.connect.assert_not_called()

    def test_visible_menus_exclude_unimplemented_actions(self):
        from PyQt6.QtWidgets import QApplication, QMainWindow

        from battery_analysis.main.ui_builder import UIBuilder

        app = QApplication.instance() or QApplication([])
        window = QMainWindow()
        builder = UIBuilder(window)
        builder.create_actions()
        builder.create_menus()
        visible = {
            action.objectName()
            for menu in window.menuBar().actions()
            for action in menu.menu().actions()
            if not action.isSeparator()
        }
        assert "actionAnalyze_Data" in visible
        assert "actionConfiguration" in visible
        assert "actionNdaxConverter" in visible
        assert not visible.intersection({
            "actionNew", "actionOpen", "actionSave", "actionSave_As",
            "actionUndo", "actionRedo", "actionExport_Report",
            "actionCalculate_Battery", "actionGenerate_Report", "actionBatch_Processing",
        })
        window.close()

    def test_update_statusbar_messages(self):
        self.manager.update_statusbar_messages()

    def test_toggle_statusbar_safe(self):
        self.manager.toggle_statusbar_safe()

    def test_zoom_in(self):
        self.manager.zoom_in()

    def test_zoom_out(self):
        self.manager.zoom_out()

    def test_reset_zoom(self):
        self.manager.reset_zoom()
