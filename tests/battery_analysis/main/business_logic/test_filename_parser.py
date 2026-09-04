"""文件名解析器 (filename_parser) 测试

测试 filename_parser.py 中的各解析函数，覆盖规格类型匹配、
制造商匹配、批次日期码提取、脉冲电流提取和恒流电流提取。
"""

from unittest.mock import MagicMock

import pytest

from battery_analysis.main.business_logic.filename_parser import (
    extract_batch_date_code,
    extract_cc_current,
    extract_pulse_current,
    set_manufacturer,
    set_specification_method,
    set_specification_type,
)


class TestSetSpecificationType:
    """set_specification_type 测试。"""

    def test_match_longest_first(self):
        """应优先匹配最长的规格类型。"""
        combo = MagicMock()
        types = ["Coin", "Coin Cell", "Pouch"]
        set_specification_type("Test Coin Cell DC2501", types, combo)
        combo.setCurrentIndex.assert_called_once_with(1)  # "Coin Cell" 的索引

    def test_no_match(self):
        """无匹配时不应调用 setCurrentIndex。"""
        combo = MagicMock()
        types = ["Pouch", "Prismatic"]
        set_specification_type("SomeOtherFile", types, combo)
        combo.setCurrentIndex.assert_not_called()

    def test_match_first_type(self):
        """匹配第一个类型时应设置正确索引。"""
        combo = MagicMock()
        types = ["AAA", "BBB"]
        set_specification_type("file_AAA_test", types, combo)
        combo.setCurrentIndex.assert_called_once_with(0)


class TestSetSpecificationMethod:
    """set_specification_method 测试。"""

    def test_match_method(self):
        """应正确匹配规格方法。"""
        combo = MagicMock()
        methods = ["MethodA", "MethodB", "LongMethodC"]
        set_specification_method("file_LongMethodC_test", methods, combo)
        combo.setCurrentIndex.assert_called_once_with(2)

    def test_no_match_method(self):
        """无匹配时不应调用 setCurrentIndex。"""
        combo = MagicMock()
        methods = ["MethodA"]
        set_specification_method("file_other", methods, combo)
        combo.setCurrentIndex.assert_not_called()


class TestSetManufacturer:
    """set_manufacturer 测试。"""

    def test_match_manufacturer(self):
        """应正确匹配制造商。"""
        combo = MagicMock()
        combo.count.return_value = 3
        combo.itemText.side_effect = lambda i: ["Sony", "Panasonic", "LG"][i]
        set_manufacturer("Test_Panasonic_DC2501", combo)
        combo.setCurrentIndex.assert_called_once_with(1)

    def test_no_match_manufacturer(self):
        """无匹配时不应调用 setCurrentIndex。"""
        combo = MagicMock()
        combo.count.return_value = 2
        combo.itemText.side_effect = lambda i: ["Sony", "LG"][i]
        set_manufacturer("Test_Samsung_File", combo)
        combo.setCurrentIndex.assert_not_called()


class TestExtractBatchDateCode:
    """extract_batch_date_code 测试。"""

    def test_dc_simple(self):
        """DC2604 格式应正确提取（无括号时 \\w+ 会贪婪匹配到下一个非 word 字符）。"""
        line_edit = MagicMock()
        extract_batch_date_code("Battery-DC2604-Type", line_edit)
        line_edit.setText.assert_called_once_with("2604")

    def test_dc_with_parentheses(self):
        """DC(2604) 格式应正确提取，括号限制了匹配范围。"""
        line_edit = MagicMock()
        extract_batch_date_code("Battery_DC(2604)_Type", line_edit)
        line_edit.setText.assert_called_once_with("2604")

    def test_dc_with_space_and_parentheses(self):
        """DC (2604) 格式应正确提取。"""
        line_edit = MagicMock()
        extract_batch_date_code("Battery_DC (2604)_Type", line_edit)
        line_edit.setText.assert_called_once_with("2604")

    def test_no_dc_code(self):
        """无 DC 标记时不应调用 setText。"""
        line_edit = MagicMock()
        extract_batch_date_code("Battery_Type_Normal", line_edit)
        line_edit.setText.assert_not_called()

    def test_dc_with_non_word_separator(self):
        """DC 标记后跟非 word 字符分隔时应正确提取。"""
        line_edit = MagicMock()
        extract_batch_date_code("Battery-DC2604-DC2701-Type", line_edit)
        # 两个独立匹配，不满足 len==1 条件，不应调用 setText
        line_edit.setText.assert_not_called()


class TestExtractPulseCurrent:
    """extract_pulse_current 测试。"""

    def test_two_currents(self):
        """两个脉冲电流值，格式为 (100-200mA)。"""
        result = extract_pulse_current("(100-200mA)")
        assert result == [100.0, 200.0]

    def test_multiple_currents(self):
        """多个脉冲电流值。"""
        result = extract_pulse_current("(50-100-200mA)")
        assert result == [50.0, 100.0, 200.0]

    def test_no_match(self):
        """无匹配时返回空列表。"""
        result = extract_pulse_current("SomeFile_no_pulse")
        assert result == []

    def test_decimal_current(self):
        """小数电流值。"""
        result = extract_pulse_current("(12.5-25.0mA)")
        assert result == [12.5, 25.0]


class TestExtractCcCurrent:
    """extract_cc_current 测试。"""

    def test_extract_cc_value(self):
        """应正确提取恒流电流值（格式: mA,<value>mA）。"""
        result = extract_cc_current("(100mA,500mA)")
        assert result == "500"

    def test_no_match(self):
        """无匹配时返回空字符串。"""
        result = extract_cc_current("No_cc_info")
        assert result == ""

    def test_multiple_mA_values(self):
        """多个 mA 值时应返回最后一个。"""
        result = extract_cc_current("(100mA,200mA,300mA)")
        assert result == "300"

    def test_mah_suffix_stripped(self):
        """mAh 后缀应被正确剥离后匹配。"""
        result = extract_cc_current("(100mA,500mAh)")
        # "500mAh" → strip "mAh" → "500" → no mA match → return ""
        assert result == ""
