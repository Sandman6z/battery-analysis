# -*- coding: utf-8 -*-
"""
TestResult实体定义

Domain层的实体，代表电池测试结果
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime


@dataclass
class TestResult:
    """电池测试结果实体类"""
    
    # 测试基本信息
    test_id: str  # 测试ID
    test_date: datetime  # 测试日期
    battery_serial_number: str  # 电池序列号
    test_equipment: str  # 测试设备
    test_operator: str  # 测试操作员
    
    # 测试条件
    temperature: float  # 测试温度 (°C)
    humidity: float  # 测试湿度 (%)
    voltage: float  # 测试电压 (V)
    current: float  # 测试电流 (A)
    
    # 测试结果数据
    capacity: float  # 测试容量 (Ah)
    internal_resistance: float  # 内阻 (mΩ)
    cycle_count: int  # 循环次数
    max_temperature: float  # 最大温度 (°C)
    min_temperature: float  # 最小温度 (°C)
    
    # 原始测试数据
    raw_data: Optional[List[Dict[str, Any]]] = None  # 原始测试数据列表
    
    # 测试状态
    is_passed: bool = True  # 测试是否通过
    test_status: str = "completed"  # 测试状态
    
    def __post_init__(self):
        """初始化后验证"""
        if self.temperature < -50 or self.temperature > 150:
            raise ValueError("测试温度必须在-50°C到150°C之间")
        if self.humidity < 0 or self.humidity > 100:
            raise ValueError("测试湿度必须在0%到100%之间")
        if self.capacity <= 0:
            raise ValueError("测试容量必须大于0")
        if self.internal_resistance < 0:
            raise ValueError("内阻不能为负数")
        if self.cycle_count < 0:
            raise ValueError("循环次数不能为负数")
        if self.test_status not in ["pending", "in_progress", "completed", "failed"]:
            raise ValueError("无效的测试状态")
