# -*- coding: utf-8 -*-
"""
纯输入验证器 — 无 UI 依赖，返回结构化验证结果。

将原先分散在 ValidationManager、ValidationService、analysis_runner 的
验证逻辑集中在此。UI 层通过 ValidationResult 判断并展示样式。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import re


@dataclass
class ValidationResult:
    """验证结果。"""
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    field_errors: Dict[str, str] = field(default_factory=dict)  # 字段名 -> 错误消息

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
        ("battery_type", "电池类型"),
        ("specification_type", "规格类型"),
        ("specification_method", "规格方法"),
        ("manufacturer", "制造商"),
        ("batch_date_code", "批次/日期代码"),
        ("samples_qty", "样品数量"),
        ("temperature", "温度"),
        ("datasheet_nominal_capacity", "标称容量（规格书）"),
        ("calculation_nominal_capacity", "标称容量（计算）"),
        ("required_usable_capacity", "所需可用容量"),
        ("tester_location", "测试地点"),
        ("tested_by", "测试人"),
        ("test_profile", "测试配置文件"),
        ("input_path", "输入路径"),
        ("output_path", "输出路径"),
        ("version", "版本号"),
    ]

    @staticmethod
    def validate_all(values: FieldValues) -> ValidationResult:
        """执行全部验证规则。"""
        result = ValidationResult()
        result.merge(InputValidator._validate_required_fields(values))
        result.merge(InputValidator._validate_paths(values))
        result.merge(InputValidator._validate_version(values))
        result.merge(InputValidator._validate_aging(values))
        if values.battery_type == "Pouch Cell":
            result.merge(InputValidator._validate_required_text(
                values.construction_method, "construction_method", "构造方法"
            ))
        return result

    @staticmethod
    def validate_before_run(values: FieldValues) -> ValidationResult:
        """运行前的快速检查（仅必填项 + 路径）。"""
        return InputValidator.validate_all(values)

    @staticmethod
    def _validate_required_fields(values: FieldValues) -> ValidationResult:
        """检查所有必填字段是否非空。"""
        result = ValidationResult()
        for field_name, label in [
            ("battery_type", "电池类型"),
            ("specification_type", "规格类型"),
            ("specification_method", "规格方法"),
            ("manufacturer", "制造商"),
            ("batch_date_code", "批次/日期代码"),
            ("samples_qty", "样品数量"),
            ("temperature", "温度"),
            ("datasheet_nominal_capacity", "标称容量"),
            ("calculation_nominal_capacity", "计算容量"),
            ("required_usable_capacity", "所需可用容量"),
            ("tester_location", "测试地点"),
            ("tested_by", "测试人"),
            ("test_profile", "测试配置文件"),
            ("input_path", "输入路径"),
            ("output_path", "输出路径"),
        ]:
            val = getattr(values, field_name, "")
            if not val:
                result.is_valid = False
                result.field_errors[field_name] = f"{label} 不能为空"
        return result

    @staticmethod
    def _validate_paths(values: FieldValues) -> ValidationResult:
        """验证输入/输出路径。"""
        import os
        result = ValidationResult()
        if values.input_path and not os.path.exists(values.input_path):
            result.is_valid = False
            result.field_errors["input_path"] = "输入路径不存在"
            result.errors.append(f"输入路径不存在: {values.input_path}")
        if values.output_path and not os.path.exists(values.output_path):
            result.is_valid = False
            result.field_errors["output_path"] = "输出路径不存在"
            result.errors.append(f"输出路径不存在: {values.output_path}")
        return result

    @staticmethod
    def _validate_version(values: FieldValues) -> ValidationResult:
        """验证版本号格式 (x.y.z)。"""
        result = ValidationResult()
        if values.version and not re.match(r"^\d+(\.\d+){0,2}$", values.version):
            result.is_valid = False
            result.field_errors["version"] = "版本号格式不正确，应为 x.y.z 格式"
        return result

    @staticmethod
    def _validate_aging(values: FieldValues) -> ValidationResult:
        """验证加速老化值范围 (0-10)。"""
        result = ValidationResult()
        if values.accelerated_aging < 0 or values.accelerated_aging > 10:
            result.is_valid = False
            result.field_errors["accelerated_aging"] = "加速老化值应在 0-10 之间"
        return result

    @staticmethod
    def _validate_required_text(value: str, field_name: str, label: str) -> ValidationResult:
        """单个必填字段验证。"""
        result = ValidationResult()
        if not value:
            result.is_valid = False
            result.field_errors[field_name] = f"{label} 不能为空"
        return result
