"""
配置 Schema 定义与验证

为 config.json 提供类型约束和结构验证，启动时校验配置完整性。
"""

from dataclasses import dataclass, field
from typing import Any

from battery_analysis.utils.exceptions import ConfigException

# ── Schema 定义 ────────────────────────────────────────────────


# ── camelCase → snake_case 映射 ───────────────────────────────

_CAMEL_TO_SNAKE = {
    "constructionMethods": "construction_methods",
    "specificationMethods": "specification_methods",
    "pulseCurrents": "pulse_currents",
    "cutOffVoltages": "cut_off_voltages",
    "testedBy": "tested_by",
}


def _to_snake(d: dict) -> dict:
    """将 dict 中的 camelCase 键转换为 snake_case。"""
    result = {}
    for k, v in d.items():
        result[_CAMEL_TO_SNAKE.get(k, k)] = v
    return result


@dataclass
class BatterySchema:
    types: list[str] = field(default_factory=lambda: ["Coin Cell", "Pouch Cell"])
    construction_methods: list[str] = field(
        default_factory=lambda: ["Spiral Type", "Laminate Type"]
    )
    specifications: dict[str, list[str]] = field(default_factory=dict)
    specification_methods: list[str] = field(default_factory=lambda: ["1S1P", "1S2P", "2S1P"])
    manufacturers: list[str] = field(default_factory=list)
    rules: list[str] = field(default_factory=list)
    pulse_currents: list[float] = field(default_factory=list)
    cut_off_voltages: list[float] = field(default_factory=list)


@dataclass
class TestSchema:
    locations: list[str] = field(default_factory=list)
    tested_by: list[str] = field(default_factory=list)
    equipment: dict[str, Any] = field(default_factory=dict)


@dataclass
class AppConfigSchema:
    """完整配置的结构定义。"""

    version: int = 1
    battery: BatterySchema = field(default_factory=BatterySchema)
    test: TestSchema = field(default_factory=TestSchema)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AppConfigSchema":
        """从原始 dict 解析并验证（自动处理 camelCase → snake_case）。"""
        errors: list[str] = []

        version = data.get("version", 1)
        if not isinstance(version, int):
            errors.append("version must be an integer")

        battery_data = _to_snake(data.get("battery", {}))
        test_data = _to_snake(data.get("test", {}))

        # 验证必需字段
        if "types" not in battery_data:
            errors.append("battery.types is missing")
        if "locations" not in test_data:
            errors.append("test.locations is missing")

        if errors:
            raise ConfigException("Configuration validation failed: " + "; ".join(errors))

        return cls(
            version=version,
            battery=BatterySchema(**battery_data),
            test=TestSchema(**test_data),
        )

    def validate(self) -> list[str]:
        """返回所有验证警告（非致命）。"""
        warnings = []
        if not self.battery.types:
            warnings.append("battery.types is empty")
        if not self.battery.pulse_currents:
            warnings.append("battery.pulseCurrents is empty - using default value")
        if not self.battery.cut_off_voltages:
            warnings.append("battery.cutOffVoltages is empty - using default value")
        if not self.test.locations:
            warnings.append("test.locations is empty")
        if not self.test.tested_by:
            warnings.append("test.testedBy is empty")
        return warnings
