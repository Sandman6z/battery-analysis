"""
主窗口补充测试——覆盖现有 test_main_window.py 未覆盖的方法

测试策略：
- 避免实例化 Main()（PyQt6 窗口在测试环境容易 hang）
- 使用 MagicMock(spec=...) + 手动注入 manager mock
- 直接对目标方法进行单元测试
"""

from unittest.mock import MagicMock, Mock, patch

import pytest


@pytest.fixture
def mw():
    """创建一个 Mock 主窗口实例，注入需要的 manager mock"""
    mw = MagicMock()
    mw._services = {}
    mw._controllers = {}
    mw._lazy_init_done = False
    mw._service_container = Mock()
    mw._service_container.get.return_value = None
    mw.version = "1.0"

    for mgr in [
        "ui_manager",
        "config_manager",
        "version_manager",
        "report_manager",
        "menu_manager",
        "table_manager",
        "validation_manager",
        "data_processor",
        "theme_manager",
        "help_manager",
        "temperature_handler",
        "environment_manager",
        "visualization_manager",
        "dialog_manager",
        "path_manager",
        "test_profile_manager",
        "signal_connector",
    ]:
        setattr(mw, mgr, Mock())
    return mw


# Alias for readability
@pytest.fixture
def main_window(mw):
    return mw


class TestComponentAccess:
    """_get_component / _get_service / _get_controller 测试"""

    def test_get_component_returns_cached_service(self, main_window):
        main_window._service_container.get.return_value = "service_instance"
        from battery_analysis.main.main_window import Main

        result = Main._get_component(main_window, "config", "service")
        assert result == "service_instance"
        main_window._service_container.get.assert_called_once_with("config")

    def test_get_component_caches_result(self, main_window):
        main_window._service_container.get.return_value = "svc"
        from battery_analysis.main.main_window import Main

        r1 = Main._get_component(main_window, "config", "service")
        r2 = Main._get_component(main_window, "config", "service")
        assert r1 == r2
        main_window._service_container.get.assert_called_once()

    def test_get_component_returns_none_on_type_error(self, main_window):
        main_window._service_container.get.side_effect = TypeError("bad type")
        from battery_analysis.main.main_window import Main

        result = Main._get_component(main_window, "missing", "service")
        assert result is None

    def test_get_component_returns_none_on_value_error(self, main_window):
        main_window._service_container.get.side_effect = ValueError("bad value")
        from battery_analysis.main.main_window import Main

        result = Main._get_component(main_window, "bad", "service")
        assert result is None

    def test_get_component_returns_none_on_import_error(self, main_window):
        main_window._service_container.get.side_effect = ImportError("no module")
        from battery_analysis.main.main_window import Main

        result = Main._get_component(main_window, "missing", "service")
        assert result is None

    def test_get_component_returns_none_on_generic_exception(self, main_window):
        main_window._service_container.get.side_effect = RuntimeError("unexpected")
        from battery_analysis.main.main_window import Main

        result = Main._get_component(main_window, "broken", "service")
        assert result is None

    def test_get_service_uses_service_type(self, main_window):
        # Bind the real _get_component so _get_service delegates correctly
        from battery_analysis.main.main_window import Main

        bound = Main._get_component.__get__(main_window, Main)
        main_window._get_component = bound
        main_window._service_container.get.return_value = "svc"
        result = Main._get_service(main_window, "config")
        assert result == "svc"
        main_window._service_container.get.assert_called_once_with("config")

    def test_get_controller_uses_controller_type(self, main_window):
        from battery_analysis.main.main_window import Main

        bound = Main._get_component.__get__(main_window, Main)
        main_window._get_component = bound
        main_window._service_container.get.return_value = "ctrl"
        result = Main._get_controller(main_window, "main_controller")
        assert result == "ctrl"
        main_window._service_container.get.assert_called_once_with("main_controller")


