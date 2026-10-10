"""配置管理对话框主类
提供左侧分类导航、右侧编辑器的 master-detail UI，用于管理应用的数据字典配置。
"""

import copy
import logging

from PyQt6 import QtWidgets as QW

from battery_analysis.i18n.language_manager import _
from battery_analysis.main.ui_components.config_dialog.battery_config_page import (
    _BatteryConfigPage,
)
from battery_analysis.main.ui_components.config_dialog.equipment_page import _EquipmentPage
from battery_analysis.main.ui_components.config_dialog.test_config_page import _TestConfigPage
from battery_analysis.utils.config_defaults import DEFAULT_CONFIG


class ConfigDialog(QW.QDialog):
    """配置管理主对话框（master-detail 布局）"""

    _CATEGORIES = ["Battery", "Test", "Equipment"]

    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
        self._config_service = main_window._get_service("config")
        if self._config_service is None:
            raise RuntimeError("ConfigService not available — cannot open Configuration dialog")

        # 从 ConfigService 加载当前数据（深拷贝，取消保存才写回）
        raw_data = self._config_service.get_config_value("")
        self._working_data = copy.deepcopy(raw_data) if isinstance(raw_data, dict) else {}

        self.setWindowTitle(_("Configuration"))
        self.setMinimumSize(760, 560)
        self._setup_ui()
        self._populate_data()

    def _setup_ui(self):
        layout = QW.QVBoxLayout(self)

        # 顶部选项卡（master-detail）
        self._tab_widget = QW.QTabWidget()
        self._page_battery = _BatteryConfigPage(self)
        self._page_test = _TestConfigPage(self)
        self._page_equipment = _EquipmentPage(self)
        self._tab_widget.addTab(self._page_battery, _("Battery"))
        self._tab_widget.addTab(self._page_test, _("Test"))
        self._tab_widget.addTab(self._page_equipment, _("Equipment"))
        # 缩短选项卡高度
        self._tab_widget.setStyleSheet("QTabWidget::pane { border: 1px solid #c0c0c0; } QTabBar::tab { padding: 4px 12px; min-height: 20px; }")
        layout.addWidget(self._tab_widget, 1)

        # 底部按钮栏
        btn_layout = QW.QHBoxLayout()
        btn_reset = QW.QPushButton(_("Reset Defaults"))
        btn_reset.clicked.connect(self._on_reset_defaults)
        btn_save = QW.QPushButton(_("Save"))
        btn_save.clicked.connect(self._on_save)
        btn_cancel = QW.QPushButton(_("Cancel"))
        btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(btn_reset)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

    def _on_reset_defaults(self):
        reply = QW.QMessageBox.question(
            self,
            _("Reset Defaults"),
            _("Reset all configuration to default values? This cannot be undone."),
            QW.QMessageBox.StandardButton.Yes | QW.QMessageBox.StandardButton.No,
        )
        if reply == QW.QMessageBox.StandardButton.Yes:
            self._working_data = copy.deepcopy(DEFAULT_CONFIG)
            self._populate_data()

    def _on_save(self):
        try:
            self._page_battery.collect_data()
            self._page_equipment.collect_data()
            self._page_test.collect_data()
            self._config_service.replace_all_config(self._working_data)
            self._config_service.save_config()
            self.accept()
        except Exception as e:
            self.logger.error("Failed to save configuration: %s", e)
            QW.QMessageBox.critical(self, _("Error"), f"{_('Failed to save configuration')}: {e}")

    def _populate_data(self):
        wd = self._working_data if isinstance(self._working_data, dict) else {}
        self._page_battery.load_data(wd.get("battery", {}))
        self._page_test.load_data(wd.get("test", {}))
        self._page_equipment.load_data(wd.get("test", {}).get("equipment", {}))
