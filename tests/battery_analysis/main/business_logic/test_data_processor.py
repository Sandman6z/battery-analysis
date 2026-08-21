"""
测试数据处理器模块的功能
"""
import pickle

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
    
    @patch('battery_analysis.main.business_logic.data_processor.ProcessPoolExecutor')
    @patch('battery_analysis.utils.resource_manager.ResourceManager.get_optimal_process_count', return_value=2)
    @patch('battery_analysis.main.business_logic.data_processor._read_excel_worker')
    def test_process_all_excel_files_success(self, mock_read_excel_worker, mock_opt_count, mock_pool_cls):
        """测试成功处理目录中所有Excel文件的情况"""
        expected_info = {'filename': 'test.xlsx', 'row_count': 3}
        mock_read_excel_worker.return_value = expected_info

        # 用同步 executor 替身：在父进程内直接调用 worker，
        # 保证 worker mock 可被断言且不依赖真实进程 spawn
        from concurrent.futures import Future

        def fake_submit(fn, *args, **kwargs):
            fut = Future()
            fut.set_result(fn(*args, **kwargs))
            return fut

        executor_mock = mock_pool_cls.return_value.__enter__.return_value
        executor_mock.submit.side_effect = fake_submit

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
        mock_read_excel_worker.assert_called()
        # 进程池 submit 的目标必须是模块级 worker（spy），而非实例绑定方法
        mock_pool_cls.assert_called_once_with(max_workers=2)
        for call in executor_mock.submit.call_args_list:
            assert call.args[0] is mock_read_excel_worker
        # 缓存由主进程写入（每个成功文件一条，key 为绝对路径）
        assert len(self.processor._cache['excel_files']) == 2
    
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


class TestProcessPoolFix:
    def test_worker_is_picklable_module_level(self):
        """模块级 worker 可 pickle；实例绑定方法不可 pickle（修复必要性证明）"""
        from battery_analysis.main.business_logic import data_processor
        pickle.dumps(data_processor._read_excel_worker)  # 不应抛
        with pytest.raises((pickle.PicklingError, AttributeError, TypeError)):
            pickle.dumps(DataProcessor(Mock()).process_excel_with_pandas)

    def test_process_all_excel_files_real_pool_skips_bad_files(self, tmp_path):
        """真实进程池 smoke test：worker 可 pickle、坏文件被跳过不崩溃、池真实创建

        目录含 1 个合法文件 + 3 个内容损坏文件：合法文件正常返回，损坏文件被跳过。
        用 wraps 包真实 ProcessPoolExecutor 的 spy 断言池被创建 —— 串行回退路径不创建池，
        从而区分"真并行"与"pickle 失败后静默全串行"。
        """
        for name in ["DC1,mA1.xlsx", "DC1,mA2.xlsx", "bad.xlsx"]:
            (tmp_path / name).write_bytes(b"not a real excel")
        pd.DataFrame({"Voltage": [3.7, 3.6], "Capacity": [1000, 950]}).to_excel(
            tmp_path / "good.xlsx", index=False)

        from concurrent.futures import ProcessPoolExecutor
        from battery_analysis.main.business_logic import data_processor as dp

        processor = DataProcessor(Mock())
        with patch.object(dp, "ProcessPoolExecutor", wraps=ProcessPoolExecutor) as mock_pool:
            result = processor.process_all_excel_files(str(tmp_path))

        mock_pool.assert_called()  # 池被创建 → 走真并行而非串行回退
        # 三个文件内容损坏 → read_excel_file 返回 {} → 全部跳过；仅合法文件成功返回
        assert [r["filename"] for r in result] == ["good.xlsx"]

    def test_process_all_excel_files_re_raises_broken_process_pool(self, tmp_path):
        """BrokenProcessPool 不被 per-future except 吞掉：re-raise 触发外层串行回退兜底

        worker 进程硬崩溃（原生库 segfault/OOM）时剩余 future 全抛 BrokenProcessPool，
        它必须传播到外层 except（串行重读兜底），而非被当"不可读文件"跳过静默返回部分数据。
        """
        from concurrent.futures import Future
        from concurrent.futures.process import BrokenProcessPool
        from battery_analysis.main.business_logic import data_processor as dp

        for name in ["a.xlsx", "b.xlsx"]:
            (tmp_path / name).write_bytes(b"not a real excel")

        # executor 替身：submit 返回的 future 在 result() 时抛 BrokenProcessPool（模拟 worker 崩溃）
        class _BrokenExecutor:
            def __init__(self, *args, **kwargs):
                pass

            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

            def submit(self, fn, *args, **kwargs):
                fut = Future()
                fut.set_exception(BrokenProcessPool("worker process died"))
                return fut

        processor = DataProcessor(Mock())
        expected = {'filename': 'a.xlsx', 'row_count': 3}
        with patch.object(dp, 'ProcessPoolExecutor', _BrokenExecutor), \
             patch('battery_analysis.utils.resource_manager.ResourceManager.get_optimal_process_count', return_value=2), \
             patch.object(processor, 'process_excel_with_pandas', return_value=expected) as mock_serial:
            result = processor.process_all_excel_files(str(tmp_path))

        # BrokenProcessPool 被 re-raise → 外层 except → 串行回退读取全部文件
        assert len(result) == 2
        mock_serial.assert_called()
