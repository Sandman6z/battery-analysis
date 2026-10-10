"""主窗口动作与配置交互

从 main_window.py 拆出（大文件拆分重构）。"""

import PyQt6.QtCore as QC
import PyQt6.QtGui as QG
import PyQt6.QtWidgets as QW


class WindowActionsMixin:
    """信号连接、偏好应用、配置重载、剪贴板、配置对话框、主题与状态栏"""

    def connect_widget(self) -> None:
        self.logger.debug("connect_widget called")
        self.ui_manager.connect_widget()
        self.logger.debug("ui_manager.connect_widget completed")
        self.menu_manager.connect_menu_actions()
        self.logger.debug("menu_manager.connect_menu_actions completed")
        self.menu_manager.setup_menu_shortcuts()
        self.logger.debug("menu_manager.setup_menu_shortcuts completed")
        self.signal_connector.connect_controllers()
        self.logger.debug("signal_connector.connect_controllers completed")

    # ------------------------------
    # 用户交互方法
    # ------------------------------
    def on_preferences_applied(self) -> None:
        try:
            # 配置路径/重载统一经 ConfigService；仅需丢弃 config_utils 的路径缓存，
            # 让 ConfigService 重新解析（含 QSettings 里的自定义路径）
            from battery_analysis.utils.config_utils import clear_config_cache

            clear_config_cache()
            svc = self._get_service("config")
            if svc is not None:
                svc.reload_config()
            if hasattr(self, "config_manager"):
                self.config_manager.reload_config()
            if hasattr(self, "ui_manager"):
                self.ui_manager.init_combobox()

            # 应用主题设置
            settings = QC.QSettings()
            theme = settings.value("display/theme", "light")
            if theme == "system":
                # 跟随系统主题
                palette = QW.QApplication.palette()
                is_dark = palette.color(QG.QPalette.ColorRole.Window).lightness() < 128
                theme = "dark" if is_dark else "light"
            self.theme_manager.set_theme(theme)

            self.refresh_ui()
        except Exception as e:
            self.logger.error("Preferences apply post-processing failed: %s", e)

    def reload_configuration(self) -> None:
        try:
            from battery_analysis.utils.config_utils import clear_config_cache

            clear_config_cache()
            svc = self._get_service("config")
            if svc is not None:
                svc.reload_config()
            if hasattr(self, "config_manager"):
                self.config_manager.reload_config()
            if hasattr(self, "ui_manager"):
                self.ui_manager.init_combobox()
            self.refresh_ui()
        except Exception as e:
            self.logger.error("Failed to reload configuration: %s", e)
            if hasattr(self, "statusBar_BatteryAnalysis"):
                self.statusBar_BatteryAnalysis.showMessage(f"Configuration reload failed: {e!s}")

    def refresh_ui(self) -> None:
        try:
            if hasattr(self, "statusBar_BatteryAnalysis"):
                self.statusBar_BatteryAnalysis.showMessage("Configuration reloaded successfully")
            if hasattr(self, "comboBox_Specification_Type"):
                current_text = self.comboBox_Specification_Type.currentText()
                if current_text:
                    index = self.comboBox_Specification_Type.findText(current_text)
                    if index >= 0:
                        self.comboBox_Specification_Type.setCurrentIndex(index)
        except Exception as e:
            self.logger.error("Error refreshing UI: %s", e)

    def copy_selected_text(self) -> None:
        w = self.focusWidget()
        if isinstance(w, (QW.QLineEdit, QW.QTextEdit)):
            w.copy()

    def paste_text(self) -> None:
        w = self.focusWidget()
        if isinstance(w, (QW.QLineEdit, QW.QTextEdit)):
            w.paste()

    def cut_selected_text(self) -> None:
        w = self.focusWidget()
        if isinstance(w, (QW.QLineEdit, QW.QTextEdit)):
            w.cut()

    def show_config_dialog(self):
        self.logger.info("Attempting to open Configuration dialog")
        saved = {
            "BatteryType": self.comboBox_BatteryType.currentText(),
            "Manufacturer": self.comboBox_Manufacturer.currentText(),
            "TesterLocation": self.comboBox_TesterLocation.currentText(),
            "TestedBy": self.comboBox_TestedBy.currentText(),
            "ReportedBy": self.comboBox_ReportedBy.currentText(),
        }
        from battery_analysis.main.ui_components.config_dialog import ConfigDialog

        try:
            self.logger.info("Creating ConfigDialog instance")
            dialog = ConfigDialog(self)
            self.logger.info("ConfigDialog created successfully")
        except RuntimeError as e:
            self.logger.warning("Configuration service not ready: %s", e)
            QW.QMessageBox.warning(
                self,
                "Configuration",
                "Configuration service is not ready. Please restart the application.",
            )
            return
        except Exception as e:
            self.logger.exception("Failed to open configuration dialog")
            QW.QMessageBox.critical(
                self,
                "Error",
                f"Unexpected error opening configuration: {e}",
            )
            return

        if dialog.exec() == QW.QDialog.DialogCode.Accepted:
            self.statusBar_BatteryAnalysis.showMessage("Configuration saved")
            self.config_manager.reload_config()
            self.ui_manager.init_combobox()
            for name, text in saved.items():
                combo = getattr(self, f"comboBox_{name}")
                if text:
                    combo.setCurrentText(text)

    # ------------------------------
    # 报告相关方法
    # ------------------------------
    def set_theme(self, theme_name) -> None:
        self.theme_manager.set_theme(theme_name)

    def toggle_statusbar(self) -> None:
        self.menu_manager.toggle_statusbar()

    # ------------------------------
    # 验证相关方法
    # ------------------------------
    def check_batterytype(self) -> None:
        self.validation_manager.check_batterytype()

    def check_specification(self) -> None:
        self.validation_manager.check_specification()

    # ------------------------------
    # 表格相关方法
    # ------------------------------
    def set_table(self) -> None:
        self.table_manager.set_table()

    # ------------------------------
    # 温度相关方法
    # ------------------------------
    def on_temperature_type_changed(self, index):
        self.temperature_handler.on_temperature_type_changed()

    def checkinput(self) -> bool:
        return self.validation_manager.checkinput()
