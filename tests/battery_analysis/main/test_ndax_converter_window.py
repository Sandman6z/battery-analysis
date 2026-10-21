"""Independent converter entry point, state isolation and worker lifecycle."""

import ast
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from PyQt6 import QtCore as QC
from PyQt6 import QtWidgets as QW

from battery_analysis.i18n import LOCALEDIR, get_current_locale, set_locale
from battery_analysis.i18n.translator import SimplePOTranslator
from battery_analysis.main.main_window import Main
from battery_analysis.main.ndax_converter_window import NdaxConverterWindow
from battery_analysis.main.tabs.battery_tab import BatteryAnalysisTab
from battery_analysis.main.ui_components.menu_manager import MenuManager
from battery_analysis.ndax.worker import ConvertWorker


@pytest.fixture(scope="module", autouse=True)
def qapp():
    app = QW.QApplication.instance() or QW.QApplication([])
    yield app


@pytest.fixture(autouse=True)
def english_locale():
    previous = get_current_locale()
    assert set_locale("en")
    yield
    assert set_locale(previous)


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
    main_window.menu_manager.setup_menu_shortcuts()
    main_window.menu_manager.connect_menu_actions()
    main_window.actionNdaxConverter.trigger()
    converter = main_window._ndax_converter_window
    assert isinstance(converter, NdaxConverterWindow)
    assert main_window.actionNdaxConverter.text() == "NDAX Converter"
    assert main_window.actionNdaxConverter.toolTip() == "NDAX → XLSX Batch Conversion"
    assert converter.windowTitle() == "NDAX Converter"
    assert converter.btn_select.text() == "📁 Select Folder"
    assert converter.btn_start.text() == "▶ Start Conversion"
    assert converter.table.horizontalHeaderItem(0).text() == "File Name"
    assert converter.table.horizontalHeaderItem(1).text() == "Status"
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
    assert converter.btn_start.text() == "■ Cancel"
    worker.file_status.emit(0, "Success")
    status = converter.table.item(0, converter.COL_STATUS)
    assert status.text() == "Success"
    assert status.foreground().color() == QC.Qt.GlobalColor.darkGreen

    with patch.object(QW.QMessageBox, "warning") as warning:
        assert not converter.close()
        assert not main_window.close()
        assert warning.call_count == 2
        assert warning.call_args.args[1:] == (
            "Conversion in Progress",
            "Please cancel the conversion and wait for the current task to finish before closing this window.",
        )
    assert converter.isVisible()
    assert main_window.isVisible()

    converter.btn_start.click()
    assert worker.cancelled
    assert converter.btn_start.text() == "Cancelling..."
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
        patch.object(QW.QMessageBox, "question", return_value=answer) as question,
        patch("battery_analysis.main.ndax_converter_window.ConvertWorker", FakeWorker),
    ):
        converter._start_convert()
    assert existing.read_bytes() == b"original data"
    assert question.call_args.args[1] == "Confirm Overwrite"
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
    assert "No NDAX files found" in converter.log_area.toPlainText()


@pytest.mark.parametrize("failed", [False, True])
def test_completion_messages_are_english(converter, failed):
    result = {"success": ["good.ndax"], "skipped": [], "failed": []}
    if failed:
        result["failed"].append(("bad.ndax", "invalid data"))
    method = "warning" if failed else "information"
    with patch.object(QW.QMessageBox, method) as message:
        converter._on_finished(result)
    assert message.call_args.args[1] == "Conversion Complete"
    assert "✔ Success: 1\n⏭ Skipped: 0" in message.call_args.args[2]
    assert converter.lbl_summary.text() == f"Success: 1  Skipped: 0  Failed: {int(failed)}"
    assert "Conversion complete: success 1, skipped 0" in converter.log_area.toPlainText()


def test_converter_chinese_locale(qapp, tmp_path):
    assert set_locale("zh_CN")
    window = NdaxConverterWindow()
    try:
        assert window.windowTitle() == "NDAX 转换器"
        assert window.btn_start.text() == "▶ 开始转换"
        window.table.setRowCount(1)
        window.table.setItem(0, window.COL_STATUS, QW.QTableWidgetItem())
        worker = ConvertWorker([tmp_path / "existing.ndax"], tmp_path)
        (tmp_path / "existing.xlsx").touch()
        worker.file_status.connect(window._on_file_status)
        worker.run()
        status = window.table.item(0, window.COL_STATUS)
        assert status.text() == "已跳过"
        assert status.foreground().color() == QC.Qt.GlobalColor.gray
    finally:
        window.close()
        window.deleteLater()


@pytest.mark.parametrize("locale", ["en", "zh_CN"])
def test_converter_translation_catalogs(locale):
    translator = SimplePOTranslator()
    assert translator.load_locale(locale, LOCALEDIR)
    root = Path(__file__).resolve().parents[3] / "src" / "battery_analysis"
    for relative in ("main/ndax_converter_window.py", "ndax/worker.py"):
        tree = ast.parse((root / relative).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
                continue
            if node.func.id != "_":
                continue
            message = node.args[0].value
            assert not any("\u4e00" <= char <= "\u9fff" for char in message), message
            translated = translator.translations[message]
            assert translated
            if locale == "en":
                assert translated == message
    assert translator.gettext("NDAX Converter") == (
        "NDAX Converter" if locale == "en" else "NDAX 转换器"
    )


def test_worker_status_and_logs_are_english(tmp_path):
    files = [tmp_path / name for name in ("existing.ndax", "good.ndax", "bad.ndax")]
    (tmp_path / "existing.xlsx").touch()
    worker = ConvertWorker(files, tmp_path)
    statuses, logs, results = [], [], []
    worker.file_status.connect(lambda row, status: statuses.append((row, status)))
    worker.log.connect(logs.append)
    worker.finished_signal.connect(results.append)

    def convert(source, output):
        if source.name == "bad.ndax":
            raise ValueError("invalid data")
        return str(output)

    with (
        patch("battery_analysis.ndax.worker.ProcessPoolExecutor", ThreadPoolExecutor),
        patch("battery_analysis.ndax.worker.convert_one", side_effect=convert),
    ):
        worker.run()

    assert (0, "Skipped") in statuses
    assert (1, "Waiting...") in statuses
    assert (1, "Converting...") in statuses
    assert (1, "Success") in statuses
    assert (2, "Failed") in statuses
    assert results == [{
        "success": ["good.ndax"],
        "skipped": ["existing.ndax"],
        "failed": [("bad.ndax", "invalid data")],
    }]
    assert all(not any("\u4e00" <= c <= "\u9fff" for c in log) for log in logs)

    logs.clear()
    worker.cancel()
    worker.run()
    assert logs == ["⚠ Conversion cancelled"]
