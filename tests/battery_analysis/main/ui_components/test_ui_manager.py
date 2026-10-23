from unittest.mock import Mock, patch

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QValidator
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication, QLineEdit, QWidget

from battery_analysis.main.business_logic.validation_fields import ValidationFieldsMixin
from battery_analysis.main.ui_components.ui_manager import UIManager


class TestUIManager:
    def setup_method(self):
        mock_main = Mock()
        mock_main.tableWidget_TestInformation = Mock()
        mock_main.scrollArea = Mock()
        self.manager = UIManager(mock_main)

    def test_init_window(self):
        with patch.object(self.manager, "_load_application_icon", return_value=Mock()):
            self.manager.init_window()


_version_app = None


@pytest.mark.parametrize("name", [
    "SamplesQty", "DatasheetNominalCapacity", "CalculationNominalCapacity", "RequiredUseableCapacity",
])
def test_derived_fields_are_display_only_but_allow_automatic_updates(name):
    global _version_app
    _version_app = QApplication.instance() or QApplication([])
    window = QWidget()
    for field_name in ("SamplesQty", "DatasheetNominalCapacity", "CalculationNominalCapacity", "RequiredUseableCapacity", "Version", "InputPath", "TestProfile"):
        setattr(window, "lineEdit_" + field_name, QLineEdit(window))
    window.validation_manager = Mock()
    UIManager(window).init_lineedit()
    field = getattr(window, "lineEdit_" + name)

    assert field.isReadOnly()
    assert not field.hasFrame()
    assert field.validator() is None
    assert field.focusPolicy() == Qt.FocusPolicy.ClickFocus
    assert not window.lineEdit_Version.isReadOnly()
    assert window.lineEdit_Version.validator() is not None

    field.setText("920")
    field.selectAll()
    QTest.keyClicks(field, "123")
    QTest.keyClick(field, Qt.Key.Key_Backspace)
    assert field.text() == "920"

    window.validation_manager.validate_required_fields.reset_mock()
    field.setText("782")
    assert field.text() == "782"
    window.validation_manager.validate_required_fields.assert_called_once()


@pytest.mark.parametrize(("value", "state", "invalid_feedback"), [
    ("", QValidator.State.Intermediate, False),
    ("1", QValidator.State.Intermediate, True),
    ("1.", QValidator.State.Intermediate, True),
    ("1.0", QValidator.State.Acceptable, False),
    ("1.0.", QValidator.State.Intermediate, True),
    ("1.0.1", QValidator.State.Acceptable, False),
    ("1.01", QValidator.State.Acceptable, False),
    ("a", QValidator.State.Invalid, True),
    ("1.0.1.2", QValidator.State.Invalid, True),
])
def test_version_validator_keeps_editing_intermediate_but_feedback_matches_run(value, state, invalid_feedback):
    global _version_app
    _version_app = QApplication.instance() or QApplication([])
    window = QWidget()
    for name in ("SamplesQty", "DatasheetNominalCapacity", "CalculationNominalCapacity", "RequiredUseableCapacity", "Version", "InputPath", "TestProfile"):
        setattr(window, "lineEdit_" + name, QLineEdit(window))
    window.validation_manager = Mock()
    window.statusBar_BatteryAnalysis = Mock()
    window.checker_battery_type = Mock(b_check_pass=True)
    UIManager(window).init_lineedit()
    validator = window.lineEdit_Version.validator()
    assert validator.validate(value, len(value))[0] == state
    window.lineEdit_Version.setText(value)
    rules = ValidationFieldsMixin()
    rules.main_window = window
    rules.validate_version()
    assert bool(window.lineEdit_Version.styleSheet()) == invalid_feedback
    if invalid_feedback:
        assert "Version format is invalid" in window.statusBar_BatteryAnalysis.showMessage.call_args.args[0]
