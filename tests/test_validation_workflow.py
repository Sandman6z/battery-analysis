"""Behavioral checks across pure validation, live feedback and the Run entry."""

from dataclasses import replace
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from battery_analysis.main.business_logic.validation_manager import ValidationManager
from battery_analysis.main.managers.analysis_runner import AnalysisRunner
from battery_analysis.utils.input_validator import FieldValues, InputValidator


@pytest.fixture
def valid_values(tmp_path):
    return FieldValues(
        battery_type="Coin Cell", specification_type="CR2450", specification_method="1S1P",
        manufacturer="Example", batch_date_code="2510", samples_qty="2",
        temperature="Room Temperature", datasheet_nominal_capacity="600",
        calculation_nominal_capacity="600", required_usable_capacity="380",
        tester_location="Lab", tested_by="Tester", reported_by="Reporter",
        input_path=str(tmp_path), output_path=str(tmp_path), version="1.0",
    )


@pytest.fixture
def validation_ui(valid_values):
    window = SimpleNamespace()
    fields = {
        "battery_type": ("comboBox_BatteryType", "label_BatteryType"),
        "construction_method": ("comboBox_ConstructionMethod", "label_ConstructionMethod"),
        "specification_type": ("comboBox_Specification_Type", "label_Specification"),
        "specification_method": ("comboBox_Specification_Method", "label_Specification"),
        "manufacturer": ("comboBox_Manufacturer", "label_Manufacturer"),
        "batch_date_code": ("lineEdit_BatchDateCode", "label_BatchDateCode"),
        "samples_qty": ("lineEdit_SamplesQty", "label_SamplesQty"),
        "temperature": ("comboBox_Temperature", "label_Temperature"),
        "datasheet_nominal_capacity": ("lineEdit_DatasheetNominalCapacity", "label_DatasheetNominalCapacity"),
        "calculation_nominal_capacity": ("lineEdit_CalculationNominalCapacity", "label_CalculationNominalCapacity"),
        "required_usable_capacity": ("lineEdit_RequiredUseableCapacity", "label_RequiredUseableCapacity"),
        "tester_location": ("comboBox_TesterLocation", "label_TesterLocation"),
        "tested_by": ("comboBox_TestedBy", "label_TestedBy"),
        "reported_by": ("comboBox_ReportedBy", None),
        "test_profile": ("lineEdit_TestProfile", "label_TestProfile"),
        "input_path": ("lineEdit_InputPath", "label_InputPath"),
        "output_path": ("lineEdit_OutputPath", "label_OutputPath"),
        "version": ("lineEdit_Version", "label_Version"),
        "accelerated_aging": ("spinBox_AcceleratedAging", "label_AcceleratedAging"),
    }
    for name, (widget_name, label_name) in fields.items():
        widget = Mock()
        widget.text.return_value = getattr(valid_values, name)
        widget.currentText.return_value = getattr(valid_values, name)
        widget.value.return_value = getattr(valid_values, name)
        setattr(window, widget_name, widget)
        if label_name:
            setattr(window, label_name, Mock())
    window.field_widgets = {
        name: getattr(window, widget_name) for name, (widget_name, _) in fields.items()
    }
    window.statusBar_BatteryAnalysis = Mock()
    window.pushButton_Run = Mock()
    window.checker_battery_type = SimpleNamespace(b_check_pass=True)
    manager = ValidationManager(window)
    window.validation_manager = manager
    window.checkinput = manager.checkinput
    return window, manager


def test_profile_is_optional_through_run_entry(validation_ui):
    window, manager = validation_ui
    assert manager.validate_fields().is_valid
    assert manager.checkinput()
    assert AnalysisRunner(window)._check_inputs()


@pytest.mark.parametrize("field", ["reported_by", "version"])
@pytest.mark.parametrize("value", ["", "   "])
def test_required_run_fields_are_also_rejected_by_pure_validator(valid_values, field, value):
    result = InputValidator.validate_all(replace(valid_values, **{field: value}))
    assert not result.is_valid
    assert field in result.field_errors


@pytest.mark.parametrize("field", ["input_path", "output_path"])
def test_regular_file_is_not_an_analysis_directory(valid_values, tmp_path, field):
    file = tmp_path / "not-a-directory.ndax"
    file.write_bytes(b"data")
    result = InputValidator.validate_all(replace(valid_values, **{field: str(file)}))
    assert not result.is_valid
    assert "directory" in result.field_errors[field]


