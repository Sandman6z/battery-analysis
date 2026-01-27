# -*- coding: utf-8 -*-
"""
report_generator测试
"""

import pytest
from unittest.mock import Mock, patch
from battery_analysis.main.business_logic.report_generator import ReportGenerator


class TestReportGenerator:
    """报告生成器测试类"""

    def setup_method(self):
        """设置测试环境"""
        # 创建模拟主窗口对象
        self.mock_main_window = Mock()
        self.mock_main_window.lineEdit_OutputPath.text.return_value = "output/path"
        self.mock_main_window.statusBar_BatteryAnalysis.showMessage = Mock()
        
        # 创建报告生成器实例
        self.report_generator = ReportGenerator(self.mock_main_window)

    def test_generate_report_with_output_path(self):
        """测试生成报告（设置了输出路径）"""
        # 模拟QW.QMessageBox.information
        with patch('battery_analysis.main.business_logic.report_generator.QW.QMessageBox.information') as mock_information:
            # 调用方法
            self.report_generator.generate_report()
            
            # 验证结果
            mock_information.assert_called_once()
            self.mock_main_window.statusBar_BatteryAnalysis.showMessage.assert_any_call("生成报告中...")
            self.mock_main_window.statusBar_BatteryAnalysis.showMessage.assert_any_call("状态:就绪")

    def test_generate_report_without_output_path(self):
        """测试生成报告（未设置输出路径）"""
        # 设置lineEdit_OutputPath返回空字符串
        self.mock_main_window.lineEdit_OutputPath.text.return_value = ""
        
        # 模拟QW.QMessageBox.warning
        with patch('battery_analysis.main.business_logic.report_generator.QW.QMessageBox.warning') as mock_warning:
            # 调用方法
            self.report_generator.generate_report()
            
            # 验证结果
            mock_warning.assert_called_once()

    def test_export_report_with_output_path(self):
        """测试导出报告（设置了输出路径）"""
        # 模拟QW.QMessageBox.information
        with patch('battery_analysis.main.business_logic.report_generator.QW.QMessageBox.information') as mock_information:
            # 调用方法
            self.report_generator.export_report()
            
            # 验证结果
            mock_information.assert_called_once()
            self.mock_main_window.statusBar_BatteryAnalysis.showMessage.assert_any_call("导出报告中...")
            self.mock_main_window.statusBar_BatteryAnalysis.showMessage.assert_any_call("状态:就绪")

    def test_export_report_without_output_path(self):
        """测试导出报告（未设置输出路径）"""
        # 设置lineEdit_OutputPath返回空字符串
        self.mock_main_window.lineEdit_OutputPath.text.return_value = ""
        
        # 模拟QW.QMessageBox.warning
        with patch('battery_analysis.main.business_logic.report_generator.QW.QMessageBox.warning') as mock_warning:
            # 调用方法
            self.report_generator.export_report()
            
            # 验证结果
            mock_warning.assert_called_once()

    def test_batch_processing(self):
        """测试批量处理"""
        # 模拟QW.QMessageBox.information
        with patch('battery_analysis.main.business_logic.report_generator.QW.QMessageBox.information') as mock_information:
            # 调用方法
            self.report_generator.batch_processing()
            
            # 验证结果
            mock_information.assert_called_once()
            self.mock_main_window.statusBar_BatteryAnalysis.showMessage.assert_any_call("准备批量处理...")
            self.mock_main_window.statusBar_BatteryAnalysis.showMessage.assert_any_call("状态:就绪")
