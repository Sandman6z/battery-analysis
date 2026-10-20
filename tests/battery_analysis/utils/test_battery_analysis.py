from unittest.mock import Mock, patch

import pytest

from battery_analysis.utils.exceptions import BatteryAnalysisException
from battery_analysis.utils.processors.battery_analysis import BatteryAnalysis


class TestBatteryAnalysis:
    def test_uba_get_test_date_from_excel(self, sample_xlsx_with_test_date):
        """UBA_GetTestDateFromExcel 应委托 extract_test_date_from_xls 返回 YYYYMMDD"""
        analysis = Mock(spec=BatteryAnalysis)
        analysis.UBA_GetTestDateFromExcel = BatteryAnalysis.UBA_GetTestDateFromExcel.__get__(
            analysis
        )
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

    def test_failed_channel_keeps_its_slot_and_marks_missing(self, tmp_path, monkeypatch):
        import json

        info = [""] * 19
        info[14], info[15], info[16], info[7] = [30], [3.0], "1.0", "Room"
        (tmp_path / "v1.0").mkdir()

        def process(args):
            if args[0].endswith("bad.ndax"):
                raise ValueError("broken channel")
            return ("good", [10], [[2]], [[3.0]], [[10]],
                    ["2025-06-10 10:01:49", "2025-06-10 11:01:49"], [])

        monkeypatch.setattr(BatteryAnalysis, "_parallel_process_file", staticmethod(process))
        analysis = BatteryAnalysis(
            str(tmp_path), str(tmp_path), info,
            input_files=[str(tmp_path / "bad.ndax"), str(tmp_path / "good.ndax")],
            decision_callback=lambda anomalies: True,
        )
        assert analysis.UBA_GetErrorLog() == ""
        assert analysis.listBatteryName == ["bad.ndax", "good"]
        assert analysis.listAllBatteryCharge == [[None], [10]]
        meta = json.loads((tmp_path / "v1.0" / "Info_Plot.json").read_text(encoding="utf-8"))
        assert meta["file_statuses"][0]["levels"][0]["voltages"][0]["status"] == "missing"
        assert meta["file_statuses"][1]["levels"][0]["voltages"][0]["status"] == "measured"

    def test_parallel_process_file_normalizes_read_failure(self, sample_xlsx):
        """read_xlsx_sheets 失败时应归一化为 BatteryAnalysisException，而非走 xlrd 回退"""
        args = (str(sample_xlsx), [500, 1000], [3.0, 4.0])
        with (
            patch(
                "battery_analysis.utils.processors.battery_analysis.read_xlsx_sheets",
                side_effect=ValueError("simulated corrupt file"),
            ),
            pytest.raises(BatteryAnalysisException, match="Failed to read Excel file"),
        ):
            BatteryAnalysis._parallel_process_file(args)
