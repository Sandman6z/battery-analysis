"""输入验证器 (input_validator) 测试

测试 input_validator.py 中 InputValidator 和 ValidationResult，
覆盖必填字段、路径验证、版本号格式、老化值范围和合并逻辑。
"""

import pytest

from battery_analysis.utils.input_validator import (
    FieldValues,
    InputValidator,
    ValidationResult,
)


def _make_valid_values(**overrides) -> FieldValues:
    """构造一个所有必填字段都已填写的 FieldValues。"""
    defaults = dict(
        battery_type="Coin Cell",
        construction_method="Welding",
        specification_type="TypeA",
        specification_method="MethodA",
        manufacturer="Sony",
        batch_date_code="2501",
        samples_qty="5",
        temperature="25",
        datasheet_nominal_capacity="100",
        calculation_nominal_capacity="100",
        accelerated_aging=0,
        tester_location="Lab1",
        tested_by="User1",
        reported_by="User2",
        test_profile="Profile1",
        input_path="C:\\",
        output_path="C:\\",
        version="1.0.0",
        required_usable_capacity="90",
    )
    defaults.update(overrides)
    return FieldValues(**defaults)


class TestValidationResult:
    """ValidationResult 合并逻辑测试。"""

    def test_merge_both_valid(self):
        """两个有效结果合并后仍有效。"""
        r1 = ValidationResult()
        r2 = ValidationResult()
        r1.merge(r2)
        assert r1.is_valid is True
        assert r1.errors == []

    def test_merge_one_invalid(self):
        """一个无效结果合并后整体无效。"""
        r1 = ValidationResult()
        r2 = ValidationResult(is_valid=False, errors=["err"])
        r1.merge(r2)
        assert r1.is_valid is False
        assert "err" in r1.errors

    def test_merge_accumulates_errors(self):
        """合并应累积错误和警告。"""
        r1 = ValidationResult(errors=["e1"], warnings=["w1"])
        r2 = ValidationResult(errors=["e2"], warnings=["w2"])
        r1.merge(r2)
        assert r1.errors == ["e1", "e2"]
        assert r1.warnings == ["w1", "w2"]

    def test_merge_field_errors(self):
        """合并应合并 field_errors 字典。"""
        r1 = ValidationResult(field_errors={"a": "err_a"})
        r2 = ValidationResult(field_errors={"b": "err_b"})
        r1.merge(r2)
        assert r1.field_errors == {"a": "err_a", "b": "err_b"}


class TestValidateAllHappyPath:
    """validate_all 正常路径测试。"""

    def test_all_fields_valid(self):
        """所有字段有效时应返回 is_valid=True。"""
        result = InputValidator.validate_all(_make_valid_values())
        assert result.is_valid is True
        assert result.errors == []
        assert result.field_errors == {}

    def test_validate_before_run_delegates(self):
        """validate_before_run 应与 validate_all 行为一致。"""
        values = _make_valid_values()
        result = InputValidator.validate_before_run(values)
        assert result.is_valid is True


class TestValidateRequiredFields:
    """必填字段验证测试。"""

    def test_empty_battery_type(self):
        """空 battery_type 应触发错误。"""
        values = _make_valid_values(battery_type="")
        result = InputValidator.validate_all(values)
        assert result.is_valid is False
        assert "battery_type" in result.field_errors

    def test_empty_manufacturer(self):
        """空 manufacturer 应触发错误。"""
        values = _make_valid_values(manufacturer="")
        result = InputValidator.validate_all(values)
        assert result.is_valid is False
        assert "manufacturer" in result.field_errors

    def test_empty_input_path(self):
        """空 input_path 应触发必填错误。"""
        values = _make_valid_values(input_path="")
        result = InputValidator.validate_all(values)
        assert result.is_valid is False
        assert "input_path" in result.field_errors

    def test_multiple_empty_fields(self):
        """多个空字段应产生多个 field_errors。"""
        values = _make_valid_values(battery_type="", manufacturer="")
        result = InputValidator.validate_all(values)
        assert result.is_valid is False
        assert "battery_type" in result.field_errors
        assert "manufacturer" in result.field_errors


