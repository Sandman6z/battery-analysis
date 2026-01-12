# -*- coding: utf-8 -*-
"""
Battery实体定义

Domain层的实体，代表电池本身
"""

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


@dataclass
class Battery:
    """电池实体类"""
    
    # 电池基本信息
    serial_number: str  # 电池序列号
    model_number: str  # 电池型号
    manufacturer: str  # 制造商
    production_date: datetime  # 生产日期
    battery_type: str  # 电池类型 (如: Li-ion, Ni-MH, Lead Acid)
    
    # 电池规格参数
    nominal_voltage: float  # 标称电压 (V)
    nominal_capacity: float  # 标称容量 (Ah)
    max_voltage: float  # 最大电压 (V)
    min_voltage: float  # 最小电压 (V)
    max_current: float  # 最大电流 (A)
    
    # 电池物理属性
    weight: float  # 重量 (kg)
    dimensions: Optional[str] = None  # 尺寸 (如: "100x50x20mm")
    
    # 电池状态
    warranty_period: Optional[int] = None  # 保修期 (月)
    status: str = "active"  # 电池状态: active, retired, defective
    
    def __post_init__(self):
        """初始化后验证"""
        if self.nominal_voltage <= 0:
            raise ValueError("标称电压必须大于0")
        if self.nominal_capacity <= 0:
            raise ValueError("标称容量必须大于0")
        if self.max_voltage <= self.min_voltage:
            raise ValueError("最大电压必须大于最小电压")
        if self.max_current <= 0:
            raise ValueError("最大电流必须大于0")
        if self.weight <= 0:
            raise ValueError("重量必须大于0")
        if self.status not in ["active", "retired", "defective"]:
            raise ValueError("无效的电池状态")
        if self.battery_type not in ["Li-ion", "Ni-MH", "Ni-Cd", "Lead Acid", "Other"]:
            raise ValueError("无效的电池类型")
