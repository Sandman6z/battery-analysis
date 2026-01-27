# -*- coding: utf-8 -*-
"""
Battery实体测试
"""

import pytest
from datetime import datetime
from battery_analysis.domain.entities.battery import Battery


def test_battery_initialization():
    """测试电池实体初始化"""
    # 正常初始化
    battery = Battery(
        serial_number="BAT-001",
        model_number="Model-A",
        manufacturer="Test Manufacturer",
        production_date=datetime.now(),
        battery_type="Li-ion",
        nominal_voltage=3.7,
        nominal_capacity=2.0,
        max_voltage=4.2,
        min_voltage=3.0,
        max_current=5.0,
        weight=0.15
    )
    
    assert battery.serial_number == "BAT-001"
    assert battery.model_number == "Model-A"
    assert battery.manufacturer == "Test Manufacturer"
    assert battery.battery_type == "Li-ion"
    assert battery.nominal_voltage == 3.7
    assert battery.nominal_capacity == 2.0
    assert battery.max_voltage == 4.2
    assert battery.min_voltage == 3.0
    assert battery.max_current == 5.0
    assert battery.weight == 0.15
    assert battery.status == "active"


def test_battery_initialization_with_optional_fields():
    """测试电池实体初始化（包含可选字段）"""
    battery = Battery(
        serial_number="BAT-002",
        model_number="Model-B",
        manufacturer="Test Manufacturer",
        production_date=datetime.now(),
        battery_type="Li-ion",
        nominal_voltage=3.7,
        nominal_capacity=2.0,
        max_voltage=4.2,
        min_voltage=3.0,
        max_current=5.0,
        weight=0.15,
        dimensions="100x50x20mm",
        warranty_period=24,
        status="active"
    )
    
    assert battery.dimensions == "100x50x20mm"
    assert battery.warranty_period == 24


def test_battery_initialization_invalid_nominal_voltage():
    """测试电池实体初始化（无效的标称电压）"""
    with pytest.raises(ValueError, match="标称电压必须大于0"):
        Battery(
            serial_number="BAT-003",
            model_number="Model-C",
            manufacturer="Test Manufacturer",
            production_date=datetime.now(),
            battery_type="Li-ion",
            nominal_voltage=0,
            nominal_capacity=2.0,
            max_voltage=4.2,
            min_voltage=3.0,
            max_current=5.0,
            weight=0.15
        )


def test_battery_initialization_invalid_nominal_capacity():
    """测试电池实体初始化（无效的标称容量）"""
    with pytest.raises(ValueError, match="标称容量必须大于0"):
        Battery(
            serial_number="BAT-004",
            model_number="Model-D",
            manufacturer="Test Manufacturer",
            production_date=datetime.now(),
            battery_type="Li-ion",
            nominal_voltage=3.7,
            nominal_capacity=-1.0,
            max_voltage=4.2,
            min_voltage=3.0,
            max_current=5.0,
            weight=0.15
        )


def test_battery_initialization_invalid_voltage_range():
    """测试电池实体初始化（无效的电压范围）"""
    with pytest.raises(ValueError, match="最大电压必须大于最小电压"):
        Battery(
            serial_number="BAT-005",
            model_number="Model-E",
            manufacturer="Test Manufacturer",
            production_date=datetime.now(),
            battery_type="Li-ion",
            nominal_voltage=3.7,
            nominal_capacity=2.0,
            max_voltage=3.0,
            min_voltage=4.2,
            max_current=5.0,
            weight=0.15
        )


def test_battery_initialization_invalid_max_current():
    """测试电池实体初始化（无效的最大电流）"""
    with pytest.raises(ValueError, match="最大电流必须大于0"):
        Battery(
            serial_number="BAT-006",
            model_number="Model-F",
            manufacturer="Test Manufacturer",
            production_date=datetime.now(),
            battery_type="Li-ion",
            nominal_voltage=3.7,
            nominal_capacity=2.0,
            max_voltage=4.2,
            min_voltage=3.0,
            max_current=0,
            weight=0.15
        )


def test_battery_initialization_invalid_weight():
    """测试电池实体初始化（无效的重量）"""
    with pytest.raises(ValueError, match="重量必须大于0"):
        Battery(
            serial_number="BAT-007",
            model_number="Model-G",
            manufacturer="Test Manufacturer",
            production_date=datetime.now(),
            battery_type="Li-ion",
            nominal_voltage=3.7,
            nominal_capacity=2.0,
            max_voltage=4.2,
            min_voltage=3.0,
            max_current=5.0,
            weight=-0.1
        )


def test_battery_initialization_invalid_status():
    """测试电池实体初始化（无效的状态）"""
    with pytest.raises(ValueError, match="无效的电池状态"):
        Battery(
            serial_number="BAT-008",
            model_number="Model-H",
            manufacturer="Test Manufacturer",
            production_date=datetime.now(),
            battery_type="Li-ion",
            nominal_voltage=3.7,
            nominal_capacity=2.0,
            max_voltage=4.2,
            min_voltage=3.0,
            max_current=5.0,
            weight=0.15,
            status="invalid"
        )


def test_battery_initialization_invalid_battery_type():
    """测试电池实体初始化（无效的电池类型）"""
    with pytest.raises(ValueError, match="无效的电池类型"):
        Battery(
            serial_number="BAT-009",
            model_number="Model-I",
            manufacturer="Test Manufacturer",
            production_date=datetime.now(),
            battery_type="InvalidType",
            nominal_voltage=3.7,
            nominal_capacity=2.0,
            max_voltage=4.2,
            min_voltage=3.0,
            max_current=5.0,
            weight=0.15
        )
