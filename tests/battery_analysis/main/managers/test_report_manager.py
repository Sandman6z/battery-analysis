from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from battery_analysis.main.managers.report_manager import ReportManager


class TestReportManager:
    def setup_method(self):
        self.main_window = Mock()
        self.manager = ReportManager(self.main_window)

    def test_init(self):
        assert self.manager.main_window == self.main_window


@pytest.mark.parametrize("other_version", ["10.0", "1.01", "1.0.1"])
def test_open_report_selects_exact_version_in_requested_root(tmp_path, monkeypatch, other_version):
    output = tmp_path / "A"
    output.mkdir()
    (output / f"other_v{other_version}.docx").write_text("other")
    unrelated = tmp_path / "B"
    unrelated.mkdir()
    (unrelated / "other_v1.0.docx").write_text("B")
    report = output / "expected_v1.0.docx"
    report.write_text("A")
    manager = ReportManager(SimpleNamespace(
        lineEdit_OutputPath=SimpleNamespace(text=lambda: str(output)),
        lineEdit_Version=SimpleNamespace(text=lambda: "1.0"),
    ))
    opened = Mock()
    monkeypatch.setattr("os.startfile", opened)
    manager.open_report()
    opened.assert_called_once_with(str(report))


def test_missing_version_does_not_open_unrelated_report(tmp_path, monkeypatch):
    (tmp_path / "other_v1.01.docx").write_text("other")
    manager = ReportManager(SimpleNamespace(
        lineEdit_OutputPath=SimpleNamespace(text=lambda: str(tmp_path)),
        lineEdit_Version=SimpleNamespace(text=lambda: "1.0"),
    ))
    monkeypatch.setattr(manager, "_info", Mock())
    opened = Mock()
    monkeypatch.setattr("os.startfile", opened)
    manager.open_report()
    opened.assert_not_called()


def test_completion_opens_delivered_paths_after_ui_changes(tmp_path, monkeypatch):
    report = tmp_path / "actual_v1.0.docx"
    report.write_text("report")
    manager = ReportManager(SimpleNamespace(
        lineEdit_OutputPath=SimpleNamespace(text=lambda: "different"),
        lineEdit_Version=SimpleNamespace(text=lambda: "2.0"),
    ))
    opened = Mock()
    monkeypatch.setattr("os.startfile", opened)
    manager.open_report(report_path=str(report))
    manager.open_report_path(output_path=str(tmp_path))
    assert opened.call_args_list[0].args == (str(report),)
    assert opened.call_args_list[1].args == (str(tmp_path),)


def test_matching_report_in_sibling_project_is_not_opened(tmp_path, monkeypatch):
    output = tmp_path / "A"
    output.mkdir()
    other = tmp_path / "B"
    other.mkdir()
    (other / "expected_v1.0.docx").write_text("B")
    manager = ReportManager(SimpleNamespace(
        lineEdit_OutputPath=SimpleNamespace(text=lambda: str(output)),
        lineEdit_Version=SimpleNamespace(text=lambda: "1.0"),
    ))
    monkeypatch.setattr(manager, "_info", Mock())
    opened = Mock()
    monkeypatch.setattr("os.startfile", opened)
    manager.open_report()
    opened.assert_not_called()