def test_live_path_and_full_check_use_the_same_rule(validation_ui, tmp_path):
    window, manager = validation_ui
    file = tmp_path / "file.ndax"
    file.write_bytes(b"data")
    window.lineEdit_InputPath.text.return_value = str(file)
    manager.validate_input_path()
    assert window.lineEdit_InputPath.setStyleSheet.call_args.args[0]
    assert not manager.validate_fields().is_valid
    window.lineEdit_InputPath.text.return_value = str(tmp_path)
    manager.validate_input_path()
    window.lineEdit_InputPath.setStyleSheet.assert_called_with("")


@pytest.mark.parametrize("field", ["calculation_nominal_capacity", "required_usable_capacity"])
@pytest.mark.parametrize("value", ["0", "-1", "1.5", "invalid", "   "])
def test_live_capacity_and_full_check_agree(validation_ui, field, value):
    window, manager = validation_ui
    widget_name = {
        "calculation_nominal_capacity": "lineEdit_CalculationNominalCapacity",
        "required_usable_capacity": "lineEdit_RequiredUseableCapacity",
    }[field]
    widget = getattr(window, widget_name)
    widget.text.return_value = value
    manager.validate_required_fields()
    assert widget.setStyleSheet.call_args.args[0]
    assert field in manager.validate_fields().field_errors
    widget.text.return_value = "380"
    manager.validate_required_fields()
    widget.setStyleSheet.assert_called_with("")


def test_shared_specification_label_stays_red_for_either_field(validation_ui):
    window, manager = validation_ui
    manager._apply_field_errors({"specification_type": "Required"})
    window.label_Specification.setStyleSheet.assert_called_with("background-color:red")
    manager._apply_field_errors({"specification_method": "Required"})
    window.label_Specification.setStyleSheet.assert_called_with("background-color:red")
    manager._apply_field_errors({})
    window.label_Specification.setStyleSheet.assert_called_with("")


def test_error_feedback_clears_on_success_and_uses_one_result(validation_ui):
    window, manager = validation_ui
    window.comboBox_ReportedBy.currentText.return_value = ""
    with patch.object(manager, "validate_fields", wraps=manager.validate_fields) as validate:
        assert not manager.checkinput()
        validate.assert_called_once()
    window.comboBox_ReportedBy.setStyleSheet.assert_called_with(
        "background-color: #FFDDDD; border: 1px solid #FF6666;"
    )
    assert "Reported By" in window.statusBar_BatteryAnalysis.showMessage.call_args.args[0]
    window.comboBox_ReportedBy.currentText.return_value = "Reporter"
    assert manager.checkinput()
    window.comboBox_ReportedBy.setStyleSheet.assert_called_with("")
    window.pushButton_Run.setEnabled.assert_called_with(False)


@pytest.mark.parametrize("field", [
    "battery_type", "specification_type", "specification_method", "manufacturer",
    "batch_date_code", "samples_qty", "temperature", "datasheet_nominal_capacity",
    "calculation_nominal_capacity", "required_usable_capacity", "tester_location",
    "tested_by", "reported_by", "input_path", "output_path", "version",
])
def test_every_required_field_agrees_between_pure_and_ui(validation_ui, valid_values, field):
    window, manager = validation_ui
    widget = window.field_widgets[field]
    widget.text.return_value = ""
    widget.currentText.return_value = ""
    pure_result = InputValidator.validate_all(replace(valid_values, **{field: ""}))
    ui_result = manager.validate_fields()
    assert pure_result.field_errors == ui_result.field_errors
    assert field in ui_result.field_errors
    assert not manager.checkinput()
    assert widget.setStyleSheet.call_args.args[0]


@pytest.mark.parametrize("battery_type,required", [("Coin Cell", False), ("Pouch Cell", True)])
def test_construction_remains_conditional(validation_ui, battery_type, required):
    window, manager = validation_ui
    window.comboBox_BatteryType.currentText.return_value = battery_type
    assert ("construction_method" in manager.validate_fields().field_errors) is required
    assert manager.checkinput() is not required


def test_aging_range_is_still_enforced_in_run_entry(validation_ui):
    window, manager = validation_ui
    window.spinBox_AcceleratedAging.value.return_value = 11
    assert not manager.checkinput()
    window.label_AcceleratedAging.setStyleSheet.assert_called_with("background-color:red")


def test_run_rechecks_directories_after_live_feedback(validation_ui, tmp_path):
    window, manager = validation_ui
    directory = tmp_path / "input"
    directory.mkdir()
    window.lineEdit_InputPath.text.return_value = str(directory)
    manager.validate_input_path()
    assert manager.validate_fields().is_valid
    directory.rmdir()
    assert not manager.checkinput()
    assert "Input path does not exist" in window.statusBar_BatteryAnalysis.showMessage.call_args.args[0]
