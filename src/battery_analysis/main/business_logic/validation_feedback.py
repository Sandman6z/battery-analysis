"""checkinput 校验执行与字段级 UI 反馈（从 validation_manager.py 拆出）

checkinput 主流程与标签/输入框高亮、警告汇总。"""

from collections.abc import Callable
from typing import TYPE_CHECKING

from battery_analysis.utils.input_validator import ValidationResult

if TYPE_CHECKING:
    from battery_analysis.main.main_window import Main

_ERROR_WIDGET_STYLE = "background-color: #FFDDDD; border: 1px solid #FF6666;"
_ERROR_LABEL_STYLE = "background-color:red"

# 向后兼容的 UI 级字段检查表：(类型, 字段名, 控件属性, 标签属性)
# 顺序即 warning_info 中缺失项的出现顺序（决定状态栏警告文案），不要随意调换。
_LEGACY_FIELD_CHECKS = [
    ("combo", "Battery Type", "comboBox_BatteryType", "label_BatteryType"),
    (
        "construction",
        "Construction Method",
        "comboBox_ConstructionMethod",
        "label_ConstructionMethod",
    ),
    ("spec", "Specification", "comboBox_Specification_Type", "label_Specification"),
    ("combo", "Manufacturer", "comboBox_Manufacturer", "label_Manufacturer"),
    ("line", "Batch/Date Code", "lineEdit_BatchDateCode", "label_BatchDateCode"),
    ("line", "SamplesQty", "lineEdit_SamplesQty", "label_SamplesQty"),
    ("combo", "Temperature", "comboBox_Temperature", "label_Temperature"),
    (
        "line",
        "Datasheet Nominal Capacity",
        "lineEdit_DatasheetNominalCapacity",
        "label_DatasheetNominalCapacity",
    ),
    (
        "line",
        "Calculation Nominal Capacity",
        "lineEdit_CalculationNominalCapacity",
        "label_CalculationNominalCapacity",
    ),
    ("aging", "Accelerated Aging", "spinBox_AcceleratedAging", "label_AcceleratedAging"),
    (
        "line",
        "Required Useable Capacity",
        "lineEdit_RequiredUseableCapacity",
        "label_RequiredUseableCapacity",
    ),
    ("combo", "Test Location", "comboBox_TesterLocation", "label_TesterLocation"),
    ("combo", "Test By", "comboBox_TestedBy", "label_TestedBy"),
    ("combo", "Reported By", "comboBox_ReportedBy", None),
    ("line", "Test Profile", "lineEdit_TestProfile", "label_TestProfile"),
    ("line", "Input Path", "lineEdit_InputPath", "label_InputPath"),
    ("line", "Output Path", "lineEdit_OutputPath", "label_OutputPath"),
    ("line", "Version", "lineEdit_Version", "label_Version"),
]