class TestLazyInit:
    """_lazy_init 测试"""

    def test_runs_only_once(self, main_window):
        from battery_analysis.main.main_window import Main

        Main._lazy_init(main_window)
        assert main_window._lazy_init_done is True
        main_window.ui_manager.setup_accessibility.assert_called_once()
        main_window.ui_manager.setup_tooltips.assert_called_once()

    def test_skips_if_already_done(self, main_window):
        main_window._lazy_init_done = True
        from battery_analysis.main.main_window import Main

        Main._lazy_init(main_window)
        main_window.ui_manager.setup_accessibility.assert_not_called()

    def test_handles_missing_ui_manager(self, main_window):
        main_window._lazy_init_done = False
        del main_window.ui_manager
        from battery_analysis.main.main_window import Main

        Main._lazy_init(main_window)  # should not raise
        assert main_window._lazy_init_done is True

    def test_handles_exception_gracefully(self, main_window):
        main_window.ui_manager.setup_accessibility.side_effect = Exception("boom")
        from battery_analysis.main.main_window import Main

        Main._lazy_init(main_window)  # should not raise
        assert main_window._lazy_init_done is True


class TestClipboardOperations:
    """剪贴板操作测试"""

    @pytest.fixture
    def mw(self, main_window):
        from battery_analysis.main.main_window import Main

        return main_window, Main

    def test_copy_on_line_edit(self, mw):
        import PyQt6.QtWidgets as QW

        mw_obj, cls = mw
        le = MagicMock(spec=QW.QLineEdit)
        mw_obj.focusWidget = Mock(return_value=le)
        cls.copy_selected_text(mw_obj)
        le.copy.assert_called_once()

    def test_copy_on_text_edit(self, mw):
        import PyQt6.QtWidgets as QW

        mw_obj, cls = mw
        te = MagicMock(spec=QW.QTextEdit)
        mw_obj.focusWidget = Mock(return_value=te)
        cls.copy_selected_text(mw_obj)
        te.copy.assert_called_once()

    def test_copy_ignores_non_text_widget(self, mw):
        mw_obj, cls = mw
        btn = MagicMock()  # no copy method
        mw_obj.focusWidget = Mock(return_value=btn)
        cls.copy_selected_text(mw_obj)  # should not raise

    def test_paste_on_line_edit(self, mw):
        import PyQt6.QtWidgets as QW

        mw_obj, cls = mw
        le = MagicMock(spec=QW.QLineEdit)
        mw_obj.focusWidget = Mock(return_value=le)
        cls.paste_text(mw_obj)
        le.paste.assert_called_once()

    def test_cut_on_line_edit(self, mw):
        import PyQt6.QtWidgets as QW

        mw_obj, cls = mw
        le = MagicMock(spec=QW.QLineEdit)
        mw_obj.focusWidget = Mock(return_value=le)
        cls.cut_selected_text(mw_obj)
        le.cut.assert_called_once()


class TestReportDelegation:
    """报告管理器委托测试"""

    def test_open_report(self, main_window):
        from battery_analysis.main.main_window import Main

        dialog = Mock()
        Main._open_report(main_window, dialog)
        main_window.report_manager.open_report.assert_called_once_with(dialog)

    def test_open_report_path(self, main_window):
        from battery_analysis.main.main_window import Main

        dialog = Mock()
        Main._open_report_path(main_window, dialog)
        main_window.report_manager.open_report_path.assert_called_once_with(dialog)

    def test_show_analysis_complete(self, main_window):
        from battery_analysis.main.main_window import Main

        Main._show_analysis_complete_dialog(main_window)
        main_window.report_manager.show_analysis_complete_dialog.assert_called_once()


