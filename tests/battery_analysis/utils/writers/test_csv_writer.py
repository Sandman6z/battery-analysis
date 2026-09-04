"""CSV 写入器 (CsvWriter) 测试

测试 csv_writer.py 中 CsvWriter 类的文件创建、header 写入、
统计数据写入、空数据处理和路径拼接逻辑。
"""

import csv
import os
from unittest.mock import patch

from battery_analysis.utils.writers.csv_writer import CsvWriter


def _make_test_info():
    """构造 CsvWriter 所需的 listTestInfo 模拟数据（16 元素列表）。"""
    return [
        None,  # 0
        None,  # 1
        "TypeA",  # 2  battery type
        "MethodB",  # 3  construction method
        "ManufacturerX",  # 4  manufacturer
        "DC2501",  # 5  batch date code
        "25.0",  # 6  temperature display
        "25:00",  # 7  temperature (含冒号，用于路径)
        None,  # 8
        None,  # 9
        None,  # 10
        None,  # 11
        None,  # 12
        "Profile1",  # 13  test profile
        [100, 200],  # 14  current levels
        [3.0, 3.5],  # 15  voltage levels
    ]


def _make_battery_info(num_batteries=2, num_cells=4):
    """构造 listBatteryInfo 模拟数据。"""
    charge_data = [[10.0 + i + j * 0.1 for i in range(num_cells)] for j in range(num_batteries)]
    names = [f"Battery_{i}" for i in range(num_batteries)]
    times = ["2025-01-01 00:00:00", "2025-01-02 00:00:00"]
    return [charge_data, names, times]


class TestCsvWriterInit:
    """CsvWriter 初始化相关测试。"""

    def test_csv_path_construction_colon_replaced(self, tmp_path):
        """温度字段中的冒号应被替换为下划线。"""
        test_info = _make_test_info()
        battery_info = _make_battery_info()
        writer = CsvWriter(str(tmp_path), test_info, battery_info)
        basename = os.path.basename(writer.strResultCsvPath)
        assert ":" not in basename
        assert "25_00" in basename

    def test_csv_path_contains_components(self, tmp_path):
        """CSV 路径应包含制造商、类型、方法等关键组件。"""
        test_info = _make_test_info()
        battery_info = _make_battery_info()
        writer = CsvWriter(str(tmp_path), test_info, battery_info)
        path = writer.strResultCsvPath
        assert "ManufacturerX" in path
        assert "TypeA" in path
        assert "MethodB" in path
        assert path.endswith(".csv")

    def test_battery_num_computed(self, tmp_path):
        """电池数量应从 battery_info 正确计算。"""
        test_info = _make_test_info()
        battery_info = _make_battery_info(num_batteries=3)
        writer = CsvWriter(str(tmp_path), test_info, battery_info)
        assert writer.intBatteryNum == 3


class TestCsvWriterWrite:
    """CsvWriter.write() 写入逻辑测试。"""

    def test_write_creates_file(self, tmp_path):
        """write() 应创建 CSV 文件。"""
        test_info = _make_test_info()
        battery_info = _make_battery_info()
        writer = CsvWriter(str(tmp_path), test_info, battery_info)
        writer.write()
        assert os.path.exists(writer.strResultCsvPath)
        with open(writer.strResultCsvPath, encoding="utf-8") as f:
            content = f.read()
        assert len(content) > 0

    def test_write_header_info(self, tmp_path):
        """CSV header 应包含版本号、温度、制造商等信息。"""
        test_info = _make_test_info()
        battery_info = _make_battery_info()
        writer = CsvWriter(str(tmp_path), test_info, battery_info)
        writer.write()

        with open(writer.strResultCsvPath, encoding="utf-8") as f:
            content = f.read()

        assert "#BEGIN HEADER" in content
        assert "#END HEADER" in content
        assert "#Version:" in content
        assert "#Temperature:" in content
        assert "#Battery Manufacturer:" in content
        assert "ManufacturerX" in content
        assert "#Test Profile:" in content
        assert "Profile1" in content

    def test_write_statistics(self, tmp_path):
        """CSV 应包含 Mean、Median、Std 等统计行。"""
        test_info = _make_test_info()
        battery_info = _make_battery_info()
        writer = CsvWriter(str(tmp_path), test_info, battery_info)
        writer.write()

        with open(writer.strResultCsvPath, encoding="utf-8") as f:
            content = f.read()

        for label in ["Mean", "Median", "Std. Var.", "Minimum", "Maximum"]:
            assert label in content, f"Missing statistic: {label}"

    def test_write_with_empty_data(self, tmp_path):
        """空电池数据（0 个电池）应能正常写入，不抛异常。"""
        test_info = _make_test_info()
        battery_info = [[], [], ["2025-01-01", "2025-01-02"]]
        # 0 个电池
        writer = CsvWriter(str(tmp_path), test_info, battery_info)
        # 不应抛异常
        writer.write()

        with open(writer.strResultCsvPath, encoding="utf-8") as f:
            content = f.read()
        assert "#BEGIN HEADER" in content

    def test_write_battery_names_in_output(self, tmp_path):
        """CSV 应包含每个电池的名称行。"""
        test_info = _make_test_info()
        battery_info = _make_battery_info(num_batteries=2)
        writer = CsvWriter(str(tmp_path), test_info, battery_info)
        writer.write()

        with open(writer.strResultCsvPath, encoding="utf-8") as f:
            content = f.read()

        assert "Battery_0" in content
        assert "Battery_1" in content
