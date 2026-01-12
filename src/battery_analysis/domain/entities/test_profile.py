# -*- coding: utf-8 -*-
"""
TestProfile实体定义

Domain层的实体，代表电池测试配置文件
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class TestProfile:
    """电池测试配置文件实体类"""
    
    # 配置文件基本信息
    profile_id: str  # 配置文件ID
    name: str  # 配置文件名称
    
    # 测试参数
    test_voltage: float  # 测试电压 (V)
    test_current: float  # 测试电流 (A)
    max_cycles: int  # 最大循环次数
    test_temperature: float  # 测试温度 (°C)
    min_temperature: float  # 最低温度 (°C)
    max_temperature: float  # 最高温度 (°C)
    
    # 循环参数
    charge_voltage: float  # 充电电压 (V)
    charge_current: float  # 充电电流 (A)
    discharge_voltage: float  # 放电电压 (V)
    discharge_current: float  # 放电电流 (A)
    
    # 截止条件
    cut_off_voltage: float  # 截止电压 (V)
    cut_off_current: float  # 截止电流 (A)
    
    # 其他必需参数
    sampling_interval: float  # 采样间隔 (秒)
    
    # 可选参数
    description: Optional[str] = None  # 配置文件描述
    manufacturer: Optional[str] = None  # 制造商
    battery_type: Optional[str] = None  # 电池类型
    version: str = "1.0"  # 配置文件版本
    test_duration: Optional[int] = None  # 测试持续时间 (小时)
    
    # 规则和阈值
    pass_thresholds: Optional[Dict[str, float]] = None  # 通过阈值
    fail_thresholds: Optional[Dict[str, float]] = None  # 失败阈值
    rules: Optional[List[str]] = None  # 测试规则
    
    def __post_init__(self):
        """初始化后验证"""
        if self.test_voltage < 0:
            raise ValueError("测试电压必须大于0")
        if self.test_current < 0:
            raise ValueError("测试电流必须大于0")
        if self.max_cycles <= 0:
            raise ValueError("最大循环次数必须大于0")
        if self.min_temperature > self.max_temperature:
            raise ValueError("最低温度不能大于最高温度")
        if self.charge_voltage < 0:
            raise ValueError("充电电压必须大于0")
        if self.discharge_voltage < 0:
            raise ValueError("放电电压必须大于0")
        if self.cut_off_voltage < 0:
            raise ValueError("截止电压必须大于0")
        if self.sampling_interval <= 0:
            raise ValueError("采样间隔必须大于0")
