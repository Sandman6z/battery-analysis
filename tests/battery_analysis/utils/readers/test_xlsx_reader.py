"""xlsx_reader 读取器测试（calamine 引擎回归锁）"""
import pandas as pd

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

        pd.testing.assert_frame_equal(cycle_df, expected_cycle)
        pd.testing.assert_frame_equal(step_df, expected_step)
        pd.testing.assert_frame_equal(record_df, expected_record)
