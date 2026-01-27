import pytest
from unittest.mock import Mock, patch
from battery_analysis.utils.battery_analysis import BatteryAnalysis


class TestBatteryAnalysis:
    def test_uba_get_test_date_from_excel(self):
        # 测试日期提取方法
        test_file = "test_file.xlsx"
        with patch('battery_analysis.utils.battery_analysis.rd.open_workbook') as mock_open_workbook:
            # 设置mock对象
            mock_workbook = Mock()
            mock_open_workbook.return_value = mock_workbook
            mock_sheet = Mock()
            mock_workbook.sheets.return_value = [mock_sheet]
            mock_sheet.nrows = 10
            mock_sheet.ncols = 5
            
            # 模拟单元格值，包含Test Date
            def mock_cell_value(row, col):
                if row == 0 and col == 0:
                    return "Test Date"
                elif row == 0 and col == 1:
                    return "2025-01-01"
                return ""
            
            mock_sheet.cell_value = mock_cell_value
            
            # 创建实例并测试方法
            analysis = Mock(spec=BatteryAnalysis)
            analysis.UBA_GetTestDateFromExcel = BatteryAnalysis.UBA_GetTestDateFromExcel.__get__(analysis)
            result = analysis.UBA_GetTestDateFromExcel(test_file)
            assert isinstance(result, str)

    def test_str_compare_date(self):
        # 测试日期比较方法
        date1 = "2025-01-01 12:00:00"
        date2 = "2025-01-02 12:00:00"
        
        analysis = Mock(spec=BatteryAnalysis)
        analysis._str_compare_date = BatteryAnalysis._str_compare_date.__get__(analysis)
        
        # 测试获取较早日期
        result = analysis._str_compare_date(date1, date2, True)
        assert result == date1
        
        # 测试获取较晚日期
        result = analysis._str_compare_date(date1, date2, False)
        assert result == date2