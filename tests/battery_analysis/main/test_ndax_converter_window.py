"""Independent converter entry point, state isolation and worker lifecycle."""

from unittest.mock import Mock, patch

import pytest
from PyQt6 import QtCore as QC
from PyQt6 import QtWidgets as QW

from battery_analysis.main.main_window import Main
from battery_analysis.main.ndax_converter_window import NdaxConverterWindow
from battery_analysis.main.tabs.battery_tab import BatteryAnalysisTab
from battery_analysis.main.ui_components.menu_manager import MenuManager


@pytest.fixture(scope="module", autouse=True)
def qapp():
    app = QW.QApplication.instance() or QW.QApplication([])
    yield app


@pytest.fixture
def main_window():
    with patch.object(Main, "_deferred_init", lambda self: None):
        window = Main()
    yield window
    if window._ndax_converter_window is not None:
        window._ndax_converter_window.worker = None
    window.close()
    window.deleteLater()


@pytest.fixture
def converter(main_window):
    main_window.show_ndax_converter()
    return main_window._ndax_converter_window


class FakeWorker(QC.QObject):
    progress = QC.pyqtSignal(int, int)
    file_status = QC.pyqtSignal(int, str)
    log = QC.pyqtSignal(str)
    finished_signal = QC.pyqtSignal(dict)

    def __init__(self, files, out_dir, force=False):
        super().__init__()
        self.files = files
        self.out_dir = out_dir
        self.force = force
        self.running = False
        self.cancelled = False

    def start(self):
        self.running = True

    def isRunning(self):
        return self.running

    def cancel(self):
        self.cancelled = True


def select_folder(converter, tmp_path):
    source = tmp_path / "1_ndax"
    source.mkdir()
    (source / "sample.ndax").touch()
    with patch.object(QW.QFileDialog, "getExistingDirectory", return_value=str(source)):
        converter._select_folder()
    return source


def test_main_opens_analysis_without_converter(main_window):
    assert isinstance(main_window.centralWidget(), BatteryAnalysisTab)
    assert main_window.centralwidget is main_window.centralWidget()
    assert main_window._ndax_converter_window is None
    assert not main_window.findChildren(NdaxConverterWindow)


def test_tools_menu_entry_opens_single_reusable_window(main_window):
    tools_menu = next(
        action.menu()
        for action in main_window.menuBar().actions()
        if action.menu() and main_window.actionBatteryChartViewer in action.menu().actions()
    )
    actions = tools_menu.actions()
    assert actions[actions.index(main_window.actionBatteryChartViewer) + 1] is main_window.actionNdaxConverter

    for attr in (
        "dialog_manager", "help_manager", "visualization_manager",
        "calculate_battery_command", "analyze_data_command", "generate_report_command",
        "batch_processing_command", "export_report_command",
    ):
        setattr(main_window, attr, Mock())
    main_window.menu_manager = MenuManager(main_window)
    main_window.menu_manager.connect_menu_actions()
    main_window.actionNdaxConverter.trigger()
    converter = main_window._ndax_converter_window
    assert isinstance(converter, NdaxConverterWindow)
    assert converter.isWindow()
    assert converter.isVisible()
    assert converter.parent() is main_window

    converter.log_area.setPlainText("keep state")
    main_window.actionNdaxConverter.trigger()
    assert main_window._ndax_converter_window is converter
    converter.close()
    main_window.actionNdaxConverter.trigger()
    assert main_window._ndax_converter_window is converter
    assert converter.isVisible()
    assert converter.log_area.toPlainText() == "keep state"


def test_select_and_finish_do_not_change_analysis(converter, main_window, tmp_path):
    main_window.lineEdit_InputPath.setText("original input")
    main_window.lineEdit_OutputPath.setText("original output")
    main_window.lineEdit_TestProfile.setText("original profile")
    main_window.path_manager = Mock()
    version_changed = Mock()
    main_window.sigSetVersion.connect(version_changed)
    profile_dir = tmp_path / "4_test profile"
    profile_dir.mkdir()
    (profile_dir / "profile.xml").touch()
    output = tmp_path / "2_xlsx"
    output.mkdir()
    (output / "sample.xlsx").touch()

    source = select_folder(converter, tmp_path)
    assert converter.ndax_files == [source / "sample.ndax"]
    assert converter.out_dir == output
    assert converter.table.item(0, converter.COL_STATUS).text()
    assert converter.btn_start.isEnabled()
    converter._on_finished({"success": [], "skipped": ["sample.ndax"], "failed": []})

    assert main_window.lineEdit_InputPath.text() == "original input"
    assert main_window.lineEdit_OutputPath.text() == "original output"
    assert main_window.lineEdit_TestProfile.text() == "original profile"
    assert main_window.path_manager.mock_calls == []
    version_changed.assert_not_called()


def test_conversion_cancel_and_safe_close(converter, main_window, tmp_path):
    source = select_folder(converter, tmp_path)
    with patch("battery_analysis.main.ndax_converter_window.ConvertWorker", FakeWorker):
        converter.btn_start.click()
    worker = converter.worker
    assert worker.files == [source / "sample.ndax"]
    assert worker.out_dir == tmp_path / "2_xlsx"
    assert not worker.force
    assert not converter.btn_select.isEnabled()
    assert converter.btn_start.isEnabled()
    worker.progress.emit(1, 1)
    assert converter.progress_bar.value() == 1

    with patch.object(QW.QMessageBox, "warning") as warning:
        assert not converter.close()
        assert not main_window.close()
        assert warning.call_count == 2
    assert converter.isVisible()
    assert main_window.isVisible()

    converter.btn_start.click()
    assert worker.cancelled
    assert not converter.btn_start.isEnabled()
    worker.running = False
    worker.finished_signal.emit({"success": [], "skipped": [], "failed": []})
    assert converter.btn_select.isEnabled()
    assert converter.btn_start.isEnabled()
    assert main_window.close()
    assert not converter.isVisible()


@pytest.mark.parametrize("overwrite", [False, True])
def test_overwrite_confirmation(converter, tmp_path, overwrite):
    select_folder(converter, tmp_path)
    converter.out_dir.mkdir()
    existing = converter.out_dir / "sample.xlsx"
    existing.write_bytes(b"original data")
    answer = QW.QMessageBox.StandardButton.Yes if overwrite else QW.QMessageBox.StandardButton.No
    with (
        patch.object(QW.QMessageBox, "question", return_value=answer),
        patch("battery_analysis.main.ndax_converter_window.ConvertWorker", FakeWorker),
    ):
        converter._start_convert()
    assert existing.read_bytes() == b"original data"
    if overwrite:
        assert converter.worker.force
        converter.worker.running = False
    else:
        assert converter.worker is None


def test_empty_folder_and_cancelled_selection(converter, tmp_path):
    with patch.object(QW.QFileDialog, "getExistingDirectory", return_value=""):
        converter._select_folder()
    assert converter.input_dir is None
    with patch.object(QW.QFileDialog, "getExistingDirectory", return_value=str(tmp_path)):
        converter._select_folder()
    assert converter.ndax_files == []
    assert not converter.btn_start.isEnabled()