class ValidationFeedbackMixin:
    """checkinput 主流程与字段级 UI 高亮/警告反馈"""

    main_window: Main
    validate_fields: Callable[[], ValidationResult]
    _get_types_requiring_construction: Callable[[], list[str]]

    def checkinput(self) -> bool:
        """
        检查所有输入是否完整有效（委托给 InputValidator + UI 样式更新）。

        Returns:
            bool: 输入是否通过验证
        """
        # 纯验证器先跑，失败则直接按字段高亮并短路
        result = self.validate_fields()
        if not result.is_valid:
            return self._report_field_validation_failure(result)

        # 向后兼容：继续执行原有 UI 级检查
        warning_info = ["Unknown: "]
        check_pass_flag = self._check_legacy_fields(warning_info)
        return self._finalize_check_result(check_pass_flag, warning_info)

    def _report_field_validation_failure(self, result) -> bool:
        """把纯验证器的失败结果反映到 UI，并返回 False"""
        self._apply_field_errors(result.field_errors)
        self.main_window.statusBar_BatteryAnalysis.showMessage(
            "; ".join(result.errors) if result.errors else "Validation failed"
        )
        self.main_window.pushButton_Run.setText("Rerun")
        self.main_window.pushButton_Run.setFocus()
        return False

    def _check_legacy_fields(self, warning_info) -> bool:
        """按 `_LEGACY_FIELD_CHECKS` 逐字段检查并高亮缺失项

        Returns:
            bool: 全部字段是否通过
        """
        mw = self.main_window
        check_pass_flag = True
        self._reset_all_label_styles()

        for kind, name, widget_attr, label_attr in _LEGACY_FIELD_CHECKS:
            widget = getattr(mw, widget_attr)
            label = getattr(mw, label_attr) if label_attr else None

            if kind == "combo":
                check_pass_flag &= self._check_combobox(name, widget, label, warning_info)
            elif kind == "line":
                check_pass_flag &= self._check_line_edit(name, widget, label, warning_info)
            elif kind == "construction":
                # 仅需要构造方法的电池类型（如 Pouch Cell）才检查；Coin Cell 下拉框禁用
                if (
                    mw.comboBox_BatteryType.currentText()
                    in self._get_types_requiring_construction()
                ):
                    check_pass_flag &= self._check_combobox(name, widget, label, warning_info)
            elif kind == "spec":
                if not (
                    mw.comboBox_Specification_Type.currentText()
                    and mw.comboBox_Specification_Method.currentText()
                ):
                    check_pass_flag = False
                    warning_info.append(name)
                    if label is not None:
                        label.setStyleSheet(_ERROR_LABEL_STYLE)
            elif kind == "aging":
                if not 0 <= widget.value() <= 10:
                    check_pass_flag = False
                    warning_info.append(name)
                    if label is not None:
                        label.setStyleSheet(_ERROR_LABEL_STYLE)

        return check_pass_flag

    def _finalize_check_result(self, check_pass_flag: bool, warning_info: list) -> bool:
        """根据逐字段检查结果更新运行按钮与状态栏"""
        if check_pass_flag:
            self.main_window.pushButton_Run.setEnabled(False)
            self.main_window.pushButton_Run.setFocus()
        else:
            warning_info_str = self._build_warning_message(warning_info)
            self.main_window.statusBar_BatteryAnalysis.showMessage(warning_info_str)
            self.main_window.pushButton_Run.setText("Rerun")
            self.main_window.pushButton_Run.setFocus()

        return check_pass_flag

    def _apply_field_errors(self, field_errors: dict) -> None:
        """根据字段错误字典高亮对应 UI 控件。

        覆盖所有必填字段（含组合框），否则验证失败时用户看不到具体是哪个字段。
        """
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
        for field_name, (widget, label) in field_to_widget.items():
            if field_name in field_errors:
                widget.setStyleSheet("background-color: #FFDDDD; border: 1px solid #FF6666;")
                if label:
                    label.setStyleSheet("background-color:red")
            else:
                widget.setStyleSheet("")
                if label:
                    label.setStyleSheet("")

    def _reset_all_label_styles(self):
        """重置所有标签的样式"""
        # 重置所有标签的背景颜色
        labels_to_reset = [
            self.main_window.label_BatteryType,
            self.main_window.label_ConstructionMethod,
            self.main_window.label_Specification,
            self.main_window.label_Manufacturer,
            self.main_window.label_BatchDateCode,
            self.main_window.label_SamplesQty,
            self.main_window.label_Temperature,
            self.main_window.label_DatasheetNominalCapacity,
            self.main_window.label_CalculationNominalCapacity,
            self.main_window.label_AcceleratedAging,
            self.main_window.label_RequiredUseableCapacity,
            self.main_window.label_TesterLocation,
            self.main_window.label_TestedBy,
            self.main_window.label_TestProfile,
            self.main_window.label_InputPath,
            self.main_window.label_OutputPath,
            self.main_window.label_Version,
        ]

        for label in labels_to_reset:
            if label:
                label.setStyleSheet("")

    def _check_combobox(self, field_name, combobox, label, warning_info):
        """检查组合框是否有选择

        Args:
            field_name: 字段名称
            combobox: 组合框控件
            label: 对应的标签控件
            warning_info: 警告信息列表

        Returns:
            bool: 检查是否通过
        """
        if not combobox.currentText():
            warning_info.append(field_name)
            if label:
                label.setStyleSheet("background-color:red")
            return False
        return True

    def _check_line_edit(self, field_name, line_edit, label, warning_info):
        """检查文本框是否有输入

        Args:
            field_name: 字段名称
            line_edit: 文本框控件
            label: 对应的标签控件
            warning_info: 警告信息列表

        Returns:
            bool: 检查是否通过
        """
        if not line_edit.text():
            warning_info.append(field_name)
            if label:
                label.setStyleSheet("background-color:red")
            return False
        return True

    def _build_warning_message(self, warning_info):
        """构建警告信息字符串

        Args:
            warning_info: 警告信息列表

        Returns:
            str: 构建好的警告信息字符串
        """
        if len(warning_info) <= 1:
            return "Unknown: "

        warning_info_str = warning_info[0]
        for i in range(1, len(warning_info) - 1):
            warning_info_str = warning_info_str + warning_info[i] + ", "
        warning_info_str += warning_info[-1]

        return warning_info_str
