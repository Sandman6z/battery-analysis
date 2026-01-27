import pytest
from unittest.mock import Mock, patch
from battery_analysis.utils.csv_utils import csv_write


class TestCsvUtils:
    def test_csv_write_with_string(self):
        """测试使用字符串调用csv_write函数"""
        # 创建模拟对象
        mock_csv_writer = Mock()
        buffer = []
        buffer_size = 0
        max_buffer_size = 10
        
        # 测试字符串消息
        test_message = "Test message"
        result = csv_write(test_message, mock_csv_writer, buffer, buffer_size, max_buffer_size)
        
        # 验证结果
        assert result == 1
        assert len(buffer) == 1
        assert buffer[0] == [test_message]

    def test_csv_write_with_list(self):
        """测试使用列表调用csv_write函数"""
        # 创建模拟对象
        mock_csv_writer = Mock()
        buffer = []
        buffer_size = 0
        max_buffer_size = 10
        
        # 测试列表消息
        test_message = [1, 2, 0, 4]
        result = csv_write(test_message, mock_csv_writer, buffer, buffer_size, max_buffer_size)
        
        # 验证结果
        assert result == 1
        assert len(buffer) == 1
        assert buffer[0] == [1, 2, "", 4]  # 0 应该被替换为空字符串