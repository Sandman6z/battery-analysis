"""Explicit report date is shared by coordinator, Word and Excel writers."""
from pathlib import Path

from battery_analysis.domain.test_info import TestInfo as ReportTestInfo
from battery_analysis.reports.excel_report_writer import ExcelReportWriter
from battery_analysis.reports.word_report_writer import WordReportWriter
from battery_analysis.utils.report_coordinator import ReportCoordinator


def test_explicit_date_reaches_writers_with_custom_result_directory(tmp_path, monkeypatch):
    info = ReportTestInfo(battery_type="Coin Cell", specification_type="CR2032",
                          manufacturer="Example", batch_date_code="20231231", version="1.0", datasheet_nominal_capacity="100",
                          current_levels=[3], voltage_levels=[2.5], temperature_value="Room Temperature").to_list()
    battery = [[[100]], ["cell"], ["2024-10-19 23:55:00", "2024-10-20 00:01:00"], "20241019", ""]
    custom_dir = tmp_path / "custom"
    captured = []
    for cls in (ExcelReportWriter, WordReportWriter):
        monkeypatch.setattr(cls, "write", lambda self, *args: captured.append(self.strReportWordPath))
    from battery_analysis.reports.csv_writer import CsvWriter
    monkeypatch.setattr(CsvWriter, "write", lambda *args: None)
    monkeypatch.setattr("battery_analysis.utils.report_coordinator.plot_writer.draw_boxplot_and_curves", lambda *args: None)
    coordinator = ReportCoordinator(str(tmp_path), info, battery, result_dir=str(custom_dir), test_date="20241019")
    coordinator.write()
    expected = str(tmp_path / "Example_CR2032_DC20231231_TD20241019_v1.0.docx")
    assert coordinator.strReportWordPath == expected
    assert captured == [expected, expected]
    assert Path(expected).name.count("20231231") == 1
