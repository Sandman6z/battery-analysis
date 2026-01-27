# -*- coding: utf-8 -*-
"""
TestProfile实体测试
"""

import pytest
from battery_analysis.domain.entities.test_profile import TestProfile


def test_test_profile_initialization():
    """测试测试配置文件实体初始化"""
    # 正常初始化
    test_profile = TestProfile(
        profile_id="TP-001",
        name="标准测试配置",
        test_voltage=3.7,
        test_current=0.5,
        max_cycles=100,
        test_temperature=25.0,
        min_temperature=0.0,
        max_temperature=45.0,
        charge_voltage=4.2,
        charge_current=1.0,
        discharge_voltage=3.0,
        discharge_current=0.5,
        cut_off_voltage=2.5,
        cut_off_current=0.05,
        sampling_interval=1.0
    )
    
    assert test_profile.profile_id == "TP-001"
    assert test_profile.name == "标准测试配置"
    assert test_profile.test_voltage == 3.7
    assert test_profile.test_current == 0.5
    assert test_profile.max_cycles == 100
    assert test_profile.test_temperature == 25.0
    assert test_profile.min_temperature == 0.0
    assert test_profile.max_temperature == 45.0
    assert test_profile.charge_voltage == 4.2
    assert test_profile.charge_current == 1.0
    assert test_profile.discharge_voltage == 3.0
    assert test_profile.discharge_current == 0.5
    assert test_profile.cut_off_voltage == 2.5
    assert test_profile.cut_off_current == 0.05
    assert test_profile.sampling_interval == 1.0
    assert test_profile.version == "1.0"


def test_test_profile_initialization_with_optional_fields():
    """测试测试配置文件实体初始化（包含可选字段）"""
    test_profile = TestProfile(
        profile_id="TP-002",
        name="高温测试配置",
        test_voltage=3.7,
        test_current=0.5,
        max_cycles=50,
        test_temperature=45.0,
        min_temperature=30.0,
        max_temperature=60.0,
        charge_voltage=4.2,
        charge_current=1.0,
        discharge_voltage=3.0,
        discharge_current=0.5,
        cut_off_voltage=2.5,
        cut_off_current=0.05,
        sampling_interval=0.5,
        description="高温环境下的电池测试配置",
        manufacturer="测试设备公司",
        battery_type="Li-ion",
        version="1.1",
        test_duration=24,
        pass_thresholds={"capacity": 80.0, "internal_resistance": 50.0},
        fail_thresholds={"capacity": 60.0, "internal_resistance": 100.0},
        rules=["温度超过60°C时停止测试", "电压低于2.0V时停止测试"]
    )
    
    assert test_profile.description == "高温环境下的电池测试配置"
    assert test_profile.manufacturer == "测试设备公司"
    assert test_profile.battery_type == "Li-ion"
    assert test_profile.version == "1.1"
    assert test_profile.test_duration == 24
    assert test_profile.pass_thresholds == {"capacity": 80.0, "internal_resistance": 50.0}
    assert test_profile.fail_thresholds == {"capacity": 60.0, "internal_resistance": 100.0}
    assert test_profile.rules == ["温度超过60°C时停止测试", "电压低于2.0V时停止测试"]


def test_test_profile_initialization_invalid_test_voltage():
    """测试测试配置文件实体初始化（无效的测试电压）"""
    with pytest.raises(ValueError, match="测试电压必须大于0"):
        TestProfile(
            profile_id="TP-003",
            name="测试配置",
            test_voltage=-1.0,
            test_current=0.5,
            max_cycles=100,
            test_temperature=25.0,
            min_temperature=0.0,
            max_temperature=45.0,
            charge_voltage=4.2,
            charge_current=1.0,
            discharge_voltage=3.0,
            discharge_current=0.5,
            cut_off_voltage=2.5,
            cut_off_current=0.05,
            sampling_interval=1.0
        )


def test_test_profile_initialization_invalid_test_current():
    """测试测试配置文件实体初始化（无效的测试电流）"""
    with pytest.raises(ValueError, match="测试电流必须大于0"):
        TestProfile(
            profile_id="TP-004",
            name="测试配置",
            test_voltage=3.7,
            test_current=-0.1,
            max_cycles=100,
            test_temperature=25.0,
            min_temperature=0.0,
            max_temperature=45.0,
            charge_voltage=4.2,
            charge_current=1.0,
            discharge_voltage=3.0,
            discharge_current=0.5,
            cut_off_voltage=2.5,
            cut_off_current=0.05,
            sampling_interval=1.0
        )


