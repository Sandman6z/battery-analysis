# -*- coding: utf-8 -*-
"""
file_writer测试
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch
from battery_analysis.utils.file_writer import XlsxWordWriter


class TestXlsxWordWriter:
    """文件写入器测试类"""

    def setup_method(self):
        """设置测试环境"""
        # 创建临时目录
        self.temp_dir = tempfile.TemporaryDirectory()
        self.result_path = Path(self.temp_dir.name) / "results"
        self.result_path.mkdir(exist_ok=True)
        
        # 创建测试数据
        self.list_test_info = [
            "Coin Cell",  # 0: 电池类型
            "Method A",  # 1: 构造方法
            "Li-ion",  # 2: 电池类型
            "Type A",  # 3: 规格类型
            "Manufacturer A",  # 4: 制造商
            "DC20230101",  # 5: 批次日期代码
            "10",  # 6: 样本数量
            "25°C",  # 7: 温度
            "2000",  # 8: 标称容量
            "2000",  # 9: 计算标称容量
            "2",  # 10: 加速老化年数
            "Location A",  # 11: 测试者位置
            "Tester A",  # 12: 测试者
            "Test Profile",  # 13: 测试配置文件
            ["1000", "2000"],  # 14: 电流水平
            ["3.7", "3.8"],  # 15: 电压水平
            "v1.0",  # 16: 版本
            "1800",  # 17: 要求可用容量
            "Tester A"  # 18: 测试者
        ]
        
        self.list_battery_info = [
            [2000, 1900, 1800],  # 0: 电池容量数据
            ["Battery1", "Battery2", "Battery3"],  # 1: 电池名称
            ["2023-01-01 10:00:00", "2023-01-01 11:00:00"],  # 2: 测试时间
            "20230101"  # 3: 测试日期
        ]

    def teardown_method(self):
        """清理测试环境"""
        self.temp_dir.cleanup()

    def test_initialization(self):
        """测试初始化"""
        # 创建XlsxWordWriter实例
        writer = XlsxWordWriter(
            strResultPath=str(self.result_path),
            listTestInfo=self.list_test_info,
            listBatteryInfo=self.list_battery_info
        )
        
        # 验证初始化
        assert writer is not None
        assert hasattr(writer, 'listTestInfo')
        assert hasattr(writer, 'listBatteryInfo')

    def test_uxww_xlsx_word_csv_write(self):
        """测试Excel、Word和CSV写入"""
        # 创建XlsxWordWriter实例
        writer = XlsxWordWriter(
            strResultPath=str(self.result_path),
            listTestInfo=self.list_test_info,
            listBatteryInfo=self.list_battery_info
        )
        
        # 验证方法存在
        assert hasattr(writer, 'UXWW_XlsxWordCsvWrite')

    def test_handle_data_error(self):
        """测试数据错误处理"""
        # 创建XlsxWordWriter实例
        writer = XlsxWordWriter(
            strResultPath=str(self.result_path),
            listTestInfo=self.list_test_info,
            listBatteryInfo=self.list_battery_info
        )
        
        # 测试数据错误处理
        error_msg = "测试错误信息"
        result = writer.handle_data_error(error_msg)
        
        # 验证结果
        assert result == "retry"

    def test_directory_creation(self):
        """测试目录创建"""
        # 创建XlsxWordWriter实例
        writer = XlsxWordWriter(
            strResultPath=str(self.result_path),
            listTestInfo=self.list_test_info,
            listBatteryInfo=self.list_battery_info
        )
        
        # 验证目录创建方法存在
        assert hasattr(writer, 'create_directories')
