"""字段级验证规则（从 validation_manager.py 拆出）

版本号、输入路径、必填字段与 InputValidator 字段校验。"""

import os
from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from battery_analysis.main.main_window import Main

from battery_analysis.i18n.language_manager import _
from battery_analysis.utils.input_validator import FieldValues, InputValidator, ValidationResult


class ValidationFieldsMixin:
    """版本号 / 输入路径 / 必填字段 / InputValidator 字段校验"""

    main_window: Main
    _get_types_requiring_construction: Callable[[], list[str]]

    def validate_version(self) -> None:
        """
        验证版本号格式并提供实时反馈
        """
        version_text = self.main_window.lineEdit_Version.text()
        result = InputValidator._validate_version(FieldValues(version=version_text))
        if not result.is_valid:
            self.main_window.statusBar_BatteryAnalysis.showMessage(
                f"{_('Warning')}: {_('Version format is invalid. Expected x.y.z format')}"
            )
            # 设置错误样式
            self.main_window.lineEdit_Version.setStyleSheet(
                "background-color: #FFDDDD; border: 1px solid #FF6666;"
            )
        else:
            # 重置样式
            self.main_window.lineEdit_Version.setStyleSheet("")
            # 如果所有验证都通过，显示正常状态
            if self.main_window.checker_battery_type.b_check_pass:
                self.main_window.statusBar_BatteryAnalysis.showMessage(_("Ready"))

    def validate_input_path(self) -> None:
        """
        验证输入路径是否存在
        """
        path = self.main_window.lineEdit_InputPath.text()
        if path and not os.path.exists(path):
            self.main_window.statusBar_BatteryAnalysis.showMessage(
                f"{_('Warning')}: {_('Input path does not exist')}"
            )
            self.main_window.lineEdit_InputPath.setStyleSheet(
                "background-color: #FFDDDD; border: 1px solid #FF6666;"
            )
        else:
            self.main_window.lineEdit_InputPath.setStyleSheet("")
            # 如果所有验证都通过，显示正常状态
            if self.main_window.checker_battery_type.b_check_pass:
                self.main_window.statusBar_BatteryAnalysis.showMessage(_("Ready"))

    def validate_required_fields(self) -> None:
        """
        验证必填字段是否为空
        """
        empty_fields = []

        if not self.main_window.lineEdit_SamplesQty.text():
            empty_fields.append("Samples Qty")
            self.main_window.lineEdit_SamplesQty.setStyleSheet(
                "background-color: #FFDDDD; border: 1px solid #FF6666;"
            )
        else:
            self.main_window.lineEdit_SamplesQty.setStyleSheet("")

        if not self.main_window.lineEdit_DatasheetNominalCapacity.text():
            empty_fields.append("Nominal Capacity")
            self.main_window.lineEdit_DatasheetNominalCapacity.setStyleSheet(
                "background-color: #FFDDDD; border: 1px solid #FF6666;"
            )
        else:
            self.main_window.lineEdit_DatasheetNominalCapacity.setStyleSheet("")

        if not self.main_window.lineEdit_CalculationNominalCapacity.text():
            empty_fields.append("Calculated Capacity")
            self.main_window.lineEdit_CalculationNominalCapacity.setStyleSheet(
                "background-color: #FFDDDD; border: 1px solid #FF6666;"
            )
        else:
            self.main_window.lineEdit_CalculationNominalCapacity.setStyleSheet("")

        if not self.main_window.lineEdit_RequiredUseableCapacity.text():
            empty_fields.append("Useable Capacity")
            self.main_window.lineEdit_RequiredUseableCapacity.setStyleSheet(
                "background-color: #FFDDDD; border: 1px solid #FF6666;"
            )
        else:
            self.main_window.lineEdit_RequiredUseableCapacity.setStyleSheet("")

        if empty_fields:
            self.main_window.statusBar_BatteryAnalysis.showMessage(
                f"{_('Warning')}: {_('The following required fields are empty')}: {', '.join(empty_fields)}"
            )
        else:
            # 如果所有验证都通过，显示正常状态
            if self.main_window.checker_battery_type.b_check_pass:
                self.main_window.statusBar_BatteryAnalysis.showMessage(_("Ready"))

    def validate_fields(self) -> ValidationResult:
        """使用纯 InputValidator 验证当前 UI 字段。"""
        values = FieldValues(
            battery_type=self.main_window.comboBox_BatteryType.currentText(),
            construction_method=self.main_window.comboBox_ConstructionMethod.currentText(),
            specification_type=self.main_window.comboBox_Specification_Type.currentText(),
            specification_method=self.main_window.comboBox_Specification_Method.currentText(),
            manufacturer=self.main_window.comboBox_Manufacturer.currentText(),
            batch_date_code=self.main_window.lineEdit_BatchDateCode.text(),
            samples_qty=self.main_window.lineEdit_SamplesQty.text(),
            temperature=self.main_window.comboBox_Temperature.currentText(),
            datasheet_nominal_capacity=self.main_window.lineEdit_DatasheetNominalCapacity.text(),
            calculation_nominal_capacity=self.main_window.lineEdit_CalculationNominalCapacity.text(),
            accelerated_aging=self.main_window.spinBox_AcceleratedAging.value(),
            tester_location=self.main_window.comboBox_TesterLocation.currentText(),
            tested_by=self.main_window.comboBox_TestedBy.currentText(),
            reported_by=self.main_window.comboBox_ReportedBy.currentText(),
            test_profile=self.main_window.lineEdit_TestProfile.text(),
            input_path=self.main_window.lineEdit_InputPath.text(),
            output_path=self.main_window.lineEdit_OutputPath.text(),
            version=self.main_window.lineEdit_Version.text(),
            required_usable_capacity=self.main_window.lineEdit_RequiredUseableCapacity.text(),
        )
        return InputValidator.validate_all(
            values,
            types_requiring_construction=self._get_types_requiring_construction(),
        )
