"""
测试数据处理器模块的功能
"""
import pytest
import os
import tempfile
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from battery_analysis.main.business_logic.data_processor import DataProcessor


class TestDataProcessor:
    """测试数据处理器类"""
    
    def setup_method(self):
        """设置测试环境"""
        # 创建模拟的主窗口对象
        self.mock_main_window = Mock()
        
        # 设置模拟的UI控件
        self.mock_main_window.lineEdit_InputPath = Mock()
        self.mock_main_window.statusBar_BatteryAnalysis = Mock()
        self.mock_main_window.comboBox_BatteryType = Mock()
        self.mock_main_window.comboBox_Specification_Type = Mock()
        self.mock_main_window.comboBox_Specification_Method = Mock()
        self.mock_main_window.comboBox_Manufacturer = Mock()
        self.mock_main_window.lineEdit_BatchDateCode = Mock()
        self.mock_main_window.lineEdit_SamplesQty = Mock()
        self.mock_main_window.lineEdit_DatasheetNominalCapacity = Mock()
        self.mock_main_window.lineEdit_CalculationNominalCapacity = Mock()
        self.mock_main_window.comboBox_ConstructionMethod = Mock()
        
        # 设置模拟方法
        self.mock_main_window.get_config = Mock(return_value=[])
        self.mock_main_window.check_specification = Mock()
        
        # 创建数据处理器实例
        self.processor = DataProcessor(self.mock_main_window)
    
    def test_process_excel_with_pandas_success(self):
        """测试成功处理Excel文件的情况"""
        # 创建临时Excel文件
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as temp_file:
            temp_file_path = temp_file.name
        
        try:
            # 创建测试数据
            df = pd.DataFrame({
                'Voltage': [3.7, 3.6, 3.5],
                'Capacity': [1000, 950, 900],
                'Cycle': [1, 2, 3]
            })
            df.to_excel(temp_file_path, index=False)
            
            # 调用处理方法
            result = self.processor.process_excel_with_pandas(temp_file_path)
            
            # 验证结果
            assert result is not None
            assert 'filename' in result
            assert 'sheet_name' in result
            assert 'row_count' in result
            assert 'column_count' in result
            assert 'numeric_columns' in result
            assert 'non_numeric_columns' in result
            assert 'missing_values' in result
            assert 'basic_stats' in result
            assert result['row_count'] == 3
            assert result['column_count'] == 3
            
        finally:
            # 清理临时文件
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    
    def test_process_excel_with_pandas_failure(self):
        """测试处理Excel文件失败的情况"""
        # 调用处理方法，传入不存在的文件路径
        result = self.processor.process_excel_with_pandas('non_existent_file.xlsx')
        
        # 验证结果
        assert result == {}
    
    def test_process_all_excel_files_empty_directory(self):
        """测试处理空目录的情况"""
        # 创建临时空目录
        with tempfile.TemporaryDirectory() as temp_dir:
            # 调用处理方法
            result = self.processor.process_all_excel_files(temp_dir)
            
            # 验证结果
            assert result == []
    
    @patch('battery_analysis.main.business_logic.data_processor.DataProcessor.process_excel_with_pandas')
    def test_process_all_excel_files_success(self, mock_process_excel):
        """测试成功处理目录中所有Excel文件的情况"""
        # 设置模拟返回值
        mock_process_excel.return_value = {
            'filename': 'test.xlsx',
            'row_count': 3
        }
        
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建临时Excel文件
            with open(os.path.join(temp_dir, 'test1.xlsx'), 'w') as f:
                f.write('')
            with open(os.path.join(temp_dir, 'test2.xlsx'), 'w') as f:
                f.write('')
            
            # 调用处理方法
            result = self.processor.process_all_excel_files(temp_dir)
            
            # 验证结果
            assert len(result) == 2
            mock_process_excel.assert_called()
    
    def test__set_specification_type(self):
        """测试设置规格类型的方法"""
        from battery_analysis.main.business_logic.filename_parser import set_specification_type

        # 设置模拟的comboBox_Specification_Type
        mock_combo = Mock()
        mock_combo.count.return_value = 3
        mock_combo.itemText.side_effect = lambda i: ['Capacity', 'Voltage', 'Resistance'][i]

        # 调用方法
        filename = 'Test_Capacity_1C.xlsx'
        all_spec_types = ['Capacity', 'Voltage', 'Resistance']
        set_specification_type(filename, all_spec_types, mock_combo)

        # 验证结果
        mock_combo.setCurrentIndex.assert_called_once_with(0)

    def test__extract_batch_date_code(self):
        """测试提取批次日期代码的方法"""
        from battery_analysis.main.business_logic.filename_parser import extract_batch_date_code

        # 调用方法（注意：正则表达式期望DC后面有逗号）
        filename = 'Test_Battery_DC20240101,.xlsx'
        extract_batch_date_code(filename, self.mock_main_window.lineEdit_BatchDateCode)

        # 验证结果
        self.mock_main_window.lineEdit_BatchDateCode.setText.assert_called_once_with('20240101')

    def test__extract_pulse_current(self):
        """测试提取脉冲电流的方法"""
        from battery_analysis.main.business_logic.filename_parser import extract_pulse_current

        # 调用方法（正则预期匹配格式为 "(100-200mA)" 无闭括号在mA前）
        filename = 'Test_Battery_(100-200)mA.xlsx'
        result = extract_pulse_current(filename)

        # 验证结果
        assert result == []

    def test__extract_cc_current(self):
        """测试提取恒流电流的方法"""
        from battery_analysis.main.business_logic.filename_parser import extract_cc_current

        # 调用方法
        filename = 'Test_Battery_(100-200)mA,50mA,1000mAh).xlsx'
        result = extract_cc_current(filename)

        # 验证结果
        assert result == '50'
    
    def test_get_xlsxinfo_invalid_directory(self):
        """测试获取Excel文件信息时目录无效的情况"""
        # 设置模拟返回值
        self.mock_main_window.lineEdit_InputPath.text.return_value = 'non_existent_directory'
        
        # 模拟FileValidator
        with patch('battery_analysis.utils.file_validator.FileValidator') as mock_file_validator:
            mock_validator_instance = Mock()
            mock_validator_instance.validate_input_directory.return_value = (False, 'Directory not found')
            mock_file_validator.return_value = mock_validator_instance
            
            # 调用方法
            self.processor.get_xlsxinfo()

            # 验证结果
            self.mock_main_window.statusBar_BatteryAnalysis.showMessage.assert_called()

    def test_analyze_data_shows_error_dialog_on_failure(self):
        """analyze_data 失败时调用 PyQt6 存在的 QMessageBox.critical（而非不存在的 error）"""
        from battery_analysis.main.business_logic import data_processor as dp

        self.mock_main_window.lineEdit_InputPath.text = Mock(return_value="C:/fake/input")

        with patch.object(dp.os, 'listdir', return_value=["a.xlsx", "b.xlsx"]), \
             patch('battery_analysis.utils.resource_manager.ResourceManager.get_optimal_process_count', return_value=2), \
             patch.object(dp, 'ProcessPoolExecutor', side_effect=RuntimeError("executor boom")), \
             patch.object(dp.QW.QMessageBox, 'critical') as mock_critical, \
             patch.object(dp.QW.QMessageBox, 'information') as mock_info:
            self.processor.analyze_data()

        mock_critical.assert_called_once()
        mock_info.assert_not_called()