class TestValidatePaths:
    """路径验证测试。"""

    def test_nonexistent_input_path(self):
        """不存在的 input_path 应触发错误。"""
        values = _make_valid_values(input_path="C:\\nonexistent_path_xyz_12345")
        result = InputValidator.validate_all(values)
        assert result.is_valid is False
        assert "input_path" in result.field_errors

    def test_nonexistent_output_path(self):
        """不存在的 output_path 应触发错误。"""
        values = _make_valid_values(output_path="C:\\nonexistent_path_xyz_12345")
        result = InputValidator.validate_all(values)
        assert result.is_valid is False
        assert "output_path" in result.field_errors

    def test_valid_paths(self, tmp_path):
        """存在的路径不应触发路径错误。"""
        values = _make_valid_values(
            input_path=str(tmp_path), output_path=str(tmp_path)
        )
        result = InputValidator.validate_all(values)
        assert result.is_valid is True


class TestValidateVersion:
    """版本号格式验证测试。"""

    def test_valid_version_formats(self):
        """合法版本号格式应通过。"""
        for ver in ["1", "1.0", "1.0.0", "12.34.56"]:
            values = _make_valid_values(version=ver)
            result = InputValidator._validate_version(values)
            assert result.is_valid is True, f"Version '{ver}' should be valid"

    def test_invalid_version_format(self):
        """非法版本号格式应触发错误。"""
        values = _make_valid_values(version="abc")
        result = InputValidator._validate_version(values)
        assert result.is_valid is False
        assert "version" in result.field_errors

    def test_empty_version_is_valid(self):
        """空版本号不应触发格式错误（必填检查另行处理）。"""
        values = _make_valid_values(version="")
        result = InputValidator._validate_version(values)
        assert result.is_valid is True


class TestValidateAging:
    """加速老化值验证测试。"""

    def test_valid_aging_range(self):
        """0-10 范围内的老化值应通过。"""
        for val in [0, 5, 10]:
            values = _make_valid_values(accelerated_aging=val)
            result = InputValidator._validate_aging(values)
            assert result.is_valid is True, f"Aging {val} should be valid"

    def test_negative_aging(self):
        """负数老化值应触发错误。"""
        values = _make_valid_values(accelerated_aging=-1)
        result = InputValidator._validate_aging(values)
        assert result.is_valid is False

    def test_aging_over_limit(self):
        """超过 10 的老化值应触发错误。"""
        values = _make_valid_values(accelerated_aging=11)
        result = InputValidator._validate_aging(values)
        assert result.is_valid is False
        assert "accelerated_aging" in result.field_errors


class TestConstructionMethodValidation:
    """构造方法验证测试（特定电池类型需要）。"""

    def test_pouch_cell_requires_construction_method(self):
        """Pouch Cell 类型需要填写 construction_method。"""
        values = _make_valid_values(
            battery_type="Pouch Cell", construction_method=""
        )
        result = InputValidator.validate_all(values)
        assert result.is_valid is False
        assert "construction_method" in result.field_errors

    def test_custom_types_requiring_construction(self):
        """可通过参数自定义需要构造方法的类型列表。"""
        values = _make_valid_values(
            battery_type="CustomType", construction_method=""
        )
        result = InputValidator.validate_all(
            values, types_requiring_construction=["CustomType"]
        )
        assert result.is_valid is False
        assert "construction_method" in result.field_errors

    def test_non_pouch_no_construction_required(self):
        """非 Pouch Cell 类型不需要 construction_method。"""
        values = _make_valid_values(
            battery_type="Coin Cell", construction_method=""
        )
        result = InputValidator.validate_all(values)
        assert result.is_valid is True
