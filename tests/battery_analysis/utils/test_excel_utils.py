# -*- coding: utf-8 -*-
"""
excel_utils测试
"""

import pytest
from unittest.mock import Mock
from battery_analysis.utils.writers.excel_utils import ws_set_col, ws_result_write_data, num2letter


class TestExcelUtils:
    """Excel工具函数测试类"""

    def test_ws_set_col(self):
        """测试设置Excel工作表列宽"""
        # 创建模拟工作表对象
        mock_worksheet = Mock()
        
        # 调用函数
        ws_set_col(mock_worksheet, 1, 3, 15)
        
        # 验证结果
        mock_worksheet.set_column.assert_called_once_with(1, 3, 15)

    def test_ws_result_write_data_with_integer(self):
        """测试向Excel工作表写入整数数据"""
        # 创建模拟工作表对象和格式对象
        mock_ws_result = Mock()
        mock_format = Mock()
        
        # 调用函数
        ws_result_write_data(1, 1, 100, mock_format, mock_ws_result)
        
        # 验证结果
        mock_ws_result.write.assert_called_once_with(1, 1, 100, mock_format)

    def test_ws_result_write_data_with_float(self):
        """测试向Excel工作表写入浮点数数据"""
        # 创建模拟工作表对象和格式对象
        mock_ws_result = Mock()
        mock_format = Mock()
        
        # 调用函数
        ws_result_write_data(1, 1, 100.5, mock_format, mock_ws_result)
        
        # 验证结果
        mock_ws_result.write.assert_called_once_with(1, 1, 100.5, mock_format)

    def test_ws_result_write_data_with_zero(self):
        """测试向Excel工作表写入零值"""
        # 创建模拟工作表对象和格式对象
        mock_ws_result = Mock()
        mock_format = Mock()
        
        # 调用函数
        ws_result_write_data(1, 1, 0, mock_format, mock_ws_result)
        
        # 验证结果
        mock_ws_result.write.assert_not_called()

    def test_ws_result_write_data_with_string(self):
        """测试向Excel工作表写入字符串数据"""
        # 创建模拟工作表对象和格式对象
        mock_ws_result = Mock()
        mock_format = Mock()
        
        # 调用函数
        ws_result_write_data(1, 1, "Test String", mock_format, mock_ws_result)
        
        # 验证结果
        mock_ws_result.write.assert_called_once_with(1, 1, "Test String", mock_format)

    def test_num2letter(self):
        """测试将数字列索引转换为字母"""
        # 测试不同的列索引
        assert num2letter(0) == "A"  # 0 -> A
        assert num2letter(1) == "B"  # 1 -> B
        assert num2letter(25) == "Z"  # 25 -> Z
        assert num2letter(26) == "AA"  # 26 -> AA
        assert num2letter(27) == "AB"  # 27 -> AB

    def test_num2letter_boundaries(self):
        """Z/AA/AZ 列边界——get_column_letter 与 xl_col_to_name 计数差异回归锁"""
        assert num2letter(25) == "Z"
        assert num2letter(26) == "AA"
        assert num2letter(51) == "AZ"

    def test_num2letter_negative_raises(self):
        """负数列索引应响亮失败（与 openpyxl get_column_letter 行为一致）"""
        with pytest.raises(ValueError, match="Column index must be >= 0"):
            num2letter(-1)
