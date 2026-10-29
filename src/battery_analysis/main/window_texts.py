"""主窗口多语言文本刷新

从 main_window.py 拆出（大文件拆分重构）。"""

import logging

from battery_analysis.i18n import _

# 分组框标题：(属性名, 翻译键)
_GROUP_TITLE_TEXTS = [
    ("groupBox_TestConfig", "Test Config"),
    ("groupBox_Path", "Path"),
    ("groupBox_BatteryConfig", "Battery Config"),
    ("groupBox_TestInformation", "Test Information"),
]

# 普通文本控件：(属性名, 翻译键)，顺序不影响结果（每项独立赋值）
_WIDGET_TEXTS = [
    # 右侧面板
    ("label_Version", "Report Ver."),
    ("label_ReportedBy", "Reported By"),
    ("pushButton_Run", "Run"),
    # 测试配置区
    ("label_TesterLocation", "Tester Location"),
    ("label_TestedBy", "Tested By"),
    ("label_TestProfile", "Test Profile"),
    ("pushButton_TestProfile", "Open"),
    # 路径区
    ("label_InputPath", "Input Path "),  # 原文尾部带空格
    ("label_OutputPath", "Output Path"),
    ("pushButton_InputPath", "Open"),
    # 电池参数区
    ("label_BatteryType", "Battery Type"),
    ("label_ConstructionMethod", "Construction Method"),
    ("label_Specification", "Specification"),
    ("label_Manufacturer", "Manufacturer"),
    ("label_BatchDateCode", "Batch/Date Code"),
    ("label_SamplesQty", "Samples Qty"),
    ("label_TemperatureType", "Temp. Type"),
    ("label_Temperature", "Temperature(℃)"),
    ("label_AcceleratedAging", "Accelerated Aging(Years)"),
    ("label_RequiredUseableCapacity", "Required Useable Capacity(mAh)"),
    ("label_CalculationNominalCapacity", "Calculation Nominal Capacity(mAh)"),
    ("label_DatasheetNominalCapacity", "Datasheet Nominal Capacity(mAh)"),
]


class WindowTextsMixin:
    """语言切换回调与 refresh_texts 文本刷新管线"""

    # ------------------------------
    # 语言相关方法
    # ------------------------------
    def _on_language_changed(self, language_code):
        self.setWindowTitle(f"Battery Analyzer v{self.version}")
        self.refresh_texts()
        self._update_statusbar_messages()
        logging.info("Interface language switched to: %s", language_code)

    def refresh_texts(self):
        """刷新所有 UI 文本（语言切换时调用）"""
        # 窗口标题
        self.setWindowTitle(f"Battery Analyzer v{self.version}")

        # 分组框标题与控件文本（数据表驱动，缺失控件跳过）
        for attr, title in _GROUP_TITLE_TEXTS:
            if hasattr(self, attr):
                getattr(self, attr).setTitle(_(title))
        for attr, text in _WIDGET_TEXTS:
            if hasattr(self, attr):
                getattr(self, attr).setText(_(text))

        # 菜单和工具栏
        if hasattr(self, "menu_manager"):
            self.menu_manager.update_statusbar_messages()

        # 进度对话框（内联于本方法：测试夹具为 MagicMock，经 self 调子方法会落到自动生成的 Mock 上）
        if hasattr(self, "signal_connector") and self.signal_connector.progress_dialog:
            self.signal_connector.progress_dialog.setWindowTitle(_("Battery Analysis Progress"))
            self.signal_connector.progress_dialog.status_label.setText(
                _("Ready to start analysis...")
            )

    def _update_ui_texts(self):
        """兼容旧代码：调用 refresh_texts"""
        self.refresh_texts()

    def _update_statusbar_messages(self):
        self.menu_manager.update_statusbar_messages()
