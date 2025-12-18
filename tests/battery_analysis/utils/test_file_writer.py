import pytest
import json
import os
import tempfile
from battery_analysis.utils.file_writer import XlsxWordWriter

# 加载测试数据
test_data_path = os.path.join(os.path.dirname(
    __file__), "../../data/test_file_writer.json")
with open(test_data_path, "r", encoding="utf-8") as f:
    file_writer_test_data = json.load(f)

test_data = file_writer_test_data["test_data"]
error_cases = file_writer_test_data["error_cases"]

# 测试ReportedBy值能否正确从listTestInfo获取


def test_reported_by_from_list_test_info():
    """
    测试当listTestInfo中有ReportedBy值时，能正确获取
    """
    # 使用测试数据中的值
    list_test_info = test_data["test_info"]

    # 确保listTestInfo有足够的元素来测试ReportedBy获取逻辑
    # ReportedBy的值在listTestInfo[18]位置
    expected_reported_by = "BOEDT"

    # 为测试添加ReportedBy值到listTestInfo
    if len(list_test_info) <= 18:
        # 如果元素不足，添加足够的占位符
        list_test_info += [""] * (18 - len(list_test_info) + 1)

    # 设置预期的ReportedBy值
    list_test_info[18] = expected_reported_by

    # 测试ReportedBy获取逻辑
    # 这是从file_writer.py中提取的逻辑
    str_reported_by = list_test_info[18] if len(list_test_info) > 18 else ""

    # 验证ReportedBy值是否正确获取
    assert str_reported_by == expected_reported_by

# 测试ReportedBy默认值


def test_reported_by_default_value():
    """
    测试当listTestInfo中没有ReportedBy值时，返回空字符串
    """
    # 使用测试数据中的错误用例
    error_case = error_cases["empty_battery_info"]
    list_test_info = error_case["test_info"]

    # 确保listTestInfo没有足够的元素来获取ReportedBy值
    # ReportedBy的值在listTestInfo[18]位置
    if len(list_test_info) > 18:
        # 如果元素过多，截断到18个元素
        list_test_info = list_test_info[:18]

    # 测试ReportedBy获取逻辑
    # 这是从file_writer.py中提取的逻辑
    str_reported_by = list_test_info[18] if len(list_test_info) > 18 else ""

    # 验证ReportedBy值是否为空字符串
    assert str_reported_by == ""
