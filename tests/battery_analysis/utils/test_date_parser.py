"""测试日期解析工具"""

from battery_analysis.utils.date_parser import _parse_date_string, parse_test_date


class TestParseDateString:
    def test_yyyymmdd(self):
        """YYYYMMDD 格式直接返回"""
        assert _parse_date_string("20250101") == "20250101"

    def test_yyyymmdd_digit_only(self):
        """只有数字且长度为8才认为是 YYYYMMDD"""
        assert _parse_date_string("12345678") == "12345678"

    def test_yyyymmdd_too_short(self):
        """长度不足8的纯数字不认为是 YYYYMMDD"""
        assert _parse_date_string("2025010") is None

    def test_hyphen_format(self):
        """YYYY-MM-DD 格式"""
        assert _parse_date_string("2025-01-01") == "20250101"

    def test_slash_format(self):
        """YYYY/MM/DD 格式"""
        assert _parse_date_string("2025/01/01") == "20250101"

    def test_hyphen_with_time(self):
        """YYYY-MM-DD HH:MM:SS 格式，忽略时间部分"""
        assert _parse_date_string("2025-01-01 12:00:00") == "20250101"

    def test_slash_with_time(self):
        """YYYY/MM/DD HH:MM:SS 格式"""
        assert _parse_date_string("2025/01/01 12:00:00") == "20250101"

    def test_empty_string(self):
        assert _parse_date_string("") is None

    def test_none(self):
        assert _parse_date_string(None) is None

    def test_single_number(self):
        """缺少分隔符的纯数字非8位返回 None"""
        assert _parse_date_string("2025010") is None


class TestParseTestDate:
    def test_test_date_yyyymmdd(self):
        """test_date 为 YYYYMMDD 时直接使用"""
        assert parse_test_date("20250101") == "20250101"

    def test_test_date_hyphen(self):
        """test_date 为 YYYY-MM-DD 时解析"""
        assert parse_test_date("2025-01-01") == "20250101"

    def test_test_date_slash(self):
        """test_date 为 YYYY/MM/DD 时解析"""
        assert parse_test_date("2025/01/01") == "20250101"

    def test_test_date_unknown_format(self):
        """test_date 不是任何已知格式但非空，依然使用"""
        assert parse_test_date("2025.01.01") == "2025.01.01"

    def test_test_date_preferred_over_cycle(self):
        """test_date 有效时优先，忽略 original_cycle_date"""
        result = parse_test_date("20250101", original_cycle_date="2020-01-01")
        assert result == "20250101"

    def test_fallback_to_original_cycle(self):
        """test_date 为空时尝试 original_cycle_date"""
        result = parse_test_date("", original_cycle_date="2020-01-01")
        assert result == "20200101"

    def test_fallback_to_original_cycle_with_time(self):
        """original_cycle_date 带时间时正确解析"""
        result = parse_test_date("", original_cycle_date="2020-01-01 10:30:00")
        assert result == "20200101"

    def test_fallback_to_cycle_slash(self):
        """original_cycle_date 为斜杠格式"""
        result = parse_test_date("", original_cycle_date="2020/01/01")
        assert result == "20200101"

    def test_fallback_to_cycle_unknown_format(self):
        """original_cycle_date 不是已知格式但非空，依然使用"""
        result = parse_test_date("", original_cycle_date="2020.01.01")
        assert result == "2020.01.01"

    def test_fallback_to_third(self):
        """前两个都无效时尝试 fallback_date_str"""
        result = parse_test_date("", "",
                                 fallback_date_str="2022-12-31 08:00:00")
        assert result == "20221231"

    def test_all_fail(self):
        """全部失败时返回 00000000"""
        assert parse_test_date("", "", "") == "00000000"

    def test_all_fail_none(self):
        assert parse_test_date("", None, None) == "00000000"
