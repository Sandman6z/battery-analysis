"""Imported metadata provenance across normalized input-project changes."""
import os
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QSignalSpy, QTest
from PyQt6.QtWidgets import QApplication, QComboBox, QLineEdit

from battery_analysis.main.business_logic.data_processor import DataProcessor
from battery_analysis.main.business_logic.validation_spec_rules import ValidationSpecRulesMixin
from battery_analysis.main.managers.analysis_runner import AnalysisRunner
from battery_analysis.main.ui_components.ui_manager import UIManager
from battery_analysis.utils.input_validator import FieldValues, InputValidator

_metadata_app = None
AUTO_FILE = "Example_LP503048_1S1P_DC(2604).ndax"
MISSING_FILE = "unconfigured_model.ndax"
FIELDS = {
    "specification_type": "comboBox_Specification_Type",
    "manufacturer": "comboBox_Manufacturer",
    "batch_date_code": "lineEdit_BatchDateCode",
}


def field_text(window, field):
    widget = getattr(window, FIELDS[field])
    return widget.text() if field == "batch_date_code" else widget.currentText()


@pytest.fixture
def metadata_ui(tmp_path, monkeypatch):
    global _metadata_app
    _metadata_app = QApplication.instance() or QApplication([])
    values = {
        "BatteryConfig/BatteryType": ["Coin Cell", "Pouch Cell"],
        "BatteryConfig/ConstructionMethod": ["Spiral Type", "Laminate Type"],
        "BatteryConfig/SpecificationTypeCoinCell": ["CR2032"],
        "BatteryConfig/SpecificationTypePouchCell": ["LP503048", "LP603040"],
        "BatteryConfig/SpecificationMethod": ["1S1P"],
        "BatteryConfig/Manufacturer": ["Example", "Other"],
        "BatteryConfig/Rules": ["LP503048/1S1P/100/100/85%|75%", "LP603040/1S1P/100/100/85%|75%"],
    }
    mw = SimpleNamespace(construction_method="", specification_type="", checker_battery_type=Mock(),
                         checker_input_xlsx=Mock(), statusBar_BatteryAnalysis=Mock())
    for name, items in {
        "BatteryType": values["BatteryConfig/BatteryType"],
        "ConstructionMethod": values["BatteryConfig/ConstructionMethod"],
        "Specification_Type": values["BatteryConfig/SpecificationTypeCoinCell"] + values["BatteryConfig/SpecificationTypePouchCell"],
        "Specification_Method": ["1S1P"], "Manufacturer": ["Example", "Other"],
        "Temperature": ["Room Temperature", "Freezer Temperature"],
        "TesterLocation": ["Lab"], "TestedBy": ["User"], "ReportedBy": ["User"],
    }.items():
        combo = QComboBox()
        combo.addItems(items)
        setattr(mw, "comboBox_" + name, combo)
    for name in ("InputPath", "BatchDateCode", "SamplesQty", "DatasheetNominalCapacity", "CalculationNominalCapacity", "RequiredUseableCapacity"):
        setattr(mw, "lineEdit_" + name, QLineEdit())
    mw.spinBox_Temperature = Mock()
    mw.config_manager = SimpleNamespace(get_config=lambda key: values.get(key, []))
    rules = ValidationSpecRulesMixin()
    rules.main_window = mw
    mw.check_batterytype = rules.check_batterytype
    mw.check_specification = rules.check_specification
    mw.comboBox_BatteryType.setCurrentText("Pouch Cell")
    rules.check_batterytype()
    mw.comboBox_BatteryType.currentIndexChanged.connect(mw.check_batterytype)
    mw.comboBox_ConstructionMethod.setCurrentText("Laminate Type")
    for project in ("A", "B"):
        (tmp_path / project / "1_ndax").mkdir(parents=True)
    mw.lineEdit_InputPath.setText(str(tmp_path / "A" / "1_ndax"))
    dp = DataProcessor(mw)
    mw.data_processor = dp
    # Mirrors the user-only events installed by UIManager.connect_widget.
    dp.connect_metadata_edit_signals()
    monkeypatch.setattr("battery_analysis.ndax.reader.recipe_levels", lambda path: [3, 6])
    return mw, dp, tmp_path


def import_file(window, processor, path, filename):
    window.lineEdit_InputPath.setText(str(path))
    processor._disconnect_specification_signals()
    processor._process_first_excel_file(filename)
    processor._reconnect_specification_signals()


