"""主窗口多语言文本刷新

从 main_window.py 拆出（大文件拆分重构）。"""

import logging

from battery_analysis.i18n import _


class WindowTextsMixin:
    """语言切换回调与 refresh_texts 文本刷新管线"""

    # ------------------------------
    # 语言相关方法
    # ------------------------------
    def _on_language_changed(self, language_code):
        self.setWindowTitle(f"Battery Analyzer v{self.version}")
        self.refresh_texts()
        self._update_statusbar_messages()
        self._refresh_dialogs()
        logging.info("Interface language switched to: %s", language_code)

    def refresh_texts(self):
        """刷新所有 UI 文本（语言切换时调用）"""
        # 窗口标题
        self.setWindowTitle(f"Battery Analyzer v{self.version}")

        # 右侧面板
        if hasattr(self, "label_Version"):
            self.label_Version.setText(_("Report Ver."))
        if hasattr(self, "label_ReportedBy"):
            self.label_ReportedBy.setText(_("Reported By"))
        if hasattr(self, "pushButton_Run"):
            self.pushButton_Run.setText(_("Run"))

        # 测试配置区
        if hasattr(self, "groupBox_TestConfig"):
            self.groupBox_TestConfig.setTitle(_("Test Config"))
        if hasattr(self, "label_TesterLocation"):
            self.label_TesterLocation.setText(_("Tester Location"))
        if hasattr(self, "label_TestedBy"):
            self.label_TestedBy.setText(_("Tested By"))
        if hasattr(self, "label_TestProfile"):
            self.label_TestProfile.setText(_("Test Profile"))
        if hasattr(self, "pushButton_TestProfile"):
            self.pushButton_TestProfile.setText(_("Open"))

        # 路径区
        if hasattr(self, "groupBox_Path"):
            self.groupBox_Path.setTitle(_("Path"))
        if hasattr(self, "label_InputPath"):
            self.label_InputPath.setText(_("Input Path "))
        if hasattr(self, "label_OutputPath"):
            self.label_OutputPath.setText(_("Output Path"))
        if hasattr(self, "pushButton_InputPath"):
            self.pushButton_InputPath.setText(_("Open"))
        if hasattr(self, "pushButton_OutputPath"):
            self.pushButton_OutputPath.setText(_("Open"))

        # 电池参数区
        if hasattr(self, "groupBox_BatteryConfig"):
            self.groupBox_BatteryConfig.setTitle(_("Battery Config"))
        if hasattr(self, "label_BatteryType"):
            self.label_BatteryType.setText(_("Battery Type"))
        if hasattr(self, "label_ConstructionMethod"):
            self.label_ConstructionMethod.setText(_("Construction Method"))
        if hasattr(self, "label_Specification"):
            self.label_Specification.setText(_("Specification"))
        if hasattr(self, "label_Manufacturer"):
            self.label_Manufacturer.setText(_("Manufacturer"))
        if hasattr(self, "label_BatchDateCode"):
            self.label_BatchDateCode.setText(_("Batch/Date Code"))
        if hasattr(self, "label_SamplesQty"):
            self.label_SamplesQty.setText(_("Samples Qty"))
        if hasattr(self, "label_TemperatureType"):
            self.label_TemperatureType.setText(_("Temp. Type"))
        if hasattr(self, "label_Temperature"):
            self.label_Temperature.setText(_("Temperature(℃)"))
        if hasattr(self, "label_AcceleratedAging"):
            self.label_AcceleratedAging.setText(_("Accelerated Aging(Years)"))
        if hasattr(self, "label_RequiredUseableCapacity"):
            self.label_RequiredUseableCapacity.setText(_("Required Useable Capacity(mAh)"))
        if hasattr(self, "label_CalculationNominalCapacity"):
            self.label_CalculationNominalCapacity.setText(_("Calculation Nominal Capacity(mAh)"))
        if hasattr(self, "label_DatasheetNominalCapacity"):
            self.label_DatasheetNominalCapacity.setText(_("Datasheet Nominal Capacity(mAh)"))

        # 设备信息区
        if hasattr(self, "groupBox_TestInformation"):
            self.groupBox_TestInformation.setTitle(_("Test Information"))

        # 菜单和工具栏
        if hasattr(self, "menu_manager"):
            self.menu_manager.update_statusbar_messages()

        # 进度对话框
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

    def _refresh_dialogs(self):
        """刷新所有打开的对话框"""
        # TODO: 实现对话框刷新逻辑，语言切换时应更新已打开对话框的文本
        # 当前为空实现，待首选项对话框等功能完成后补充
        pass
