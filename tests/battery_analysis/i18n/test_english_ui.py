"""English UI regression checks, with particular attention to modal dialogs."""

import ast
from pathlib import Path
from string import Formatter
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pandas as pd
import pytest
from PyQt6 import QtCore as QC
from PyQt6 import QtWidgets as QW

from battery_analysis.i18n import LOCALEDIR, get_current_locale, set_locale
from battery_analysis.i18n.language_manager import LanguageManager
from battery_analysis.i18n.translator import SimplePOTranslator
from battery_analysis.main.ui_components.dialog_manager import DialogManager
from battery_analysis.main.ui_components.preferences_dialog import PreferencesDialog
from battery_analysis.main.utils.signal_connector import SignalConnector
from battery_analysis.utils.readers.xlsx_reader import read_xlsx_sheets

ROOT = Path(__file__).resolve().parents[3]


def has_chinese(text):
    return any("\u4e00" <= char <= "\u9fff" for char in text)


@pytest.fixture(scope="module")
def qapp():
    return QW.QApplication.instance() or QW.QApplication([])


@pytest.fixture(autouse=True)
def english_locale(qapp):
    previous = get_current_locale()
    native_dialogs_disabled = qapp.testAttribute(QC.Qt.ApplicationAttribute.AA_DontUseNativeDialogs)
    assert set_locale("en")
    yield
    assert set_locale(previous)
    qapp.setAttribute(QC.Qt.ApplicationAttribute.AA_DontUseNativeDialogs, native_dialogs_disabled)


def test_no_hardcoded_chinese_in_ui_calls():
    presentation_calls = {
        "setText", "setWindowTitle", "setInformativeText", "setDetailedText",
        "setPlaceholderText", "setToolTip", "setTitle", "showMessage",
        "QLabel", "QPushButton", "QRadioButton", "QCheckBox", "QGroupBox",
    }
    violations = []
    for path in (ROOT / "src" / "battery_analysis").rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8-sig"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            function = ast.unparse(node.func)
            if not (
                function.rsplit(".", 1)[-1] in presentation_calls
                or "QMessageBox." in function
                or "QInputDialog." in function
                or "QFileDialog." in function
                or function == "_"
            ):
                continue
            for child in ast.walk(node):
                if isinstance(child, ast.Constant) and isinstance(child.value, str):
                    if has_chinese(child.value):
                        violations.append(f"{path.relative_to(ROOT)}:{child.lineno}: {child.value}")
    assert not violations, "\n".join(violations)


@pytest.mark.parametrize("locale", ["en", "zh_CN"])
def test_dialog_catalogs_cover_static_templates_and_preserve_placeholders(locale):
    translator = SimplePOTranslator()
    assert translator.load_locale(locale, LOCALEDIR)
    for relative in (
        "main/managers/path_manager.py",
        "main/ui_components/dialog_manager.py",
        "main/ui_components/preferences_dialog.py",
        "main/utils/signal_connector.py",
    ):
        path = ROOT / "src" / "battery_analysis" / relative
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
                continue
            if node.func.id != "_":
                continue
            assert isinstance(node.args[0], ast.Constant), f"Dynamic gettext key: {relative}:{node.lineno}"
            source = node.args[0].value
            translated = translator.translations[source]
            assert translated
            source_fields = {field for _, field, _, _ in Formatter().parse(source) if field}
            translated_fields = {field for _, field, _, _ in Formatter().parse(translated) if field}
            assert source_fields == translated_fields, source
            if locale == "en":
                assert translated == source
                assert not has_chinese(translated)


def test_exit_confirmation_is_english():
    with patch.object(QW.QMessageBox, "question", return_value=QW.QMessageBox.StandardButton.No) as question:
        DialogManager().handle_exit()
    assert question.call_args.args[1:3] == (
        "Confirm Exit", "Are you sure you want to exit the application?",
    )
    assert question.call_args.args[-1] == QW.QMessageBox.StandardButton.No


