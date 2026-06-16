# -*- coding: utf-8 -*-
"""
TestInfo 数据类

替换原先通过 19 位位置列表 (listTestInfo) 传递测试信息的方式，
提供具名字段访问，同时保留 to_list() 后向兼容。
"""

from dataclasses import dataclass, field
from typing import List, Any


@dataclass
class TestInfo:
    """电池分析测试信息（具名数据类）

    字段顺序与原先 listTestInfo 的索引位置一致（0-based）。
    """
    # 0
    battery_type: str = ""
    # 1
    construction_method: str = ""
    # 2
    specification_type: str = ""
    # 3
    specification_method: str = ""
    # 4
    manufacturer: str = ""
    # 5
    batch_date_code: str = ""
    # 6
    samples_qty: str = ""
    # 7
    temperature_value: str = ""
    # 8
    datasheet_nominal_capacity: str = ""
    # 9
    calculation_nominal_capacity: str = ""
    # 10
    accelerated_aging: str = "0"
    # 11
    tester_location: str = ""
    # 12
    tested_by: str = ""
    # 13
    test_profile: str = ""
    # 14
    current_levels: List[Any] = field(default_factory=list)
    # 15
    voltage_levels: List[Any] = field(default_factory=list)
    # 16
    version: str = ""
    # 17
    required_usable_capacity: str = ""
    # 18
    reported_by: str = ""

    def to_list(self) -> list:
        """转回位置列表，供 BatteryAnalysis 等旧代码内部使用。"""
        return [
            self.battery_type,
            self.construction_method,
            self.specification_type,
            self.specification_method,
            self.manufacturer,
            self.batch_date_code,
            self.samples_qty,
            self.temperature_value,
            self.datasheet_nominal_capacity,
            self.calculation_nominal_capacity,
            self.accelerated_aging,
            self.tester_location,
            self.tested_by,
            self.test_profile,
            self.current_levels,
            self.voltage_levels,
            self.version,
            self.required_usable_capacity,
            self.reported_by,
        ]

    @classmethod
    def from_list(cls, items: list) -> "TestInfo":
        """从位置列表构造 TestInfo（后向兼容）。"""
        if not isinstance(items, (list, tuple)):
            raise TypeError(f"Expected list/tuple, got {type(items).__name__}")
        # 补足缺省值（旧代码可能传少于 19 个元素）
        padded = list(items) + [""] * max(0, 19 - len(items))
        return cls(
            battery_type=padded[0],
            construction_method=padded[1],
            specification_type=padded[2],
            specification_method=padded[3],
            manufacturer=padded[4],
            batch_date_code=padded[5],
            samples_qty=padded[6],
            temperature_value=padded[7],
            datasheet_nominal_capacity=padded[8],
            calculation_nominal_capacity=padded[9],
            accelerated_aging=str(padded[10]) if padded[10] is not None else "0",
            tester_location=padded[11],
            tested_by=padded[12],
            test_profile=padded[13],
            current_levels=padded[14] if isinstance(padded[14], (list, tuple)) else [],
            voltage_levels=padded[15] if isinstance(padded[15], (list, tuple)) else [],
            version=padded[16],
            required_usable_capacity=padded[17],
            reported_by=padded[18],
        )
