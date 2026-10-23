from unittest.mock import Mock, patch

import pytest

from battery_analysis.analysis.battery_analysis import BatteryAnalysis
from battery_analysis.utils.exceptions import BatteryAnalysisException


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

    @pytest.mark.parametrize("missing_current,missing_voltage,should_confirm", [
        (15, 1.8, False),
        (150, 1.8, False),
        (15, 2.25, False),
        (150, 2.25, True),
    ])
    def test_only_judgment_slot_missing_requires_confirmation(self, tmp_path, monkeypatch, missing_current, missing_voltage, should_confirm):
        import json

        info = [""] * 19
        info[1], info[2], info[3], info[9], info[17] = "Spiral Type", "CP5022121", "1S1P", "4000", "3400"
        info[14], info[15], info[16], info[7] = [150, 15], [2.25, 1.8], "1.0", "Room"
        charges = [3500] * 4
        charges[info[14].index(missing_current) * 2 + info[15].index(missing_voltage)] = None
        result = ("good", charges, [[2], [3]], [[2.25], [2.25]], [[3500], [3500]],
                  ["2025-06-10 10:01:49", "2025-06-10 11:01:49"], [])
        monkeypatch.setattr(BatteryAnalysis, "_parallel_process_file", staticmethod(lambda args: result))
        decision = Mock(return_value=True)
        analysis = BatteryAnalysis(str(tmp_path), str(tmp_path), info,
                                   input_files=[str(tmp_path / "a.ndax")], decision_callback=decision)
        assert analysis.UBA_GetErrorLog() == ""
        assert analysis.listAllBatteryCharge == [charges]
        assert decision.called is should_confirm
        assert bool(analysis.warning_summary) is not should_confirm
        metadata = json.loads((tmp_path / "v1.0" / "Info_Plot.json").read_text(encoding="utf-8"))
        assert metadata["anomalies"] == [{"file": "a.ndax", "type": "missing_pulse", "current": missing_current, "voltage": missing_voltage}]
        audit = metadata["analysis_audit"]
        entry = audit["classification"][0]
        assert entry["requires_confirmation"] is should_confirm
        assert entry["category"] == ("required_judgment_missing" if should_confirm else "non_judgment_cutoff_missing")
        assert audit["confirmation"] == ("allowed" if should_confirm else "not_required")
        missing_slot = next(s for s in audit["slot_sample_counts"] if s["current_ma"] == missing_current and s["voltage"] == missing_voltage)
        assert missing_slot["valid"] == 0 and missing_slot["expected"] == 1

    @pytest.mark.parametrize("spec,construction,qnom,required,currents,voltages,expected", [
        ("CR2450", "", "600", "380", [30, 26, 15, 6], [1.8], [(30, 2.25)]),
        ("CP583083", "Spiral Type", "4000", "3000", [500, 250, 100, 50, 25], [2.25], [(500, 2.5), (100, 2.5)]),
        ("CP5022121", "", "4000", "3400", [150, 100], [1.8], [(150, 2.25)]),
    ])
    def test_absent_judgment_levels_require_confirmation(self, tmp_path, monkeypatch, spec, construction, qnom, required, currents, voltages, expected):
        info = [""] * 19
        info[1], info[2], info[9], info[17] = construction, spec, qnom, required
        info[14], info[15], info[16], info[7] = currents, voltages, "1.0", "Room"
        result = ("good", [3500] * (len(currents) * len(voltages)), [[] for _ in currents],
                  [[] for _ in currents], [[] for _ in currents], ["2025-06-10 10:01:49", "2025-06-10 11:01:49"], [])
        monkeypatch.setattr(BatteryAnalysis, "_parallel_process_file", staticmethod(lambda args: result))
        decision = Mock(return_value=True)
        analysis = BatteryAnalysis(str(tmp_path), str(tmp_path), info,
                                   input_files=[str(tmp_path / "a.ndax")], decision_callback=decision)
        assert analysis.UBA_GetErrorLog() == ""
        assert [(a["current"], a["voltage"]) for a in decision.call_args.args[0]] == expected

    def test_all_bad_files_cannot_be_released_without_timestamp(self, tmp_path, monkeypatch):
        info = [""] * 19
        info[14], info[15], info[16], info[7] = [30], [2.25], "1.0", "Room"
        monkeypatch.setattr(BatteryAnalysis, "_parallel_process_file", Mock(side_effect=ValueError("No measured Timestamp")))
        decision = Mock(return_value=True)
        analysis = BatteryAnalysis(str(tmp_path), str(tmp_path), info,
                                   input_files=[str(tmp_path / "a.ndax")], decision_callback=decision)
        assert "No measured Timestamp" in analysis.UBA_GetErrorLog()
        decision.assert_not_called()
        assert not (tmp_path / "v1.0" / "Info_Image.csv").exists()

    def test_judgment_missing_can_stop_without_writing(self, tmp_path, monkeypatch):
        from battery_analysis.main.workers.task_runner import TaskCancelled

        info = [""] * 19
        info[2], info[9], info[17] = "CR2450", "600", "380"
        info[14], info[15], info[16], info[7] = [30], [2.25], "1.0", "Room"
        result = ("good", [None], [[]], [[]], [[]], ["2025-06-10 10:01:49", "2025-06-10 11:01:49"], [])
        monkeypatch.setattr(BatteryAnalysis, "_parallel_process_file", staticmethod(lambda args: result))
        with pytest.raises(TaskCancelled):
            BatteryAnalysis(str(tmp_path), str(tmp_path), info, input_files=[str(tmp_path / "a.ndax")], decision_callback=lambda issues: False)
        assert not (tmp_path / "v1.0" / "Info_Image.csv").exists()

    def test_nonblocking_anomalies_and_capacity_basis_are_audited(self, tmp_path, monkeypatch, caplog):
        import json

        info = [""] * 19
        info[0], info[2], info[8], info[9], info[17] = "Coin Cell", "CR2450", "600", "550", "380"
        info[14], info[15], info[16], info[7] = [30], [2.25], "1.0", "Room"
        result = ("good", [400], [[2]], [[2.25]], [[400]],
                  ["2025-06-10 10:01:49", "2025-06-11 11:01:49"],
                  [{"type": "current_deviation", "current": 30, "median_ma": 29}])
        monkeypatch.setattr(BatteryAnalysis, "_parallel_process_file", staticmethod(lambda args: result))
        decision = Mock(return_value=True)
        analysis = BatteryAnalysis(str(tmp_path), str(tmp_path), info,
                                   input_files=[str(tmp_path / "a.ndax")], decision_callback=decision)
        assert analysis.UBA_GetErrorLog() == ""
        decision.assert_not_called()
        audit = json.loads((tmp_path / "v1.0" / "Info_Plot.json").read_text(encoding="utf-8"))["analysis_audit"]
        assert {a["category"] for a in audit["classification"]} == {"cross_day", "current_deviation", "capacity_basis_difference"}
        assert all(not a["requires_confirmation"] for a in audit["classification"])
        assert audit["input_context"]["datasheet_nominal_capacity"] == "600"
        assert audit["input_context"]["calculation_nominal_capacity"] == "550"
        for category in ("cross_day", "current_deviation", "capacity_basis_difference"):
            assert category in caplog.text

    def test_parallel_process_file_normalizes_read_failure(self, sample_xlsx):
        """read_xlsx_sheets 失败时应归一化为 BatteryAnalysisException，而非走 xlrd 回退"""
        args = (str(sample_xlsx), [500, 1000], [3.0, 4.0])
        with (
            patch(
                "battery_analysis.analysis.battery_analysis.read_xlsx_sheets",
                side_effect=ValueError("simulated corrupt file"),
            ),
            pytest.raises(BatteryAnalysisException, match="Failed to read Excel file"),
        ):
            BatteryAnalysis._parallel_process_file(args)
