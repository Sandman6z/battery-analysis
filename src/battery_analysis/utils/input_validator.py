"""
纯输入验证器 — 无 UI 依赖，返回结构化验证结果。

将原先分散在 ValidationManager、ValidationService、analysis_runner 的
验证逻辑集中在此。UI 层通过 ValidationResult 判断并展示样式。
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class ValidationResult:
    """验证结果。"""

    is_valid: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    field_errors: dict[str, str] = field(default_factory=dict)  # 字段名 -> 错误消息

    def merge(self, other: ValidationResult) -> ValidationResult:
        self.is_valid = self.is_valid and other.is_valid
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        self.field_errors.update(other.field_errors)
        return self


@dataclass
class FieldValues:
    """待验证的所有输入字段的纯数据表示。"""

    battery_type: str = ""
    construction_method: str = ""
    specification_type: str = ""
    specification_method: str = ""
    manufacturer: str = ""
    batch_date_code: str = ""
    samples_qty: str = ""
    temperature: str = ""
    datasheet_nominal_capacity: str = ""
    calculation_nominal_capacity: str = ""
    accelerated_aging: int = 0
    tester_location: str = ""
    tested_by: str = ""
    reported_by: str = ""
    test_profile: str = ""
    input_path: str = ""
    output_path: str = ""
    version: str = ""
    required_usable_capacity: str = ""


class InputValidator:
    """纯输入验证器，无 UI 依赖。"""

    REQUIRED_TEXT_FIELDS = [
        ("battery_type", "Battery Type"),
        ("specification_type", "Specification Type"),
        ("specification_method", "Specification Method"),
        ("manufacturer", "Manufacturer"),
        ("batch_date_code", "Batch/Date Code"),
        ("samples_qty", "Samples Qty"),
        ("temperature", "Temperature"),
        ("datasheet_nominal_capacity", "Nominal Capacity (Datasheet)"),
        ("calculation_nominal_capacity", "Nominal Capacity (Calculated)"),
        ("required_usable_capacity", "Required Useable Capacity"),
        ("tester_location", "Tester Location"),
        ("tested_by", "Tested By"),
        ("test_profile", "Test Profile"),
        ("input_path", "Input Path"),
        ("output_path", "Output Path"),
        ("version", "Version"),
    ]

    @staticmethod
    def validate_all(
        values: FieldValues, types_requiring_construction: list | None = None
    ) -> ValidationResult:
        """执行全部验证规则。

        Args:
            values: 待验证的字段值
            types_requiring_construction: 需要填写构造方法的电池类型名称列表。
                                         为 None 时默认为 ["Pouch Cell"]。
        """
        result = ValidationResult()
        result.merge(InputValidator._validate_required_fields(values))
        result.merge(InputValidator._validate_paths(values))
        result.merge(InputValidator._validate_version(values))
        result.merge(InputValidator._validate_aging(values))
        if types_requiring_construction is None:
            types_requiring_construction = ["Pouch Cell"]
        if values.battery_type in types_requiring_construction:
            result.merge(
                InputValidator._validate_required_text(
                    values.construction_method, "construction_method", "Construction Method"
                )
            )
        return result

    @staticmethod
    def validate_before_run(
        values: FieldValues, types_requiring_construction: list | None = None
    ) -> ValidationResult:
        """运行前的快速检查（仅必填项 + 路径）。"""
        return InputValidator.validate_all(values, types_requiring_construction)

    @staticmethod
    def _validate_required_fields(values: FieldValues) -> ValidationResult:
        """检查所有必填字段是否非空。"""
        result = ValidationResult()
        for field_name, label in [
            ("battery_type", "Battery Type"),
            ("specification_type", "Specification Type"),
            ("specification_method", "Specification Method"),
            ("manufacturer", "Manufacturer"),
            ("batch_date_code", "Batch/Date Code"),
            ("samples_qty", "Samples Qty"),
            ("temperature", "Temperature"),
            ("datasheet_nominal_capacity", "Nominal Capacity"),
            ("calculation_nominal_capacity", "Calculated Capacity"),
            ("required_usable_capacity", "Required Useable Capacity"),
            ("tester_location", "Tester Location"),
            ("tested_by", "Tested By"),
            ("test_profile", "Test Profile"),
            ("input_path", "Input Path"),
            ("output_path", "Output Path"),
        ]:
            val = getattr(values, field_name, "")
            if not val:
                result.is_valid = False
                result.field_errors[field_name] = f"{label} cannot be empty"
        return result

    @staticmethod
    def _validate_paths(values: FieldValues) -> ValidationResult:
        """验证输入/输出路径。"""
        import os

        result = ValidationResult()
        if values.input_path and not os.path.exists(values.input_path):
            result.is_valid = False
            result.field_errors["input_path"] = "Input path does not exist"
            result.errors.append(f"Input path does not exist: {values.input_path}")
        if values.output_path and not os.path.exists(values.output_path):
            result.is_valid = False
            result.field_errors["output_path"] = "Output path does not exist"
            result.errors.append(f"Output path does not exist: {values.output_path}")
        return result

    @staticmethod
    def _validate_version(values: FieldValues) -> ValidationResult:
        """验证版本号格式 (x.y.z)。"""
        result = ValidationResult()
        if values.version and not re.match(r"^\d+(\.\d+){0,2}$", values.version):
            result.is_valid = False
            result.field_errors["version"] = "Version format is invalid. Expected x.y.z format"
        return result

    @staticmethod
    def _validate_aging(values: FieldValues) -> ValidationResult:
        """验证加速老化值范围 (0-10)。"""
        result = ValidationResult()
        if values.accelerated_aging < 0 or values.accelerated_aging > 10:
            result.is_valid = False
            result.field_errors["accelerated_aging"] = (
                "Accelerated aging value should be between 0 and 10"
            )
        return result

    @staticmethod
    def _validate_required_text(value: str, field_name: str, label: str) -> ValidationResult:
        """单个必填字段验证。"""
        result = ValidationResult()
        if not value:
            result.is_valid = False
            result.field_errors[field_name] = f"{label} cannot be empty"
        return result
