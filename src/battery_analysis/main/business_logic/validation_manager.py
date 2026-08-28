"""
验证管理模块

这个模块负责处理所有输入验证逻辑，包括：
- 版本号格式验证
- 输入路径验证
- 必填字段验证
- 电池类型验证
- 规格验证
"""

import logging
import os
import re

import PyQt6.QtCore as QC

from battery_analysis.i18n.language_manager import _
from battery_analysis.utils.input_validator import FieldValues, InputValidator, ValidationResult


class ValidationManager:
    """
    验证管理器，负责处理所有输入验证逻辑
    """

    def __init__(self, main_window=None):
        """
        初始化验证管理器

        Args:
            main_window: 主窗口实例（旧接口）
        """
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)

    def validate_version(self) -> None:
        """
        验证版本号格式并提供实时反馈
        """
        version_text = self.main_window.lineEdit_Version.text()
        regex = QC.QRegularExpression(r"^\d+(\.\d+){0,2}$")
        if version_text and not regex.match(version_text).hasMatch():
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

    def check_batterytype(self) -> None:
        """
        检查电池类型并更新相关UI组件
        """
        self.main_window.checker_battery_type.clear()
        current_type = self.main_window.comboBox_BatteryType.currentText()

        if not current_type:
            # 未选择电池类型 → 禁用相关控件
            self.main_window.comboBox_ConstructionMethod.setEnabled(False)
            self.main_window.comboBox_ConstructionMethod.setCurrentIndex(-1)
            self.main_window.lineEdit_DatasheetNominalCapacity.setText("")
            self.main_window.lineEdit_CalculationNominalCapacity.setText("")
            self.main_window.lineEdit_RequiredUseableCapacity.setText("")
            try:
                self.main_window.comboBox_Specification_Type.currentIndexChanged.disconnect(
                    self.main_window.check_specification
                )
                self.main_window.comboBox_Specification_Method.currentIndexChanged.disconnect(
                    self.main_window.check_specification
                )
            except (TypeError, AttributeError):
                pass
            self.main_window.comboBox_Specification_Type.clear()
            self.main_window.comboBox_Specification_Type.setEnabled(False)
            self.main_window.comboBox_Specification_Method.setEnabled(False)
            self.main_window.comboBox_Specification_Type.setCurrentIndex(-1)
            self.main_window.comboBox_Specification_Method.setCurrentIndex(-1)
            self.main_window.comboBox_Specification_Type.currentIndexChanged.connect(
                self.main_window.check_specification
            )
            self.main_window.comboBox_Specification_Method.currentIndexChanged.connect(
                self.main_window.check_specification
            )
            return

        # 构造方法：仅需要的电池类型（如 Pouch Cell）启用，其他类型禁用并清空
        requires_construction = current_type in self._get_types_requiring_construction()
        self.main_window.comboBox_ConstructionMethod.setEnabled(requires_construction)
        self.main_window.comboBox_ConstructionMethod.setCurrentIndex(-1)
        # 将文件名解析到的构造方法设置到下拉框（仅需要的类型）
        if requires_construction and self.main_window.construction_method:
            for c in range(self.main_window.comboBox_ConstructionMethod.count()):
                if (
                    self.main_window.construction_method
                    == self.main_window.comboBox_ConstructionMethod.itemText(c)
                ):
                    self.main_window.comboBox_ConstructionMethod.setCurrentIndex(c)
                    self.main_window.construction_method = ""
                    break
        self.main_window.lineEdit_DatasheetNominalCapacity.setText("")
        self.main_window.lineEdit_CalculationNominalCapacity.setText("")
        self.main_window.lineEdit_RequiredUseableCapacity.setText("")
        try:
            self.main_window.comboBox_Specification_Type.currentIndexChanged.disconnect(
                self.main_window.check_specification
            )
            self.main_window.comboBox_Specification_Method.currentIndexChanged.disconnect(
                self.main_window.check_specification
            )
        except (TypeError, AttributeError):
            pass
        self.main_window.comboBox_Specification_Type.clear()
        self.main_window.comboBox_Specification_Type.addItems(self._get_all_specifications())
        self.main_window.comboBox_Specification_Type.setEnabled(True)
        self.main_window.comboBox_Specification_Method.setEnabled(True)
        self.main_window.comboBox_Specification_Type.setCurrentIndex(-1)
        # 先恢复选中项（信号仍断开，不会触发 check_specification）
        for t in range(self.main_window.comboBox_Specification_Type.count()):
            if (
                self.main_window.specification_type
                == self.main_window.comboBox_Specification_Type.itemText(t)
            ):
                self.main_window.comboBox_Specification_Type.setCurrentIndex(t)
                break
        # 再重连信号
        self.main_window.comboBox_Specification_Type.currentIndexChanged.connect(
            self.main_window.check_specification
        )
        self.main_window.comboBox_Specification_Method.currentIndexChanged.connect(
            self.main_window.check_specification
        )

    def _get_all_specifications(self) -> list:
        """从配置中获取所有规格型号（不分电池类型）"""
        coin = self.main_window.get_config("BatteryConfig/SpecificationTypeCoinCell") or []
        pouch = self.main_window.get_config("BatteryConfig/SpecificationTypePouchCell") or []
        return coin + pouch

    def check_specification(self) -> None:
        """
        检查规格并更新相关UI组件
        """
        self.main_window.specification_type = (
            self.main_window.comboBox_Specification_Type.currentText()
        )
        # 规格 → 电池类型映射表（配置驱动，不硬编码索引）
        type_spec_pairs = [
            (
                "Coin Cell",
                self.main_window.get_config("BatteryConfig/SpecificationTypeCoinCell") or [],
            ),
            (
                "Pouch Cell",
                self.main_window.get_config("BatteryConfig/SpecificationTypePouchCell") or [],
            ),
        ]

        # 临时断开 BatteryType 信号，避免递归触发 check_batterytype
        try:
            self.main_window.comboBox_BatteryType.currentIndexChanged.disconnect(
                self.main_window.check_batterytype
            )
        except (TypeError, AttributeError):
            pass

        # 根据当前选中的规格自动匹配电池类型（按文本值，非索引）
        for type_name, spec_list in type_spec_pairs:
            if self.main_window.specification_type in spec_list:
                for i in range(self.main_window.comboBox_BatteryType.count()):
                    if self.main_window.comboBox_BatteryType.itemText(i) == type_name:
                        self.main_window.comboBox_BatteryType.setCurrentIndex(i)
                        break
                break

        self.main_window.comboBox_BatteryType.currentIndexChanged.connect(
            self.main_window.check_batterytype
        )

        # 显式执行 check_batterytype 以确保 UI 状态更新
        # （setCurrentIndex 在信号断开期间执行，不会自动触发回调）
        self.main_window.check_batterytype()

        specification_method = self.main_window.comboBox_Specification_Method.currentText()
        if not self.main_window.specification_type or not specification_method:
            return

        rules = self.main_window.get_config("BatteryConfig/Rules")
        for rule in rules:
            rule_parts = rule.split("/")
            if rule_parts[0] == self.main_window.specification_type:
                if specification_method == rule_parts[1]:
                    self.main_window.lineEdit_DatasheetNominalCapacity.setText(f"{rule_parts[2]}")
                    self.main_window.lineEdit_CalculationNominalCapacity.setText(f"{rule_parts[3]}")
                    listRequiredUseableCapacityPercentage = re.findall(r"(\d+)%", rule_parts[4])
                    if (
                        listRequiredUseableCapacityPercentage != []
                        and len(listRequiredUseableCapacityPercentage) == 1
                    ):
                        nominal_capacity = int(rule_parts[3])
                        percentage = int(listRequiredUseableCapacityPercentage[0])
                        required_capacity = int(nominal_capacity * percentage / 100)
                        self.main_window.lineEdit_RequiredUseableCapacity.setText(
                            f"{required_capacity}"
                        )
                    else:
                        self.main_window.lineEdit_RequiredUseableCapacity.setText(
                            f"{rule_parts[4]}"
                        )
                else:
                    self.main_window.lineEdit_DatasheetNominalCapacity.setText("")
                    self.main_window.lineEdit_CalculationNominalCapacity.setText("")
                    self.main_window.lineEdit_RequiredUseableCapacity.setText("")
                break
            elif rule_parts[0] in self.main_window.specification_type:
                if specification_method == rule_parts[1]:
                    self.main_window.lineEdit_DatasheetNominalCapacity.setText(f"{rule_parts[2]}")
                    self.main_window.lineEdit_CalculationNominalCapacity.setText(f"{rule_parts[3]}")
                    listRequiredUseableCapacityPercentage = re.findall(r"(\d+)%", rule_parts[4])
                    if (
                        listRequiredUseableCapacityPercentage != []
                        and len(listRequiredUseableCapacityPercentage) == 1
                    ):
                        nominal_capacity = int(rule_parts[3])
                        percentage = int(listRequiredUseableCapacityPercentage[0])
                        required_capacity = int(nominal_capacity * percentage / 100)
                        self.main_window.lineEdit_RequiredUseableCapacity.setText(
                            f"{required_capacity}"
                        )
                    else:
                        self.main_window.lineEdit_RequiredUseableCapacity.setText(
                            f"{rule_parts[4]}"
                        )
                else:
                    self.main_window.lineEdit_DatasheetNominalCapacity.setText("")
                    self.main_window.lineEdit_CalculationNominalCapacity.setText("")
                    self.main_window.lineEdit_RequiredUseableCapacity.setText("")
            else:
                pass

        # 根据 required useable capacity 自动判定温度类型
        capacity_text = self.main_window.lineEdit_RequiredUseableCapacity.text()
        if capacity_text:
            try:
                capacity_value = int(capacity_text)
                self.main_window.temperature_handler.set_temperature_by_capacity(capacity_value)
            except ValueError:
                pass

    def _get_types_requiring_construction(self) -> list:
        """返回需要填写构造方法的电池类型名称列表。

        业务约定：仅 Pouch Cell（软包电池）需要填写构造方法；
        Coin Cell（纽扣电池）不需要，且下拉框禁用。
        """
        return ["Pouch Cell"]

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

    def checkinput(self) -> bool:
        """
        检查所有输入是否完整有效（委托给 InputValidator + UI 样式更新）。

        Returns:
            bool: 输入是否通过验证
        """
        # 使用纯验证器
        result = self.validate_fields()
        if not result.is_valid:
            self._apply_field_errors(result.field_errors)
            self.main_window.statusBar_BatteryAnalysis.showMessage(
                "; ".join(result.errors) if result.errors else "Validation failed"
            )
            self.main_window.pushButton_Run.setText("Rerun")
            self.main_window.pushButton_Run.setFocus()
            return False

        # 向后兼容：继续执行原有 UI 级检查
        check_pass_flag = True
        warning_info = ["Unknown: "]

        # 重置所有标签样式
        self._reset_all_label_styles()

        # 检查必填字段
        check_pass_flag &= self._check_combobox(
            "Battery Type",
            self.main_window.comboBox_BatteryType,
            self.main_window.label_BatteryType,
            warning_info,
        )

        # 检查构造方法（仅需要的电池类型，如 Pouch Cell；Coin Cell 不需要且下拉框禁用）
        if (
            self.main_window.comboBox_BatteryType.currentText()
            in self._get_types_requiring_construction()
        ):
            check_pass_flag &= self._check_combobox(
                "Construction Method",
                self.main_window.comboBox_ConstructionMethod,
                self.main_window.label_ConstructionMethod,
                warning_info,
            )

        # 检查规格
        spec_valid = (
            self.main_window.comboBox_Specification_Type.currentText()
            and self.main_window.comboBox_Specification_Method.currentText()
        )
        if not spec_valid:
            check_pass_flag = False
            warning_info.append("Specification")
            self.main_window.label_Specification.setStyleSheet("background-color:red")

        # 检查其他必填字段
        check_pass_flag &= self._check_combobox(
            "Manufacturer",
            self.main_window.comboBox_Manufacturer,
            self.main_window.label_Manufacturer,
            warning_info,
        )

        check_pass_flag &= self._check_line_edit(
            "Batch/Date Code",
            self.main_window.lineEdit_BatchDateCode,
            self.main_window.label_BatchDateCode,
            warning_info,
        )

        check_pass_flag &= self._check_line_edit(
            "SamplesQty",
            self.main_window.lineEdit_SamplesQty,
            self.main_window.label_SamplesQty,
            warning_info,
        )

        check_pass_flag &= self._check_combobox(
            "Temperature",
            self.main_window.comboBox_Temperature,
            self.main_window.label_Temperature,
            warning_info,
        )

        check_pass_flag &= self._check_line_edit(
            "Datasheet Nominal Capacity",
            self.main_window.lineEdit_DatasheetNominalCapacity,
            self.main_window.label_DatasheetNominalCapacity,
            warning_info,
        )

        check_pass_flag &= self._check_line_edit(
            "Calculation Nominal Capacity",
            self.main_window.lineEdit_CalculationNominalCapacity,
            self.main_window.label_CalculationNominalCapacity,
            warning_info,
        )

        # 检查加速老化值
        aging_value = self.main_window.spinBox_AcceleratedAging.value()
        if aging_value < 0 or aging_value > 10:
            check_pass_flag = False
            warning_info.append("Accelerated Aging")
            self.main_window.label_AcceleratedAging.setStyleSheet("background-color:red")

        check_pass_flag &= self._check_line_edit(
            "Required Useable Capacity",
            self.main_window.lineEdit_RequiredUseableCapacity,
            self.main_window.label_RequiredUseableCapacity,
            warning_info,
        )

        check_pass_flag &= self._check_combobox(
            "Test Location",
            self.main_window.comboBox_TesterLocation,
            self.main_window.label_TesterLocation,
            warning_info,
        )

        check_pass_flag &= self._check_combobox(
            "Test By",
            self.main_window.comboBox_TestedBy,
            self.main_window.label_TestedBy,
            warning_info,
        )

        check_pass_flag &= self._check_combobox(
            "Reported By",
            self.main_window.comboBox_ReportedBy,
            None,  # Reported By没有对应的label
            warning_info,
        )

        check_pass_flag &= self._check_line_edit(
            "Test Profile",
            self.main_window.lineEdit_TestProfile,
            self.main_window.label_TestProfile,
            warning_info,
        )

        check_pass_flag &= self._check_line_edit(
            "Input Path",
            self.main_window.lineEdit_InputPath,
            self.main_window.label_InputPath,
            warning_info,
        )

        check_pass_flag &= self._check_line_edit(
            "Output Path",
            self.main_window.lineEdit_OutputPath,
            self.main_window.label_OutputPath,
            warning_info,
        )

        check_pass_flag &= self._check_line_edit(
            "Version",
            self.main_window.lineEdit_Version,
            self.main_window.label_Version,
            warning_info,
        )

        # 更新UI状态
        if check_pass_flag:
            self.main_window.pushButton_Run.setEnabled(False)
            self.main_window.pushButton_Run.setFocus()
        else:
            # 构建警告信息字符串
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
