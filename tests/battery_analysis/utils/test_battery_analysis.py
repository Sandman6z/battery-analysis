import pytest
from unittest.mock import Mock, patch
from battery_analysis.utils.exceptions import BatteryAnalysisException
from battery_analysis.utils.processors.battery_analysis import BatteryAnalysis


class TestBatteryAnalysis:
    def test_uba_get_test_date_from_excel(self, sample_xlsx_with_test_date):
        """UBA_GetTestDateFromExcel 应委托 extract_test_date_from_xls 返回 YYYYMMDD"""
        analysis = Mock(spec=BatteryAnalysis)
        analysis.UBA_GetTestDateFromExcel = BatteryAnalysis.UBA_GetTestDateFromExcel.__get__(analysis)
        result = analysis.UBA_GetTestDateFromExcel(str(sample_xlsx_with_test_date))
        assert result == "20250610"

    def test_str_compare_date(self):
        # 测试日期比较方法
        date1 = "2025-01-01 12:00:00"
        date2 = "2025-01-02 12:00:00"

        # 直接调用静态方法，不经过 Mock
        result = BatteryAnalysis._str_compare_date(date1, date2, True)
        assert result == date1

        result = BatteryAnalysis._str_compare_date(date1, date2, False)
        assert result == date2

    def test_parallel_process_file_normalizes_read_failure(self, sample_xlsx):
        """read_xlsx_sheets 失败时应归一化为 BatteryAnalysisException，而非走 xlrd 回退"""
        args = (str(sample_xlsx), [500, 1000], [3.0, 4.0])
        with patch(
            "battery_analysis.utils.processors.battery_analysis.read_xlsx_sheets",
            side_effect=ValueError("simulated corrupt file"),
        ):
            with pytest.raises(BatteryAnalysisException, match="Failed to read Excel file"):
                BatteryAnalysis._parallel_process_file(args)