"""把统一字段校验结果展示到 UI；业务规则由 InputValidator 负责。"""

from collections.abc import Callable
from typing import TYPE_CHECKING

from battery_analysis.utils.input_validator import ValidationResult

if TYPE_CHECKING:
    from battery_analysis.main.main_window import Main

_ERROR_WIDGET_STYLE = "background-color: #FFDDDD; border: 1px solid #FF6666;"
_ERROR_LABEL_STYLE = "background-color:red"


class ValidationFeedbackMixin:
    """checkinput 主流程与字段级 UI 高亮/警告反馈。"""

    main_window: Main
    validate_fields: Callable[[], ValidationResult]

    def checkinput(self) -> bool:
        """只校验一次，界面不再维护第二份必填项和范围规则。"""
        result = self.validate_fields()
        if not result.is_valid:
            return self._report_field_validation_failure(result)

        self._apply_field_errors({})
        self.main_window.pushButton_Run.setEnabled(False)
        self.main_window.pushButton_Run.setFocus()
        return True

    def _report_field_validation_failure(self, result) -> bool:
        """把纯验证器的失败结果反映到 UI，并返回 False。"""
        self._apply_field_errors(result.field_errors)
        messages = result.errors or list(result.field_errors.values())
        self.main_window.statusBar_BatteryAnalysis.showMessage(
            "; ".join(messages) if messages else "Validation failed"
        )
        self.main_window.pushButton_Run.setText("Rerun")
        self.main_window.pushButton_Run.setFocus()
        return False

    def _apply_field_errors(self, field_errors: dict) -> None:
        """高亮错误字段；共享标签按所有关联字段的错误合并显示。"""
        field_to_widget = {
            "battery_type": (
                self.main_window.comboBox_BatteryType,
                self.main_window.label_BatteryType,
            ),
            "construction_method": (
                self.main_window.comboBox_ConstructionMethod,
                self.main_window.label_ConstructionMethod,
            ),
            "specification_type": (
                self.main_window.comboBox_Specification_Type,
                self.main_window.label_Specification,
            ),
            "specification_method": (
                self.main_window.comboBox_Specification_Method,
                self.main_window.label_Specification,
            ),
            "manufacturer": (
                self.main_window.comboBox_Manufacturer,
                self.main_window.label_Manufacturer,
            ),
            "batch_date_code": (
                self.main_window.lineEdit_BatchDateCode,
                self.main_window.label_BatchDateCode,
            ),
            "samples_qty": (
                self.main_window.lineEdit_SamplesQty,
                self.main_window.label_SamplesQty,
            ),
            "temperature": (
                self.main_window.comboBox_Temperature,
                self.main_window.label_Temperature,
            ),
            "datasheet_nominal_capacity": (
                self.main_window.lineEdit_DatasheetNominalCapacity,
                self.main_window.label_DatasheetNominalCapacity,
            ),
            "calculation_nominal_capacity": (
                self.main_window.lineEdit_CalculationNominalCapacity,
                self.main_window.label_CalculationNominalCapacity,
            ),
            "required_usable_capacity": (
                self.main_window.lineEdit_RequiredUseableCapacity,
                self.main_window.label_RequiredUseableCapacity,
            ),
            "tester_location": (
                self.main_window.comboBox_TesterLocation,
                self.main_window.label_TesterLocation,
            ),
            "tested_by": (self.main_window.comboBox_TestedBy, self.main_window.label_TestedBy),
            "reported_by": (self.main_window.comboBox_ReportedBy, None),
            "test_profile": (
                self.main_window.lineEdit_TestProfile,
                self.main_window.label_TestProfile,
            ),
            "input_path": (self.main_window.lineEdit_InputPath, self.main_window.label_InputPath),
            "output_path": (
                self.main_window.lineEdit_OutputPath,
                self.main_window.label_OutputPath,
            ),
            "version": (self.main_window.lineEdit_Version, self.main_window.label_Version),
            "accelerated_aging": (
                self.main_window.spinBox_AcceleratedAging,
                self.main_window.label_AcceleratedAging,
            ),
        }
        label_errors = {}
        for field_name, (widget, label) in field_to_widget.items():
            invalid = field_name in field_errors
            widget.setStyleSheet(_ERROR_WIDGET_STYLE if invalid else "")
            if label is not None:
                label_errors[label] = label_errors.get(label, False) or invalid
        for label, invalid in label_errors.items():
            label.setStyleSheet(_ERROR_LABEL_STYLE if invalid else "")