def test_project_switch_clears_only_unmatched_automatic_metadata_and_derived_capacity(metadata_ui):
    mw, dp, root = metadata_ui
    import_file(mw, dp, root / "A" / "1_ndax", AUTO_FILE)
    assert field_text(mw, "specification_type") == "LP503048"
    assert mw.lineEdit_RequiredUseableCapacity.text() == "75"
    import_file(mw, dp, root / "B" / "1_ndax", MISSING_FILE)
    assert all(field_text(mw, field) == "" for field in FIELDS)
    assert mw.specification_type == ""
    assert mw.lineEdit_RequiredUseableCapacity.text() == ""
    assert mw.lineEdit_DatasheetNominalCapacity.text() == ""
    assert mw.comboBox_BatteryType.currentText() == "Pouch Cell"
    assert mw.comboBox_ConstructionMethod.currentText() == "Laminate Type"


@pytest.mark.parametrize("field", FIELDS)
def test_user_edit_then_restore_same_text_remains_manual(metadata_ui, field):
    mw, dp, root = metadata_ui
    import_file(mw, dp, root / "A" / "1_ndax", AUTO_FILE)
    widget = getattr(mw, FIELDS[field])
    original = field_text(mw, field)
    if field == "batch_date_code":
        edited = QSignalSpy(widget.textEdited)
        widget.selectAll()
        QTest.keyClicks(widget, "hand")
        widget.selectAll()
        QTest.keyClicks(widget, original)
    else:
        edited = QSignalSpy(widget.activated)
        QTest.keyClick(widget, Qt.Key.Key_Down)
        QTest.keyClick(widget, Qt.Key.Key_Up)
    assert edited
    assert field_text(mw, field) == original
    import_file(mw, dp, root / "B" / "1_ndax", MISSING_FILE)
    assert field_text(mw, field) == original
    assert all(field_text(mw, other) == "" for other in FIELDS if other != field)


def test_programmatic_updates_do_not_mark_imported_metadata_manual(metadata_ui):
    mw, dp, root = metadata_ui
    import_file(mw, dp, root / "A" / "1_ndax", AUTO_FILE)
    mw.lineEdit_BatchDateCode.setText("programmatic")
    mw.lineEdit_BatchDateCode.setText("2604")
    mw.comboBox_Manufacturer.setCurrentText("Other")
    mw.comboBox_Manufacturer.setCurrentText("Example")
    mw.comboBox_Specification_Type.setCurrentText("LP603040")
    mw.comboBox_Specification_Type.setCurrentText("LP503048")
    import_file(mw, dp, root / "B" / "1_ndax", MISSING_FILE)
    assert all(field_text(mw, field) == "" for field in FIELDS)


def test_same_normalized_input_project_rescan_does_not_clear_metadata(metadata_ui):
    mw, dp, root = metadata_ui
    import_file(mw, dp, root / "A" / "1_ndax", AUTO_FILE)
    old = {field: field_text(mw, field) for field in FIELDS}
    alternate = str(root / "A" / ".." / "A" / "1_ndax") + "/"
    import_file(mw, dp, alternate, MISSING_FILE)
    assert {field: field_text(mw, field) for field in FIELDS} == old
    if os.name == "nt":
        case_alias = str(root / "A" / "1_ndax").swapcase().replace("\\", "/")
        import_file(mw, dp, case_alias, MISSING_FILE)
        assert {field: field_text(mw, field) for field in FIELDS} == old


def test_unknown_startup_values_are_preserved_but_explicit_new_fields_still_override(metadata_ui):
    mw, dp, root = metadata_ui
    mw.comboBox_Specification_Type.setCurrentText("LP603040")
    mw.comboBox_Manufacturer.setCurrentText("Other")
    mw.lineEdit_BatchDateCode.setText("restored-hand")
    import_file(mw, dp, root / "B" / "1_ndax", MISSING_FILE)
    assert [field_text(mw, field) for field in FIELDS] == ["LP603040", "Other", "restored-hand"]
    import_file(mw, dp, root / "B" / "1_ndax", AUTO_FILE)
    assert [field_text(mw, field) for field in FIELDS] == ["LP503048", "Example", "2604"]


