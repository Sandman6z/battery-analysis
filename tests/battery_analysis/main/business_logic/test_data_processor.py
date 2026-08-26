"""
测试数据处理器模块的功能
"""
import pandas as pd
from unittest.mock import Mock, patch
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

    def test_on_scan_finished_dispatches_background_processing(self):
        """扫描完成 → 后台线程处理 Excel 解析，主线程不阻塞"""
        self.mock_main_window.lineEdit_InputPath.text.return_value = '/fake/dir'
        with patch.object(self.processor, 'run_in_background') as mock_run:
            self.processor._on_scan_finished(['a.xlsx', 'b.xlsx'])
        mock_run.assert_called_once()
        task_func, on_finished, on_error, input_dir, excel_files = mock_run.call_args[0]
        assert task_func == self.processor._process_excel_files_task
        assert on_finished == self.processor._on_excel_files_processed
        assert on_error == self.processor._on_excel_files_process_error
        assert input_dir == '/fake/dir'
        assert excel_files == ['a.xlsx', 'b.xlsx']
        assert self.processor._scanning_input_dir == '/fake/dir'

    def test_on_scan_finished_empty_files_no_background(self):
        """无文件 → 走 _handle_no_excel_files，不派发后台任务"""
        with patch.object(self.processor, '_handle_no_excel_files') as mock_handle, \
             patch.object(self.processor, 'run_in_background') as mock_run:
            self.processor._on_scan_finished([])
        mock_handle.assert_called_once()
        mock_run.assert_not_called()

    def test_process_excel_files_task_returns_data_and_errors(self, tmp_path):
        """后台任务只读文件：返回 (excel_files, excel_data, error_files)，不碰 UI

        文件名须通过 validate_excel_filename（含 DC / mA / 逗号 / 温度），
        否则文件在内容校验前就被拒绝，无法测到读取路径。
        """
        valid = tmp_path / 'DC1,mA1.xlsx'
        pd.DataFrame({'Capacity': [1000, 2000]}).to_excel(valid, index=False)
        invalid = tmp_path / 'DC2,mA2.xlsx'
        invalid.write_bytes(b'not a real xlsx')
        result = self.processor._process_excel_files_task(str(tmp_path), ['DC1,mA1.xlsx', 'DC2,mA2.xlsx'])
        excel_files, excel_data, error_files = result
        assert excel_files == ['DC1,mA1.xlsx', 'DC2,mA2.xlsx']
        assert len(excel_data) == 1
        assert excel_data[0]['filename'] == 'DC1,mA1.xlsx'
        assert excel_data[0]['row_count'] == 2
        assert len(error_files) == 1
        assert error_files[0][0] == 'DC2,mA2.xlsx'

    def test_on_excel_files_processed_success(self):
        """处理成功 → 更新 UI + 解析首个文件 + 重连规格信号"""
        self.processor._scanning_input_dir = '/fake/dir'
        self.mock_main_window.lineEdit_InputPath.text.return_value = '/fake/dir'
        excel_files = ['a.xlsx']
        excel_data = [{'filename': 'a.xlsx'}]
        with patch.object(self.processor, '_update_ui_with_excel_info') as mock_ui, \
             patch.object(self.processor, '_process_first_excel_file') as mock_first, \
             patch.object(self.processor, '_reconnect_specification_signals') as mock_reconnect:
            self.processor._on_excel_files_processed((excel_files, excel_data, []))
        mock_ui.assert_called_once_with(excel_files, excel_data)
        mock_first.assert_called_once_with('a.xlsx')
        mock_reconnect.assert_called_once()

    def test_on_excel_files_processed_no_valid_data_sets_error(self):
        """隔离 not excel_data 分支（无有效文件）→ 设置错误提示，不进入成功流程

        注：(['a.xlsx'], [], []) 是 _process_excel_files_task 不可能返回的组合
        （非空 excel_files 时每文件必进一个桶），此处仅用于隔离 not excel_data 分支。
        """
        self.processor._scanning_input_dir = '/fake/dir'
        self.mock_main_window.lineEdit_InputPath.text.return_value = '/fake/dir'
        self.mock_main_window.checker_input_xlsx = Mock()
        with patch.object(self.processor, '_update_ui_with_excel_info') as mock_ui:
            self.processor._on_excel_files_processed((['a.xlsx'], [], []))
        mock_ui.assert_not_called()
        self.mock_main_window.checker_input_xlsx.set_error.assert_called()
        self.mock_main_window.statusBar_BatteryAnalysis.showMessage.assert_called()

    def test_on_excel_files_processed_shows_error_dialog(self):
        """存在错误文件 → 主线程弹 QMessageBox 明细"""
        from battery_analysis.main.business_logic import data_processor as dp
        self.processor._scanning_input_dir = '/fake/dir'
        self.mock_main_window.lineEdit_InputPath.text.return_value = '/fake/dir'
        mock_msgbox = Mock()
        with patch.object(dp.QW, 'QMessageBox', return_value=mock_msgbox):
            self.processor._on_excel_files_processed((['a.xlsx'], [], [('a.xlsx', 'bad format')]))
        mock_msgbox.exec.assert_called_once()
        mock_msgbox.setDetailedText.assert_called_once()

    def test_on_excel_files_processed_discards_stale_result(self):
        """输入路径已变更 → 丢弃旧路径的解析结果，不更新 UI"""
        self.processor._scanning_input_dir = '/old/dir'
        self.mock_main_window.lineEdit_InputPath.text.return_value = '/new/dir'
        with patch.object(self.processor, '_update_ui_with_excel_info') as mock_ui, \
             patch.object(self.processor, '_process_first_excel_file') as mock_first, \
             patch.object(self.processor, '_reconnect_specification_signals') as mock_reconnect:
            self.processor._on_excel_files_processed((['a.xlsx'], [{'filename': 'a.xlsx'}], []))
        mock_ui.assert_not_called()
        mock_first.assert_not_called()
        mock_reconnect.assert_not_called()

    def test_on_excel_files_process_error_discards_stale_result(self):
        """输入路径已变更 → 错误兜底同样丢弃"""
        self.processor._scanning_input_dir = '/old/dir'
        self.mock_main_window.lineEdit_InputPath.text.return_value = '/new/dir'
        with patch.object(self.processor.logger, 'error') as mock_log:
            self.processor._on_excel_files_process_error('boom')
        mock_log.assert_not_called()

    def test_on_excel_files_process_error_sets_ui_and_reconnects(self):
        """后台任务异常 → 记录日志 + checker/状态栏报错 + 重连规格信号"""
        self.processor._scanning_input_dir = '/fake/dir'
        self.mock_main_window.lineEdit_InputPath.text.return_value = '/fake/dir'
        self.mock_main_window.checker_input_xlsx = Mock()
        with patch.object(self.processor, '_reconnect_specification_signals') as mock_reconnect, \
             patch.object(self.processor.logger, 'error') as mock_log:
            self.processor._on_excel_files_process_error('boom')
        mock_log.assert_called_once()
        self.mock_main_window.checker_input_xlsx.set_error.assert_called()
        self.mock_main_window.statusBar_BatteryAnalysis.showMessage.assert_called()
        mock_reconnect.assert_called_once()

    def test_on_excel_files_processed_mixed_valid_and_invalid(self):
        """部分成功部分失败 → 既弹错误框，也用有效文件更新 UI"""
        from battery_analysis.main.business_logic import data_processor as dp
        mock_msgbox = Mock()
        self.processor._scanning_input_dir = '/fake/dir'
        self.mock_main_window.lineEdit_InputPath.text.return_value = '/fake/dir'
        self.mock_main_window.checker_input_xlsx = Mock()
        with patch.object(dp.QW, 'QMessageBox', return_value=mock_msgbox), \
             patch.object(self.processor, '_update_ui_with_excel_info') as mock_ui, \
             patch.object(self.processor, '_process_first_excel_file') as mock_first, \
             patch.object(self.processor, '_reconnect_specification_signals') as mock_reconnect:
            self.processor._on_excel_files_processed(
                (['a.xlsx', 'b.xlsx'], [{'filename': 'a.xlsx'}], [('b.xlsx', 'bad')]))
        mock_msgbox.exec.assert_called_once()
        mock_ui.assert_called_once_with(['a.xlsx', 'b.xlsx'], [{'filename': 'a.xlsx'}])
        mock_first.assert_called_once_with('a.xlsx')  # Fix 4 生效后是 excel_data[0]['filename']
        mock_reconnect.assert_called_once()
