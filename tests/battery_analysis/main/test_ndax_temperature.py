"""NDAX temperature selection, mixed-input rejection and UI authority."""
import zipfile
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest
from PyQt6.QtWidgets import QApplication, QComboBox, QLineEdit, QSpinBox

from battery_analysis.main.business_logic.data_processor import DataProcessor
from battery_analysis.main.business_logic.validation_spec_rules import ValidationSpecRulesMixin
from battery_analysis.main.handlers.temperature_handler import TemperatureHandler, TemperatureType
from battery_analysis.main.managers.analysis_runner import AnalysisRunner


def test_temperature_ui_follows_ndax_and_preserves_nominal_value():
    app = QApplication.instance() or QApplication([])
    mw = Mock()
    mw.comboBox_Temperature = QComboBox()
    mw.comboBox_Temperature.addItems([t.value for t in TemperatureType])
    mw.spinBox_Temperature = QSpinBox()
    mw.spinBox_Temperature.setRange(-100, 100)
    handler = TemperatureHandler(mw)
    handler.clear_temperature_ui()
    assert mw.comboBox_Temperature.currentText() == ""
    handler.update_temperature_ui(TemperatureType.FREEZER)
    assert mw.comboBox_Temperature.currentText() == "Freezer Temperature"
    assert not mw.comboBox_Temperature.isEnabled()
    assert mw.spinBox_Temperature.value() == -20
    mw.spinBox_Temperature.setValue(-25)
    handler.update_temperature_ui(TemperatureType.FREEZER)
    assert handler.get_temperature_value() == "Freezer Temperature:-25"
    handler.update_temperature_ui(TemperatureType.ROOM)
    assert handler.get_temperature_value() == "Room Temperature"
    assert not mw.spinBox_Temperature.isEnabled()
    handler.clear_temperature_ui()
    assert mw.comboBox_Temperature.currentIndex() == -1
    mw.comboBox_Temperature.close()
    mw.spinBox_Temperature.close()
    assert app is not None


@pytest.mark.parametrize("other", [
    {"temperature": "Room Temperature", "current_levels": [15, 13, 7.5, 3]},
    {"temperature": "Freezer Temperature", "current_levels": [30, 26, 15, 6]},
])
def test_scan_rejects_mixed_ndax_inputs(other):
    mw = Mock()
    processor = DataProcessor(mw)
    entries = [
        {"filename": "a.ndax", "temperature": "Freezer Temperature", "current_levels": [15, 13, 7.5, 3]},
        {"filename": "b.ndax", **other},
    ]
    with patch.object(processor, "_process_first_excel_file") as first:
        processor._on_excel_files_processed((["a.ndax", "b.ndax"], entries, []), 0)
    first.assert_not_called()
    mw.temperature_handler.clear_temperature_ui.assert_called_once()
    assert "different recipe temperatures" in mw.checker_input_xlsx.set_error.call_args.args[0]


def test_scan_sets_freezer_ui_from_metadata():
    mw = Mock()
    processor = DataProcessor(mw)
    entry = {"filename": "room.ndax", "temperature": "Freezer Temperature", "current_levels": [15, 13, 7.5, 3]}
    with patch.object(processor, "_process_first_excel_file"), patch.object(processor, "_reconnect_specification_signals"):
        processor._on_excel_files_processed((["room.ndax"], [entry], []), 0)
    mw.temperature_handler.update_temperature_ui.assert_called_once_with(TemperatureType.FREEZER)


def test_temperature_refresh_recomputes_capacity_and_report_threshold():
    from battery_analysis.utils.quality_requirements import build_expectations

    app = QApplication.instance() or QApplication([])
    mw = SimpleNamespace(
        comboBox_Temperature=QComboBox(), spinBox_Temperature=QSpinBox(),
        comboBox_Specification_Type=QComboBox(), comboBox_Specification_Method=QComboBox(),
        comboBox_ConstructionMethod=QComboBox(),
        lineEdit_DatasheetNominalCapacity=QLineEdit(),
        lineEdit_CalculationNominalCapacity=QLineEdit(),
        lineEdit_RequiredUseableCapacity=QLineEdit(), config_manager=Mock(),
    )
    mw.comboBox_Temperature.addItems([t.value for t in TemperatureType])
    mw.spinBox_Temperature.setRange(-100, 100)
    mw.comboBox_Specification_Type.addItem("CR2450")
    mw.comboBox_Specification_Method.addItem("1S1P")
    mw.config_manager.get_config.return_value = [
        "CR2450/1S1P/600/550/380/1.0", "CR2450/1S1P/600/550/280/1.0",
    ]
    validator = ValidationSpecRulesMixin()
    validator.main_window = mw
    mw.check_construction = validator.check_construction
    handler = TemperatureHandler(mw)
    for temperature, required, current in [
        (TemperatureType.ROOM, "380", 30), (TemperatureType.FREEZER, "280", 15),
        (TemperatureType.ROOM, "380", 30),
    ]:
        handler.update_temperature_ui(temperature)
        assert mw.lineEdit_RequiredUseableCapacity.text() == required
        assert mw.lineEdit_DatasheetNominalCapacity.text() == "600"
        assert mw.lineEdit_CalculationNominalCapacity.text() == "550"
        test_info = [""] * 19
        test_info[2], test_info[3] = "CR2450", "1S1P"
        test_info[7], test_info[9], test_info[17] = handler.get_temperature_value(), "600", required
        expectation = build_expectations(test_info)[0]
        assert expectation.threshold_mah == int(required)
        assert expectation.current_ma == current
    assert app is not None


def test_preflight_rechecks_mixed_temperatures_even_with_same_currents(tmp_path):
    for name, step in [("a.ndax", "Freezer.xml"), ("b.ndax", "room.xml")]:
        with zipfile.ZipFile(tmp_path / name, "w") as archive:
            archive.writestr("TestInfo.xml", f'<root><TestInfo StepName="{step}"/></root>')
            archive.writestr("Step.xml", '<root><Step_Info><Step4><PulseData Count="1"><Pulse1 Value="-30"/></PulseData></Step4></Step_Info></root>')
    mw = Mock()
    mw.lineEdit_InputPath.text.return_value = str(tmp_path)
    with pytest.raises(ValueError, match=r"Different TestInfo\.xml recipe temperatures"):
        AnalysisRunner(mw)._preflight_recipe()