def test_configuration_rebuild_forgets_old_automatic_provenance(metadata_ui):
    mw, dp, root = metadata_ui
    import_file(mw, dp, root / "A" / "1_ndax", AUTO_FILE)
    UIManager(mw).init_combobox()
    mw.comboBox_BatteryType.setCurrentText("Pouch Cell")
    mw.comboBox_Specification_Type.setCurrentText("LP503048")
    mw.comboBox_Manufacturer.setCurrentText("Example")
    mw.lineEdit_BatchDateCode.setText("2604")
    import_file(mw, dp, root / "B" / "1_ndax", MISSING_FILE)
    assert [field_text(mw, field) for field in FIELDS] == ["LP503048", "Example", "2604"]


@pytest.mark.parametrize("source", ["automatic", "manual", "unknown", "same_project"])
def test_empty_input_obeys_metadata_policy_and_invalidates_sample_count(metadata_ui, source):
    mw, dp, root = metadata_ui
    if source != "unknown":
        import_file(mw, dp, root / "A" / "1_ndax", AUTO_FILE)
    else:
        mw.comboBox_Specification_Type.setCurrentText("LP503048")
        mw.comboBox_Manufacturer.setCurrentText("Example")
        mw.lineEdit_BatchDateCode.setText("2604")
    if source == "manual":
        for field in FIELDS:
            widget = getattr(mw, FIELDS[field])
            if field == "batch_date_code":
                widget.selectAll()
                QTest.keyClicks(widget, "hand")
            else:
                QTest.keyClick(widget, Qt.Key.Key_Down)
    old = {field: field_text(mw, field) for field in FIELDS}
    mw.lineEdit_DatasheetNominalCapacity.setText("123")  # No-data alone must not erase a user capacity.
    mw.lineEdit_SamplesQty.setText("9")
    project = "A" if source == "same_project" else "B"
    input_path = root / project / "1_ndax"
    mw.lineEdit_InputPath.setText(str(input_path))
    dp._disconnect_specification_signals()
    dp._handle_no_excel_files(str(input_path))
    expected = {field: "" for field in FIELDS} if source == "automatic" else old
    assert {field: field_text(mw, field) for field in FIELDS} == expected
    assert mw.comboBox_BatteryType.currentText() == "Pouch Cell"
    assert mw.comboBox_ConstructionMethod.currentText() == "Laminate Type"
    assert mw.lineEdit_SamplesQty.text() == ""
    mw.checker_input_xlsx.set_error.assert_called()
    assert "samples_qty" in InputValidator._validate_required_fields(FieldValues()).field_errors
    with pytest.raises(ValueError, match=r"No \.ndax files"):
        AnalysisRunner(mw)._preflight_recipe()
    if source != "automatic":
        assert mw.lineEdit_DatasheetNominalCapacity.text() == "123"
    else:
        assert mw.lineEdit_RequiredUseableCapacity.text() == ""
        assert mw.lineEdit_CalculationNominalCapacity.text() == ""
    # Repeated no-data refreshes reconnect exactly one specification slot.
    assert mw.comboBox_Specification_Type.receivers(mw.comboBox_Specification_Type.currentIndexChanged) == 1
    dp._disconnect_specification_signals()
    dp._handle_no_excel_files(str(input_path))
    assert mw.comboBox_Specification_Type.receivers(mw.comboBox_Specification_Type.currentIndexChanged) == 1


def test_stale_scan_does_not_parse_old_filenames_as_new_project(metadata_ui, monkeypatch):
    mw, dp, root = metadata_ui
    mw.temperature_handler = Mock()
    callbacks = []
    monkeypatch.setattr(dp, "_run_async", lambda task, done, error, *args: callbacks.append(done))
    dp.get_xlsxinfo()
    mw.lineEdit_InputPath.setText(str(root / "B" / "1_ndax"))
    dp.get_xlsxinfo()
    assert len(callbacks) == 2
    callbacks[0]([AUTO_FILE])
    assert len(callbacks) == 2


def test_metadata_edit_signals_are_connected_once(metadata_ui):
    mw, dp, _ = metadata_ui
    dp.connect_metadata_edit_signals()
    dp.connect_metadata_edit_signals()
    assert mw.lineEdit_BatchDateCode.receivers(mw.lineEdit_BatchDateCode.textEdited) == 1
    assert mw.comboBox_Specification_Type.receivers(mw.comboBox_Specification_Type.activated) == 1
    assert mw.comboBox_Manufacturer.receivers(mw.comboBox_Manufacturer.activated) == 1


def test_main_ui_connects_user_metadata_events():
    window = Mock()
    UIManager(window).connect_widget()
    window.data_processor.connect_metadata_edit_signals.assert_called_once_with()
