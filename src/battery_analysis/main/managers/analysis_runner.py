# -*- coding: utf-8 -*-
"""
分析运行管理器

负责处理电池分析的运行逻辑，包括：
- 输入验证
- 测试信息准备
- 控制器上下文更新
- 分析启动
"""

# 标准库导入
import logging
import os

# 第三方库导入
import PyQt6.QtWidgets as QW

# 本地应用/库导入
from battery_analysis.i18n.language_manager import _


class AnalysisRunner:
    """
    分析运行管理器
    负责处理电池分析的运行逻辑
    """
    
    def __init__(self, main_window):
        """
        初始化分析运行管理器
        
        Args:
            main_window: 主窗口实例
        """
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
    
    def run_analysis(self):
        """
        执行分析运行逻辑
        """
        # 保存表格数据
        self.main_window.save_table()
        self.main_window.init_widgetcolor()
        
        # 检查输入是否完整，包括reportedby
        if not self._check_inputs():
            return

        # 准备测试信息
        test_info = self._prepare_test_info()
        if not test_info:
            return

        # 更新控制器的上下文和测试信息
        self._update_controller_context(test_info)
    
    def _check_inputs(self):
        """
        检查输入是否完整
        
        Returns:
            bool: 输入是否完整
        """
        if not self.main_window.checkinput():
            # 检查失败，获取警告信息
            warning_info = []
            if not self.main_window.comboBox_ReportedBy.currentText():
                warning_info.append("Reported By")
            
            # 构建警告信息
            if warning_info:
                warning_str = "请完成以下必填项：" + ", ".join(warning_info)
                QW.QMessageBox.warning(self.main_window, "输入验证失败", warning_str)
            else:
                QW.QMessageBox.warning(self.main_window, "输入验证失败", "请检查所有必填项")
            
            self.main_window.pushButton_Run.setEnabled(True)
            return False
        
        # 简化验证，只验证必要的路径
        if not self.main_window.lineEdit_InputPath.text():
            QW.QMessageBox.critical(self.main_window, _("validation_failed", "输入验证失败"), _("input_path_empty", "输入数据路径不能为空"))
            self.main_window.pushButton_Run.setEnabled(True)
            return False

        if not self.main_window.lineEdit_OutputPath.text():
            QW.QMessageBox.critical(self.main_window, _("validation_failed", "输入验证失败"), _("output_path_empty", "输出路径不能为空"))
            self.main_window.pushButton_Run.setEnabled(True)
            return False

        # 检查冷冻温度是否设置为0，如果是则提示用户
        temperature_type = self.main_window.comboBox_Temperature.currentText()
        if temperature_type == "Freezer Temperature" and self.main_window.spinBox_Temperature.value() == 0:
            reply = QW.QMessageBox.question(
                self.main_window,
                "温度确认",
                "当前冷冻温度设置为0°C，是否继续运行？",
                QW.QMessageBox.StandardButton.Yes | QW.QMessageBox.StandardButton.No,
                QW.QMessageBox.StandardButton.No
            )
            if reply == QW.QMessageBox.StandardButton.No:
                self.main_window.pushButton_Run.setEnabled(True)
                return False
        
        return True
    
    def _prepare_test_info(self):
        """
        准备测试信息列表
        
        Returns:
            list: 测试信息列表
        """
        # 使用温度处理器构建温度值字符串
        temperature_value = self.main_window.temperature_handler.get_temperature_value()
        
        test_info = [
            self.main_window.comboBox_BatteryType.currentText(),
            self.main_window.comboBox_ConstructionMethod.currentText(),
            self.main_window.comboBox_Specification_Type.currentText(),
            self.main_window.comboBox_Specification_Method.currentText(),
            self.main_window.comboBox_Manufacturer.currentText(),
            self.main_window.lineEdit_BatchDateCode.text(),
            self.main_window.lineEdit_SamplesQty.text(),
            temperature_value,  # 使用构建的温度值
            self.main_window.lineEdit_DatasheetNominalCapacity.text(),
            self.main_window.lineEdit_CalculationNominalCapacity.text(),
            str(self.main_window.spinBox_AcceleratedAging.value()),
            self.main_window.comboBox_TesterLocation.currentText(),
            self.main_window.comboBox_TestedBy.currentText(),
            self.main_window.lineEdit_TestProfile.text(),
            self.main_window.listCurrentLevel,
            self.main_window.listVoltageLevel,
            self.main_window.lineEdit_Version.text(),
            self.main_window.lineEdit_RequiredUseableCapacity.text(),
            # 直接使用comboBox_ReportedBy的值，不再从表格获取
            self.main_window.comboBox_ReportedBy.currentText()
        ]
        
        return test_info
    
    def _update_controller_context(self, test_info):
        """
        更新控制器的上下文和测试信息
        
        Args:
            test_info: 测试信息列表
        """
        # 更新控制器的上下文和测试信息
        success = False
        main_controller = self.main_window._get_controller("main_controller")
        if main_controller:
            main_controller.set_project_context(
                project_path=self.main_window.path,
                input_path=self.main_window.lineEdit_InputPath.text(),
                output_path=self.main_window.lineEdit_OutputPath.text()
            )
            main_controller.set_test_info(test_info)

            # 更新配置
            self.main_window.update_config(test_info)
            self.main_window.sha256_checksum_run = self.main_window.sha256_checksum
            self.main_window.statusBar_BatteryAnalysis.showMessage("status:ok")

            # 启动分析
            success = main_controller.start_analysis()
        
        if not success:
            self.main_window.pushButton_Run.setEnabled(True)
            QW.QMessageBox.warning(self.main_window, _("start_failed", "启动失败"), _("cannot_start_analysis", "无法启动分析任务"))