def test_test_profile_initialization_invalid_max_cycles():
    """测试测试配置文件实体初始化（无效的最大循环次数）"""
    with pytest.raises(ValueError, match="最大循环次数必须大于0"):
        TestProfile(
            profile_id="TP-005",
            name="测试配置",
            test_voltage=3.7,
            test_current=0.5,
            max_cycles=0,
            test_temperature=25.0,
            min_temperature=0.0,
            max_temperature=45.0,
            charge_voltage=4.2,
            charge_current=1.0,
            discharge_voltage=3.0,
            discharge_current=0.5,
            cut_off_voltage=2.5,
            cut_off_current=0.05,
            sampling_interval=1.0
        )


def test_test_profile_initialization_invalid_temperature_range():
    """测试测试配置文件实体初始化（无效的温度范围）"""
    with pytest.raises(ValueError, match="最低温度不能大于最高温度"):
        TestProfile(
            profile_id="TP-006",
            name="测试配置",
            test_voltage=3.7,
            test_current=0.5,
            max_cycles=100,
            test_temperature=25.0,
            min_temperature=50.0,
            max_temperature=0.0,
            charge_voltage=4.2,
            charge_current=1.0,
            discharge_voltage=3.0,
            discharge_current=0.5,
            cut_off_voltage=2.5,
            cut_off_current=0.05,
            sampling_interval=1.0
        )


def test_test_profile_initialization_invalid_charge_voltage():
    """测试测试配置文件实体初始化（无效的充电电压）"""
    with pytest.raises(ValueError, match="充电电压必须大于0"):
        TestProfile(
            profile_id="TP-007",
            name="测试配置",
            test_voltage=3.7,
            test_current=0.5,
            max_cycles=100,
            test_temperature=25.0,
            min_temperature=0.0,
            max_temperature=45.0,
            charge_voltage=-0.5,
            charge_current=1.0,
            discharge_voltage=3.0,
            discharge_current=0.5,
            cut_off_voltage=2.5,
            cut_off_current=0.05,
            sampling_interval=1.0
        )


def test_test_profile_initialization_invalid_discharge_voltage():
    """测试测试配置文件实体初始化（无效的放电电压）"""
    with pytest.raises(ValueError, match="放电电压必须大于0"):
        TestProfile(
            profile_id="TP-008",
            name="测试配置",
            test_voltage=3.7,
            test_current=0.5,
            max_cycles=100,
            test_temperature=25.0,
            min_temperature=0.0,
            max_temperature=45.0,
            charge_voltage=4.2,
            charge_current=1.0,
            discharge_voltage=-1.0,
            discharge_current=0.5,
            cut_off_voltage=2.5,
            cut_off_current=0.05,
            sampling_interval=1.0
        )


def test_test_profile_initialization_invalid_cut_off_voltage():
    """测试测试配置文件实体初始化（无效的截止电压）"""
    with pytest.raises(ValueError, match="截止电压必须大于0"):
        TestProfile(
            profile_id="TP-009",
            name="测试配置",
            test_voltage=3.7,
            test_current=0.5,
            max_cycles=100,
            test_temperature=25.0,
            min_temperature=0.0,
            max_temperature=45.0,
            charge_voltage=4.2,
            charge_current=1.0,
            discharge_voltage=3.0,
            discharge_current=0.5,
            cut_off_voltage=-0.5,
            cut_off_current=0.05,
            sampling_interval=1.0
        )


def test_test_profile_initialization_invalid_sampling_interval():
    """测试测试配置文件实体初始化（无效的采样间隔）"""
    with pytest.raises(ValueError, match="采样间隔必须大于0"):
        TestProfile(
            profile_id="TP-010",
            name="测试配置",
            test_voltage=3.7,
            test_current=0.5,
            max_cycles=100,
            test_temperature=25.0,
            min_temperature=0.0,
            max_temperature=45.0,
            charge_voltage=4.2,
            charge_current=1.0,
            discharge_voltage=3.0,
            discharge_current=0.5,
            cut_off_voltage=2.5,
            cut_off_current=0.05,
            sampling_interval=0
        )