class TestSimpleDelegations:
    """简单委托方法测试（各 manager 的单方法委托）"""

    def test_get_config(self, main_window):
        from battery_analysis.main.main_window import Main

        main_window.config_manager.get_config.return_value = ["a", "b"]
        result = Main.get_config(main_window, "battery.types")
        assert result == ["a", "b"]
        main_window.config_manager.get_config.assert_called_once_with("battery.types")

    def test_init_window(self, main_window):
        from battery_analysis.main.main_window import Main

        Main.init_window(main_window)
        main_window.ui_manager.init_window.assert_called_once()

    def test_init_widgetcolor(self, main_window):
        from battery_analysis.main.main_window import Main

        Main.init_widgetcolor(main_window)
        main_window.ui_manager.init_widgetcolor.assert_called_once()

    def test_set_table(self, main_window):
        from battery_analysis.main.main_window import Main

        Main.set_table(main_window)
        main_window.table_manager.set_table.assert_called_once()

    def test_save_table(self, main_window):
        from battery_analysis.main.main_window import Main

        Main.save_table(main_window)
        main_window.table_manager.save_table.assert_called_once()

    def test_toggle_statusbar(self, main_window):
        from battery_analysis.main.main_window import Main

        Main.toggle_statusbar(main_window)
        main_window.menu_manager.toggle_statusbar.assert_called_once()

    def test_initialize_environment_info(self, main_window):
        from battery_analysis.main.main_window import Main

        Main._initialize_environment_info(main_window)
        main_window.environment_manager.initialize_environment_info.assert_called_once()

    def test_ensure_env_info_keys(self, main_window):
        from battery_analysis.main.main_window import Main

        Main._ensure_env_info_keys(main_window)
        main_window.environment_manager.ensure_env_info_keys.assert_called_once()

    def test_show_visualizer_error(self, main_window):
        from battery_analysis.main.main_window import Main

        Main.show_visualizer_error(main_window, "err")
        main_window.visualization_manager.show_visualizer_error.assert_called_once_with("err")

    def test_validate_required_fields(self, main_window):
        from battery_analysis.main.main_window import Main

        Main.validate_required_fields(main_window)
        main_window.validation_manager.validate_required_fields.assert_called_once()


class TestLanguageMethods:
    """语言切换相关方法测试"""

    def test_update_ui_texts(self, main_window):
        from battery_analysis.main.main_window import Main

        with patch("battery_analysis.i18n.language_manager._") as mock_t:
            mock_t.side_effect = lambda x, y=None: y if y else x
            Main._update_ui_texts(main_window)
            # Should have accessed progress dialog title
            assert main_window.signal_connector.progress_dialog.setWindowTitle.called

    def test_on_language_changed(self, main_window):
        from battery_analysis.main.main_window import Main

        main_window.version = "1.0"
        # Patch at instance level since MagicMock auto-creates these attrs
        main_window._update_ui_texts = Mock()
        main_window._update_statusbar_messages = Mock()
        main_window._refresh_dialogs = Mock()
        Main._on_language_changed(main_window, "zh_CN")
        main_window._update_ui_texts.assert_called_once_with()
        main_window._update_statusbar_messages.assert_called_once_with()
        main_window._refresh_dialogs.assert_called_once_with()


class TestRefreshUi:
    """refresh_ui 测试"""

    def test_updates_status_bar(self, main_window):
        from battery_analysis.main.main_window import Main

        main_window.statusBar_BatteryAnalysis = Mock()
        main_window.comboBox_Specification_Type = Mock()
        main_window.comboBox_Specification_Type.currentText = Mock(return_value="")
        Main.refresh_ui(main_window)
        main_window.statusBar_BatteryAnalysis.showMessage.assert_called_once()

    def test_preserves_combo_selection(self, main_window):
        from battery_analysis.main.main_window import Main

        main_window.statusBar_BatteryAnalysis = Mock()
        main_window.comboBox_Specification_Type = Mock()
        main_window.comboBox_Specification_Type.currentText.return_value = "LCO"
        main_window.comboBox_Specification_Type.findText.return_value = 1
        Main.refresh_ui(main_window)
        main_window.comboBox_Specification_Type.setCurrentIndex.assert_called_once_with(1)

    def test_handles_missing_combo(self, main_window):
        from battery_analysis.main.main_window import Main

        main_window.statusBar_BatteryAnalysis = Mock()
        Main.refresh_ui(main_window)  # no comboBox_Specification_Type attr
        main_window.statusBar_BatteryAnalysis.showMessage.assert_called_once()
