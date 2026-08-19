"""xlsx_reader 读取器测试（calamine 引擎回归锁）"""
import pandas as pd

from battery_analysis.utils.readers.xlsx_reader import extract_test_date_from_xls
from battery_analysis.utils.readers.xlsx_reader import read_xlsx_sheets


class TestReadXlsxSheets:
    def test_returns_three_dataframes(self, sample_xlsx):
        cycle_df, step_df, record_df = read_xlsx_sheets(str(sample_xlsx))
        assert isinstance(cycle_df, pd.DataFrame)
        assert isinstance(step_df, pd.DataFrame)
        assert isinstance(record_df, pd.DataFrame)

    def test_calamine_matches_openpyxl_content(self, sample_xlsx):
        """calamine 读取结果与 openpyxl 完全一致（值/类型回归锁）"""
        cycle_df, step_df, record_df = read_xlsx_sheets(str(sample_xlsx))

        expected_cycle = pd.read_excel(sample_xlsx, sheet_name=0, header=None, engine="openpyxl")
        expected_step = pd.read_excel(sample_xlsx, sheet_name=1, header=None, engine="openpyxl")
        expected_record = pd.read_excel(sample_xlsx, sheet_name=2, header=None, engine="openpyxl")

        pd.testing.assert_frame_equal(cycle_df, expected_cycle, check_exact=True)
        pd.testing.assert_frame_equal(step_df, expected_step, check_exact=True)
        pd.testing.assert_frame_equal(record_df, expected_record, check_exact=True)


class TestExtractTestDate:
    def test_from_test_date_cell(self, sample_xlsx_with_test_date):
        """Test Date 单元格右侧的日期值（10.06.2025 - 08.07.2025 取起始日）"""
        assert extract_test_date_from_xls(str(sample_xlsx_with_test_date)) == "20250610"

    def test_from_filename(self, tmp_path):
        """无 Test Date 单元格时回退文件名解析"""
        import openpyxl

        file_path = tmp_path / "test_20250715_data.xlsx"
        wb = openpyxl.Workbook()
        ws0 = wb.active
        ws0.title = "Cycle"
        ws0.append(["Cycle#", "CycleBegin", "CycleEnd"])
        ws0.append([1, "2025-06-10 08:00:00", "2025-06-10 08:30:00"])
        wb.save(file_path)
        assert extract_test_date_from_xls(str(file_path)) == "20250715"

    def test_broken_file_returns_default(self, tmp_path):
        broken = tmp_path / "broken.xlsx"
        broken.write_bytes(b"not a real xlsx file")
        assert extract_test_date_from_xls(str(broken)) == "00000000"
