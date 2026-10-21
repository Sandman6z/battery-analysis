"""Completion actions refer to delivered artifacts, not mutable UI fields."""
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from battery_analysis.main.utils.signal_connector import SignalConnector


@pytest.mark.parametrize("action", ["report", "folder"])
def test_success_dialog_shows_and_opens_delivered_paths(monkeypatch, action):
    window = Mock()
    window._get_controller.return_value = SimpleNamespace(
        completed_report_path="A/results/Example_TD20241019_v1.0.docx",
        completed_result_dir="A/results/20241019_v1.0",
    )
    window.lineEdit_OutputPath.text.return_value = "B/results"
    window.lineEdit_Version.text.return_value = "2.0"
    box = Mock()
    report, folder, ok = Mock(), Mock(), Mock()
    box.addButton.side_effect = [report, folder, ok]
    box.clickedButton.return_value = report if action == "report" else folder
    monkeypatch.setattr("battery_analysis.main.utils.signal_connector.QW.QMessageBox", Mock(return_value=box))
    SignalConnector(window)._on_status_changed(False, 0, "status:success")
    text = box.setText.call_args.args[0]
    assert "A/results/Example_TD20241019_v1.0.docx" in text
    assert "A/results/20241019_v1.0" in text
    assert "B/results" not in text
    if action == "report":
        window.report_manager.open_report.assert_called_once_with(
            report_path="A/results/Example_TD20241019_v1.0.docx"
        )
    else:
        window.report_manager.open_report_path.assert_called_once_with(
            output_path="A/results/20241019_v1.0"
        )


def test_success_count_uses_completed_context_only_on_success():
    from battery_analysis.main.controllers.main_controller import MainController

    controller = MainController()
    controller.completed_context = {
        "project_path": "A", "output_path": "A/results", "checksum": "a", "version": "1.0"
    }
    window = Mock()
    window._get_controller.return_value = controller
    connector = SignalConnector(window)
    connector._connect_main_controller_signals()
    controller.analysis_completed.emit()
    window.version_manager.set_version.assert_not_called()
    controller.analysis_succeeded.emit()
    window.version_manager.set_version.assert_called_once_with(**controller.completed_context)


def test_automatic_chart_signal_uses_completed_result_not_changed_ui():
    from battery_analysis.main.controllers.main_controller import MainController

    controller = MainController()
    controller.completed_result_dir = "A/results/20241019_v1.0"
    window = Mock()
    window.lineEdit_TestProfile.text.return_value = "B/changed-profile.xml"
    window._get_controller.return_value = controller
    connector = SignalConnector(window)
    connector._connect_main_controller_signals()
    controller.start_visualizer.emit()
    window.visualization_manager.run_visualizer.assert_called_once_with(
        data_path="A/results/20241019_v1.0"
    )
