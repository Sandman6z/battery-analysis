"""
测试电池计算器模块的功能
"""
import pytest
from unittest.mock import Mock, patch
from battery_analysis.main.business_logic.battery_calculator import BatteryCalculator


class TestBatteryCalculator:
    """测试电池计算器类"""
    
    def setup_method(self):
        """设置测试环境"""
        # 创建模拟的主窗口对象
        self.mock_main_window = Mock()
        
        # 设置模拟的UI控件
        self.mock_main_window.comboBox_BatteryType = Mock()
        self.mock_main_window.comboBox_ConstructionMethod = Mock()
        self.mock_main_window.comboBox_Specification_Type = Mock()
        self.mock_main_window.comboBox_Specification_Method = Mock()
        self.mock_main_window.comboBox_Manufacturer = Mock()
        self.mock_main_window.comboBox_TesterLocation = Mock()
        self.mock_main_window.comboBox_TestedBy = Mock()
        self.mock_main_window.comboBox_ReportedBy = Mock()
        self.mock_main_window.comboBox_Temperature = Mock()
        self.mock_main_window.lineEdit_InputPath = Mock()
        self.mock_main_window.lineEdit_OutputPath = Mock()
        self.mock_main_window.lineEdit_Barcode = Mock()
        self.mock_main_window.statusBar_BatteryAnalysis = Mock()
        
        # 创建电池计算器实例
        self.calculator = BatteryCalculator(self.mock_main_window)
    
    @patch('battery_analysis.main.business_logic.battery_calculator.QW.QMessageBox')
    @patch('battery_analysis.main.business_logic.battery_calculator._')
    def test_calculate_battery(self, mock_gettext, mock_message_box):
        """测试电池计算功能"""
        # 设置国际化翻译模拟
        mock_gettext.side_effect = lambda x, y=None: y if y else x
        
        # 调用计算方法
        self.calculator.calculate_battery()
        
        # 验证状态栏更新被调用
        assert self.mock_main_window.statusBar_BatteryAnalysis.showMessage.called
        
        # 验证消息框调用
        mock_message_box.information.assert_called_once()
    
    def test_check_input_all_valid(self):
        """测试所有输入都有效的情况"""
        # 设置所有控件返回有效值
        self.mock_main_window.comboBox_BatteryType.currentText.return_value = "Li-ion"
        self.mock_main_window.comboBox_ConstructionMethod.currentText.return_value = "Coin Cell"
        self.mock_main_window.comboBox_Specification_Type.currentText.return_value = "Capacity"
        self.mock_main_window.comboBox_Specification_Method.currentText.return_value = "Constant Current"
        self.mock_main_window.comboBox_Manufacturer.currentText.return_value = "Samsung"
        self.mock_main_window.comboBox_TesterLocation.currentText.return_value = "Lab A"
        self.mock_main_window.comboBox_TestedBy.currentText.return_value = "Test Engineer"
        self.mock_main_window.comboBox_ReportedBy.currentText.return_value = "Report Engineer"
        self.mock_main_window.comboBox_Temperature.currentText.return_value = "25°C"
        self.mock_main_window.lineEdit_InputPath.text.return_value = "C:\\test\\data"
        self.mock_main_window.lineEdit_OutputPath.text.return_value = "C:\\test\\output"
        self.mock_main_window.lineEdit_Barcode.text.return_value = "BAT001"
        
        # 调用检查方法
        result = self.calculator.check_input()
        
        # 验证结果
        assert result is True
    
    @patch('battery_analysis.main.business_logic.battery_calculator.QW.QMessageBox')
    def test_check_input_missing_battery_type(self, mock_message_box):
        """测试缺少电池类型的情况"""
        # 设置电池类型为空
        self.mock_main_window.comboBox_BatteryType.currentText.return_value = ""
        
        # 设置其他控件返回有效值
        self.mock_main_window.comboBox_ConstructionMethod.currentText.return_value = "Coin Cell"
        self.mock_main_window.comboBox_Specification_Type.currentText.return_value = "Capacity"
        self.mock_main_window.comboBox_Specification_Method.currentText.return_value = "Constant Current"
        self.mock_main_window.comboBox_Manufacturer.currentText.return_value = "Samsung"
        self.mock_main_window.comboBox_TesterLocation.currentText.return_value = "Lab A"
        self.mock_main_window.comboBox_TestedBy.currentText.return_value = "Test Engineer"
        self.mock_main_window.comboBox_ReportedBy.currentText.return_value = "Report Engineer"
        self.mock_main_window.comboBox_Temperature.currentText.return_value = "25°C"
        self.mock_main_window.lineEdit_InputPath.text.return_value = "C:\\test\\data"
        self.mock_main_window.lineEdit_OutputPath.text.return_value = "C:\\test\\output"
        self.mock_main_window.lineEdit_Barcode.text.return_value = "BAT001"
        
        # 调用检查方法
        result = self.calculator.check_input()
        
        # 验证结果
        assert result is False
        mock_message_box.warning.assert_called_once()
    
    @patch('battery_analysis.main.business_logic.battery_calculator.QW.QMessageBox')
    def test_check_input_missing_multiple_fields(self, mock_message_box):
        """测试缺少多个字段的情况"""
        # 设置多个字段为空
        self.mock_main_window.comboBox_BatteryType.currentText.return_value = ""
        self.mock_main_window.comboBox_ConstructionMethod.currentText.return_value = ""
        self.mock_main_window.lineEdit_Barcode.text.return_value = ""
        
        # 设置其他控件返回有效值
        self.mock_main_window.comboBox_Specification_Type.currentText.return_value = "Capacity"
        self.mock_main_window.comboBox_Specification_Method.currentText.return_value = "Constant Current"
        self.mock_main_window.comboBox_Manufacturer.currentText.return_value = "Samsung"
        self.mock_main_window.comboBox_TesterLocation.currentText.return_value = "Lab A"
        self.mock_main_window.comboBox_TestedBy.currentText.return_value = "Test Engineer"
        self.mock_main_window.comboBox_ReportedBy.currentText.return_value = "Report Engineer"
        self.mock_main_window.comboBox_Temperature.currentText.return_value = "25°C"
        self.mock_main_window.lineEdit_InputPath.text.return_value = "C:\\test\\data"
        self.mock_main_window.lineEdit_OutputPath.text.return_value = "C:\\test\\output"
        
        # 调用检查方法
        result = self.calculator.check_input()
        
        # 验证结果
        assert result is False
        mock_message_box.warning.assert_called_once()