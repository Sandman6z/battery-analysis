"""主窗口动作与配置交互

从 main_window.py 拆出（大文件拆分重构）。"""

import logging

import PyQt6.QtWidgets as QW

logger = logging.getLogger(__name__)

from battery_analysis.main.ui_components.config_dialog import ConfigDialog
from battery_analysis.main.window_state import MainWindowState
from battery_analysis.ui.styles.theme_settings import load_theme_preference
from battery_analysis.utils.config_utils import clear_config_cache


class WindowActionsMixin(MainWindowState):
    """信号连接、偏好应用、配置重载、剪贴板、配置对话框、主题与状态栏"""

    def connect_widget(self) -> None:
        logger.debug("connect_widget called")
        self.ui_manager.connect_widget()
        logger.debug("ui_manager.connect_widget completed")
        self.menu_manager.connect_menu_actions()
        logger.debug("menu_manager.connect_menu_actions completed")
        self.menu_manager.setup_menu_shortcuts()
        logger.debug("menu_manager.setup_menu_shortcuts completed")
        self.signal_connector.connect_controllers()
        logger.debug("signal_connector.connect_controllers completed")

    # ------------------------------
    # 用户交互方法
    # ------------------------------
    def show_ndax_converter(self) -> None:
        """Open or reactivate the independent NDAX export tool."""
        if self._ndax_converter_window is None:
            from battery_analysis.main.ndax_converter_window import NdaxConverterWindow

            self._ndax_converter_window = NdaxConverterWindow(self)
        self._ndax_converter_window.showNormal()
        self._ndax_converter_window.raise_()
        self._ndax_converter_window.activateWindow()

    def on_preferences_applied(self) -> None:
        try:
            # 配置路径/重载统一经 ConfigService；仅需丢弃 config_utils 的路径缓存，
            # 让 ConfigService 重新解析（含 QSettings 里的自定义路径）
            clear_config_cache()
            svc = self._get_service("config")
            if svc is not None:
                svc.reload_config()
            if hasattr(self, "config_manager"):
                self.config_manager.reload_config()
            else:
                logger.warning("config_manager missing, skip reload in preferences apply")
            if hasattr(self, "ui_manager"):
                self.ui_manager.init_combobox()
            else:
                logger.warning("ui_manager missing, skip combobox init in preferences apply")

            # 应用主题设置
            self.theme_manager.set_theme(load_theme_preference())

            self.refresh_ui()
        except Exception as e:
            logger.error("Preferences apply post-processing failed: %s", e)

    def reload_configuration(self) -> None:
        try:
            clear_config_cache()
            svc = self._get_service("config")
            if svc is not None:
                svc.reload_config()
            if hasattr(self, "config_manager"):
                self.config_manager.reload_config()
            else:
                logger.warning("config_manager missing, skip reload in reload_configuration")
            if hasattr(self, "ui_manager"):
                self.ui_manager.init_combobox()
            else:
                logger.warning("ui_manager missing, skip combobox init in reload_configuration")
            self.refresh_ui()
        except Exception as e:
            logger.error("Failed to reload configuration: %s", e)
            if hasattr(self, "statusBar_BatteryAnalysis"):
                self.statusBar_BatteryAnalysis.showMessage(f"Configuration reload failed: {e!s}")
            else:
                logger.warning(
                    "statusBar_BatteryAnalysis missing, cannot show reload failure message"
                )

    def refresh_ui(self) -> None:
        try:
            if hasattr(self, "statusBar_BatteryAnalysis"):
                self.statusBar_BatteryAnalysis.showMessage("Configuration reloaded successfully")
            else:
                logger.warning("statusBar_BatteryAnalysis missing, skip status message")
            if hasattr(self, "comboBox_Specification_Type"):
                current_text = self.comboBox_Specification_Type.currentText()
                if current_text:
                    index = self.comboBox_Specification_Type.findText(current_text)
                    if index >= 0:
                        self.comboBox_Specification_Type.setCurrentIndex(index)
            else:
                logger.warning("comboBox_Specification_Type missing, skip combobox refresh")
        except Exception as e:
            logger.error("Error refreshing UI: %s", e)

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
        logger.info("Attempting to open Configuration dialog")
        saved = {
            "BatteryType": self.comboBox_BatteryType.currentText(),
            "Manufacturer": self.comboBox_Manufacturer.currentText(),
            "TesterLocation": self.comboBox_TesterLocation.currentText(),
            "TestedBy": self.comboBox_TestedBy.currentText(),
            "ReportedBy": self.comboBox_ReportedBy.currentText(),
        }

        try:
            logger.info("Creating ConfigDialog instance")
            dialog = ConfigDialog(self)
            logger.info("ConfigDialog created successfully")
        except RuntimeError as e:
            logger.warning("Configuration service not ready: %s", e)
            QW.QMessageBox.warning(
                self,
                "Configuration",
                "Configuration service is not ready. Please restart the application.",
            )
            return
        except Exception as e:
            logger.exception("Failed to open configuration dialog")
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
                # 控件可能因配置变化被移除/重建；此时只记录，不中断后续恢复
                combo = getattr(self, f"comboBox_{name}", None)
                if combo is None:
                    logger.warning("Widget comboBox_%s not found, skipping restore", name)
                    continue
                if text:
                    combo.setCurrentText(text)

    # ------------------------------
    # 主题/状态栏开关
    # ------------------------------
    def set_theme(self, theme_name) -> None:
        self.theme_manager.set_theme(theme_name)

    def toggle_statusbar(self) -> None:
        self.menu_manager.toggle_statusbar_safe()

    # ------------------------------
    # 验证相关方法
    # ------------------------------
    def check_batterytype(self) -> None:
        self.validation_manager.check_batterytype()

    def check_specification(self) -> None:
        self.validation_manager.check_specification()

    def check_construction(self) -> None:
        """构造方法变化 → 重算「要求可用容量」（85%|75% 规则按构造取值）"""
        self.validation_manager.check_construction()

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
