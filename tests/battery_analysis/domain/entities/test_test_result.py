# -*- coding: utf-8 -*-
"""
TestResult实体测试
"""

import pytest
from datetime import datetime
from battery_analysis.domain.entities.test_result import TestResult


def test_test_result_initialization():
    """测试测试结果实体初始化"""
    # 正常初始化
    test_result = TestResult(
        test_id="TR-001",
        test_date=datetime.now(),
        battery_serial_number="BAT-001",
        test_equipment="Test Equipment A",
        test_operator="Operator 1",
        temperature=25.0,
        humidity=50.0,
        voltage=3.7,
        current=0.5,
        capacity=2.0,
        internal_resistance=50.0,
        cycle_count=100,
        max_temperature=30.0,
        min_temperature=20.0
    )
    
    assert test_result.test_id == "TR-001"
    assert test_result.battery_serial_number == "BAT-001"
    assert test_result.test_equipment == "Test Equipment A"
    assert test_result.test_operator == "Operator 1"
    assert test_result.temperature == 25.0
    assert test_result.humidity == 50.0
    assert test_result.voltage == 3.7
    assert test_result.current == 0.5
    assert test_result.capacity == 2.0
    assert test_result.internal_resistance == 50.0
    assert test_result.cycle_count == 100
    assert test_result.max_temperature == 30.0
    assert test_result.min_temperature == 20.0
    assert test_result.is_passed is True
    assert test_result.test_status == "completed"


def test_test_result_initialization_with_optional_fields():
    """测试测试结果实体初始化（包含可选字段）"""
    raw_data = [
        {"time": 0, "voltage": 3.7, "current": 0.5, "temperature": 25.0},
        {"time": 1, "voltage": 3.6, "current": 0.5, "temperature": 25.5}
    ]
    
    test_result = TestResult(
        test_id="TR-002",
        test_date=datetime.now(),
        battery_serial_number="BAT-002",
        test_equipment="Test Equipment B",
        test_operator="Operator 2",
        temperature=30.0,
        humidity=45.0,
        voltage=3.7,
        current=1.0,
        capacity=1.9,
        internal_resistance=55.0,
        cycle_count=50,
        max_temperature=35.0,
        min_temperature=28.0,
        raw_data=raw_data,
        is_passed=False,
        test_status="completed"
    )
    
    assert test_result.raw_data == raw_data
    assert test_result.is_passed is False


def test_test_result_initialization_invalid_temperature():
    """测试测试结果实体初始化（无效的温度）"""
    with pytest.raises(ValueError, match="测试温度必须在-50°C到150°C之间"):
        TestResult(
            test_id="TR-003",
            test_date=datetime.now(),
            battery_serial_number="BAT-003",
            test_equipment="Test Equipment C",
            test_operator="Operator 3",
            temperature=200.0,  # 无效温度
            humidity=50.0,
            voltage=3.7,
            current=0.5,
            capacity=2.0,
            internal_resistance=50.0,
            cycle_count=100,
            max_temperature=30.0,
            min_temperature=20.0
        )


def test_test_result_initialization_invalid_humidity():
    """测试测试结果实体初始化（无效的湿度）"""
    with pytest.raises(ValueError, match="测试湿度必须在0%到100%之间"):
        TestResult(
            test_id="TR-004",
            test_date=datetime.now(),
            battery_serial_number="BAT-004",
            test_equipment="Test Equipment D",
            test_operator="Operator 4",
            temperature=25.0,
            humidity=150.0,  # 无效湿度
            voltage=3.7,
            current=0.5,
            capacity=2.0,
            internal_resistance=50.0,
            cycle_count=100,
            max_temperature=30.0,
            min_temperature=20.0
        )


def test_test_result_initialization_invalid_capacity():
    """测试测试结果实体初始化（无效的容量）"""
    with pytest.raises(ValueError, match="测试容量必须大于0"):
        TestResult(
            test_id="TR-005",
            test_date=datetime.now(),
            battery_serial_number="BAT-005",
            test_equipment="Test Equipment E",
            test_operator="Operator 5",
            temperature=25.0,
            humidity=50.0,
            voltage=3.7,
            current=0.5,
            capacity=0,  # 无效容量
            internal_resistance=50.0,
            cycle_count=100,
            max_temperature=30.0,
            min_temperature=20.0
        )


def test_test_result_initialization_invalid_internal_resistance():
    """测试测试结果实体初始化（无效的内阻）"""
    with pytest.raises(ValueError, match="内阻不能为负数"):
        TestResult(
            test_id="TR-006",
            test_date=datetime.now(),
            battery_serial_number="BAT-006",
            test_equipment="Test Equipment F",
            test_operator="Operator 6",
            temperature=25.0,
            humidity=50.0,
            voltage=3.7,
            current=0.5,
            capacity=2.0,
            internal_resistance=-10.0,  # 无效内阻
            cycle_count=100,
            max_temperature=30.0,
            min_temperature=20.0
        )


def test_test_result_initialization_invalid_cycle_count():
    """测试测试结果实体初始化（无效的循环次数）"""
    with pytest.raises(ValueError, match="循环次数不能为负数"):
        TestResult(
            test_id="TR-007",
            test_date=datetime.now(),
            battery_serial_number="BAT-007",
            test_equipment="Test Equipment G",
            test_operator="Operator 7",
            temperature=25.0,
            humidity=50.0,
            voltage=3.7,
            current=0.5,
            capacity=2.0,
            internal_resistance=50.0,
            cycle_count=-10,  # 无效循环次数
            max_temperature=30.0,
            min_temperature=20.0
        )


def test_test_result_initialization_invalid_test_status():
    """测试测试结果实体初始化（无效的测试状态）"""
    with pytest.raises(ValueError, match="无效的测试状态"):
        TestResult(
            test_id="TR-008",
            test_date=datetime.now(),
            battery_serial_number="BAT-008",
            test_equipment="Test Equipment H",
            test_operator="Operator 8",
            temperature=25.0,
            humidity=50.0,
            voltage=3.7,
            current=0.5,
            capacity=2.0,
            internal_resistance=50.0,
            cycle_count=100,
            max_temperature=30.0,
            min_temperature=20.0,
            test_status="invalid"  # 无效测试状态
        )