def test_analysis_completion_popup_is_english():
    controller = SimpleNamespace(completed_report_path="reports/report.docx", completed_result_dir="reports/20241019_v1.0")
    window = SimpleNamespace(pushButton_Run=Mock(), statusBar_BatteryAnalysis=Mock(), _get_controller=lambda name: controller)
    connector = SignalConnector(window)
    captured = {}

    def inspect_dialog(dialog):
        captured["title"] = dialog.windowTitle()
        captured["text"] = dialog.text()
        captured["buttons"] = [button.text() for button in dialog.buttons()]
        dialog.deleteLater()
        return QW.QMessageBox.StandardButton.Ok

    with patch.object(QW.QMessageBox, "exec", inspect_dialog):
        connector._on_status_changed(False, 0, "success\nOptional profile was not supplied")
    assert captured["title"] == "Analysis Completed"
    assert "Battery analysis completed successfully!" in captured["text"]
    assert "Warning: Optional profile was not supplied" in captured["text"]
    assert "Open Report" in captured["buttons"]
    assert "Open Output Folder" in captured["buttons"]
    assert any(button.replace("&", "") == "OK" for button in captured["buttons"])
    assert not has_chinese(str(captured))


@pytest.mark.parametrize("state, title", [
    (1, "Battery Analysis Error"),
    (2, "Report Generation Error"),
    (3, "Date Mismatch Error"),
])
def test_analysis_error_popups_are_english(state, title):
    window = SimpleNamespace(pushButton_Run=Mock(), statusBar_BatteryAnalysis=Mock())
    with patch.object(QW.QMessageBox, "critical") as critical:
        SignalConnector(window)._on_status_changed(False, state, "permission denied writing output")
    assert critical.call_args.args[1] == title
    assert "Suggested steps:" in critical.call_args.args[2]
    assert not has_chinese(critical.call_args.args[2])


@pytest.mark.parametrize("sheets, expected", [
    ({"Cycle": pd.DataFrame()}, "XLSX requires Cycle, Step and Record worksheets; found 1"),
    ({name: pd.DataFrame() for name in ("Cycle", "Step", "Other")}, "Record worksheet not found"),
])
def test_xlsx_errors_shown_to_users_are_english(sheets, expected):
    with patch("battery_analysis.utils.readers.xlsx_reader.pd.read_excel", return_value=sheets):
        with pytest.raises(ValueError) as error:
            read_xlsx_sheets("broken.xlsx")
    assert expected in str(error.value)
    assert not has_chinese(str(error.value))


@pytest.mark.parametrize("locale, suffix, content, expected", [
    ("en", ".json", "{}", "Missing required keys: battery, test"),
    ("en", ".ini", "[Other]\n", "Missing required sections: BatteryConfig, TestConfig, PltConfig"),
    ("zh_CN", ".json", "{}", "缺少必需配置项：battery, test"),
])
def test_preferences_validation_formats_translatable_messages(qapp, tmp_path, locale, suffix, content, expected):
    assert set_locale(locale)
    manager = Mock()
    manager.get_installed_locales.return_value = {"en": "English", "zh_CN": "中文(简体)"}
    config = tmp_path / f"config{suffix}"
    config.write_text(content, encoding="utf-8")
    with (
        patch("battery_analysis.main.ui_components.preferences_dialog.get_language_manager", return_value=manager),
        patch.object(PreferencesDialog, "_load_settings"),
    ):
        dialog = PreferencesDialog()
    try:
        dialog.config_path_lineedit.setText(str(config))
        dialog._validate_config_file()
        assert dialog.config_status_label.text() == expected
    finally:
        dialog.close()
        dialog.deleteLater()


def test_language_manager_uses_po_catalogs_and_english_file_dialogs(qapp):
    settings = Mock()
    settings.value.return_value = "en"
    with patch("battery_analysis.i18n.language_manager.QSettings", return_value=settings):
        manager = LanguageManager()
    assert manager._has_translation_file("zh_CN")
    assert manager.get_installed_locales() == {"en": "English", "zh_CN": "中文(简体)"}
    assert qapp.testAttribute(QC.Qt.ApplicationAttribute.AA_DontUseNativeDialogs)
    assert manager.set_locale("zh_CN")
    assert not qapp.testAttribute(QC.Qt.ApplicationAttribute.AA_DontUseNativeDialogs)
    assert manager.set_locale("en")
    assert qapp.testAttribute(QC.Qt.ApplicationAttribute.AA_DontUseNativeDialogs)
